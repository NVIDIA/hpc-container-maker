# Copyright (c) 2018, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# pylint: disable=invalid-name, too-few-public-methods
# pylint: disable=too-many-instance-attributes

"""HDF5 building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import re
import os

import hpccm.config

from hpccm.building_blocks.packages import packages
from hpccm.common import linux_distro
from hpccm.primitives.comment import comment
from hpccm.primitives.copy import copy
from hpccm.primitives.environment import environment
from hpccm.primitives.shell import shell
from hpccm.templates.ConfigureMake import ConfigureMake
from hpccm.templates.rm import rm
from hpccm.templates.tar import tar
from hpccm.templates.wget import wget
from hpccm.toolchain import toolchain

class hdf5(ConfigureMake, rm, tar, wget):
    """The `hdf5` building block downloads, configures, builds, and
    installs the [HDF5](http://www.hdfgroup.org) component.  Depending
    on the parameters, the source will be downloaded from the web
    (default) or copied from a source directory in the local build
    context.

    As a side effect, this building block modifies `PATH`,
    `LD_LIBRARY_PATH` to include the HDF5 build, and sets `HDF5_DIR`.

    # Parameters

    check: Boolean flag to specify whether the `make check` step
    should be performed.  The default is False.

    configure_opts: List of options to pass to `configure`.  The
    default values are `--enable-cxx` and `--enable-fortran`.

    directory: Path to the unpackaged source directory relative to the
    local build context.  The default value is empty.  If this is
    defined, the source in the local build context will be used rather
    than downloading the source from the web.

    ospackages: List of OS packages to install prior to configuring
    and building.  For Ubuntu, the default values are `bzip2`, `file`,
    `make`, `wget`, and `zlib1g-dev`.  For RHEL-based Linux
    distributions the default values are `bzip2`, `file`, `make`,
    `wget` and `zlib-devel`.

    prefix: The top level install location.  The default value is
    `/usr/local/hdf5`.

    toolchain: The toolchain object.  This should be used if
    non-default compilers or other toolchain options are needed.  The
    default is empty.

    version: The version of HDF5 source to download.  This value is
    ignored if `directory` is set.  The default value is `1.10.4`.

    # Examples

    ```python
    hdf5(prefix='/opt/hdf5/1.10.1', version='1.10.1')
    ```

    ```python
    hdf5(directory='sources/hdf5-1.10.1')
    ```

    ```python
    p = pgi(eula=True)
    hdf5(toolchain=p.toolchain)
    ```

    ```python
    hdf5(check=True, configure_opts=['--enable-cxx', '--enable-fortran',
                                     '--enable-profiling=yes'])
    ```
    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        # Trouble getting MRO with kwargs working correctly, so just call
        # the parent class constructors manually for now.
        #super(hdf5, self).__init__(**kwargs)
        ConfigureMake.__init__(self, **kwargs)
        rm.__init__(self, **kwargs)
        tar.__init__(self, **kwargs)
        wget.__init__(self, **kwargs)

        self.configure_opts = kwargs.get('configure_opts',
                                         ['--enable-cxx', '--enable-fortran'])
        self.prefix = kwargs.get('prefix', '/usr/local/hdf5')

        self.__baseurl = kwargs.get('baseurl', 'http://www.hdfgroup.org/ftp/HDF5/releases')
        self.__check = kwargs.get('check', False)
        self.__directory = kwargs.get('directory', '')
        self.__ospackages = kwargs.get('ospackages', [])
        self.__runtime_ospackages = [] # Filled in by __distro()
        self.__toolchain = kwargs.get('toolchain', toolchain())
        self.__version = kwargs.get('version', '1.10.4')

        self.__commands = [] # Filled in by __setup()
        self.__environment_variables = {
            'HDF5_DIR': self.prefix,
            'PATH':
            '{}:$PATH'.format(os.path.join(self.prefix, 'bin')),
            'LD_LIBRARY_PATH':
            '{}:$LD_LIBRARY_PATH'.format(os.path.join(self.prefix, 'lib'))}
        self.__wd = '/var/tmp' # working directory

        # Set the Linux distribution specific parameters
        self.__distro()

        # Construct the series of steps to execute
        self.__setup()

    def __str__(self):
        """String representation of the building block"""

        instructions = []
        if self.__directory:
            instructions.append(comment('HDF5'))
        else:
            instructions.append(comment(
                'HDF5 version {}'.format(self.__version)))

        instructions.append(packages(ospackages=self.__ospackages))

        if self.__directory:
            # Use source from local build context
            instructions.append(
                copy(src=self.__directory,
                     dest=os.path.join(self.__wd, self.__directory)))

        instructions.append(shell(commands=self.__commands))
        instructions.append(environment(
            variables=self.__environment_variables))

        return '\n'.join(str(x) for x in instructions)

    def __distro(self):
        """Based on the Linux distribution, set values accordingly.  A user
        specified value overrides any defaults."""

        if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
            if not self.__ospackages:
                self.__ospackages = ['bzip2', 'file', 'make', 'wget',
                                     'zlib1g-dev']
            self.__runtime_ospackages = ['zlib1g']
        elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
            if not self.__ospackages:
                self.__ospackages = ['bzip2', 'file', 'make', 'wget',
                                     'zlib-devel']
            self.__runtime_ospackages = ['zlib']
        else: # pragma: no cover
            raise RuntimeError('Unknown Linux distribution')

    def __setup(self):
        """Construct the series of shell commands, i.e., fill in
           self.__commands"""

        # The download URL has the format contains vMAJOR.MINOR in the
        # path and the tarball contains MAJOR.MINOR.REVISION, so pull
        # apart the full version to get the MAJOR and MINOR components.
        match = re.match(r'(?P<major>\d+)\.(?P<minor>\d+)', self.__version)
        major_minor = '{0}.{1}'.format(match.groupdict()['major'],
                                       match.groupdict()['minor'])
        tarball = 'hdf5-{}.tar.bz2'.format(self.__version)
        url = '{0}/hdf5-{1}/hdf5-{2}/src/{3}'.format(self.__baseurl,
                                                     major_minor,
                                                     self.__version, tarball)

        if self.__directory:
            # Use source from local build context
            self.__commands.append(self.configure_step(
                directory=os.path.join(self.__wd, self.__directory),
                toolchain=self.__toolchain))
        else:
            # Download source from web
            self.__commands.append(self.download_step(url=url,
                                                      directory=self.__wd))
            self.__commands.append(self.untar_step(
                tarball=os.path.join(self.__wd, tarball), directory=self.__wd))
            self.__commands.append(self.configure_step(
                directory=os.path.join(self.__wd,
                                       'hdf5-{}'.format(self.__version)),
                toolchain=self.__toolchain))

        self.__commands.append(self.build_step())

        # Check the build
        if self.__check:
            self.__commands.append(self.check_step())

        self.__commands.append(self.install_step())

        if self.__directory:
            # Using source from local build context, cleanup directory
            self.__commands.append(self.cleanup_step(
                items=[os.path.join(self.__wd, self.__directory)]))
        else:
            # Using downloaded source, cleanup tarball and directory
            self.__commands.append(self.cleanup_step(
                items=[os.path.join(self.__wd, tarball),
                       os.path.join(self.__wd,
                                    'hdf5-{}'.format(self.__version))]))

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples

        ```python
        h = hdf5(...)
        Stage0 += h
        Stage1 += h.runtime()
        ```
        """
        instructions = []
        instructions.append(comment('HDF5'))
        instructions.append(packages(ospackages=self.__runtime_ospackages))
        instructions.append(copy(_from=_from, src=self.prefix,
                                 dest=self.prefix))
        instructions.append(environment(
            variables=self.__environment_variables))
        return '\n'.join(str(x) for x in instructions)
