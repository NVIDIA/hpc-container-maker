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

import posixpath
import re

import hpccm.config
import hpccm.templates.envvars
import hpccm.templates.ldconfig

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.generic_autotools import generic_autotools
from hpccm.building_blocks.packages import packages
from hpccm.common import linux_distro
from hpccm.primitives.comment import comment

class hdf5(bb_base, hpccm.templates.envvars, hpccm.templates.ldconfig):
    """The `hdf5` building block downloads, configures, builds, and
    installs the [HDF5](http://www.hdfgroup.org) component.  Depending
    on the parameters, the source will be downloaded from the web
    (default) or copied from a source directory in the local build
    context.

    # Parameters

    annotate: Boolean flag to specify whether to include annotations
    (labels).  The default is False.

    check: Boolean flag to specify whether the `make check` step
    should be performed.  The default is False.

    configure_opts: List of options to pass to `configure`.  The
    default values are `--enable-cxx` and `--enable-fortran`.

    directory: Path to the unpackaged source directory relative to the
    local build context.  The default value is empty.  If this is
    defined, the source in the local build context will be used rather
    than downloading the source from the web.

    disable_FEATURE: Flags to control disabling features when
    configuring.  For instance, `disable_foo=True` maps to
    `--disable-foo`.  Underscores in the parameter name are converted
    to dashes.

    enable_FEATURE[=ARG]: Flags to control enabling features when
    configuring.  For instance, `enable_foo=True` maps to
    `--enable-foo` and `enable_foo='yes'` maps to `--enable-foo=yes`.
    Underscores in the parameter name are converted to dashes.

    environment: Boolean flag to specify whether the environment
    (`CPATH`, `LD_LIBRARY_PATH`, `LIBRARY_PATH`, `PATH`, and others)
    should be modified to include HDF5. The default is True.

    ldconfig: Boolean flag to specify whether the HDF5 library
    directory should be added dynamic linker cache.  If False, then
    `LD_LIBRARY_PATH` is modified to include the HDF5 library
    directory. The default value is False.

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
    ignored if `directory` is set.  The default value is `1.10.6`.

    with_PACKAGE[=ARG]: Flags to control optional packages when
    configuring.  For instance, `with_foo=True` maps to `--with-foo`
    and `with_foo='/usr/local/foo'` maps to
    `--with-foo=/usr/local/foo`.  Underscores in the parameter name
    are converted to dashes.

    without_PACKAGE: Flags to control optional packages when
    configuring.  For instance `without_foo=True` maps to
    `--without-foo`.  Underscores in the parameter name are converted
    to dashes.

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

        super(hdf5, self).__init__(**kwargs)

        self.__baseurl = kwargs.pop('baseurl', 'http://www.hdfgroup.org/ftp/HDF5/releases')
        self.__check = kwargs.pop('check', False)
        self.__configure_opts = kwargs.pop('configure_opts',
                                           ['--enable-cxx',
                                            '--enable-fortran'])
        self.__ospackages = kwargs.pop('ospackages', [])
        self.__prefix = kwargs.pop('prefix', '/usr/local/hdf5')
        self.__runtime_ospackages = [] # Filled in by __distro()
        self.__version = kwargs.pop('version', '1.10.6')

        # Set the Linux distribution specific parameters
        self.__distro()

        # Set the download specific parameters
        self.__download()

        # Set the environment variables
        self.environment_variables['CPATH'] = '{}:$CPATH'.format(
            posixpath.join(self.__prefix, 'include'))
        self.environment_variables['HDF5_DIR'] = self.__prefix
        self.environment_variables['LIBRARY_PATH'] = '{}:$LIBRARY_PATH'.format(
            posixpath.join(self.__prefix, 'lib'))
        self.environment_variables['PATH'] = '{}:$PATH'.format(
            posixpath.join(self.__prefix, 'bin'))
        if not self.ldconfig:
            self.environment_variables['LD_LIBRARY_PATH'] = '{}:$LD_LIBRARY_PATH'.format(posixpath.join(self.__prefix, 'lib'))

        # Setup build configuration
        self.__bb = generic_autotools(
            annotations={'version': self.__version},
            base_annotation=self.__class__.__name__,
            check=self.__check,
            configure_opts=self.__configure_opts,
            comment=False,
            devel_environment=self.environment_variables,
            prefix=self.__prefix,
            runtime_environment=self.environment_variables,
            url=self.__url,
            **kwargs)

        # Container instructions
        self += comment('HDF5 version {}'.format(self.__version))
        self += packages(ospackages=self.__ospackages)
        self += self.__bb

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
                if self.__check:
                    self.__ospackages.append('diffutils')
            self.__runtime_ospackages = ['zlib']
        else: # pragma: no cover
            raise RuntimeError('Unknown Linux distribution')

    def __download(self):
        """Construct the series of shell commands, i.e., fill in
           self.__commands"""

        # The download URL has the format contains vMAJOR.MINOR in the
        # path and the tarball contains MAJOR.MINOR.REVISION, so pull
        # apart the full version to get the MAJOR and MINOR components.
        match = re.match(r'(?P<major>\d+)\.(?P<minor>\d+)', self.__version)
        major_minor = '{0}.{1}'.format(match.groupdict()['major'],
                                       match.groupdict()['minor'])
        tarball = 'hdf5-{}.tar.bz2'.format(self.__version)
        self.__url = '{0}/hdf5-{1}/hdf5-{2}/src/{3}'.format(
            self.__baseurl, major_minor, self.__version, tarball)

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
        instructions.append(self.__bb.runtime(_from=_from))
        return '\n'.join(str(x) for x in instructions)
