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

"""CGNS building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import os
import re
from copy import copy as _copy

import hpccm.config

from hpccm.building_blocks.packages import packages
from hpccm.common import linux_distro
from hpccm.primitives.comment import comment
from hpccm.primitives.copy import copy
from hpccm.primitives.shell import shell
from hpccm.templates.ConfigureMake import ConfigureMake
from hpccm.templates.rm import rm
from hpccm.templates.tar import tar
from hpccm.templates.wget import wget
from hpccm.toolchain import toolchain

class cgns(ConfigureMake, rm, tar, wget):
    """The `cgns` building block downloads and installs the
    [CGNS](https://cgns.github.io/index.html) component.

    The [HDF5](#hdf5) building block should be installed prior to this
    building block.

    # Parameters

    check: Boolean flag to specify whether the test cases should be
    run.  The default is False.

    configure_opts: List of options to pass to `configure`.  The
    default value is `--with-hdf5=/usr/local/hdf5` and `--with-zlib`.

    prefix: The top level install location.  The default value is
    `/usr/local/cgns`.

    ospackages: List of OS packages to install prior to configuring
    and building.  For Ubuntu, the default values are `file`, `make`,
    `wget`, and `zlib1g-dev`.  For RHEL-based Linux distributions the
    default values are `bzip2`, `file`, `make`, `wget` and
    `zlib-devel`.

    toolchain: The toolchain object.  This should be used if
    non-default compilers or other toolchain options are needed.  The
    default is empty.

    version: The version of CGNS source to download.  The default
    value is `3.3.1`.

    # Examples

    ```python
    cgns(prefix='/opt/cgns/3.3.1', version='3.3.1')
    ```
    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        # Trouble getting MRO with kwargs working correctly, so just call
        # the parent class constructors manually for now.
        #super(cgns, self).__init__(**kwargs)
        ConfigureMake.__init__(self, **kwargs)
        tar.__init__(self, **kwargs)
        rm.__init__(self, **kwargs)
        wget.__init__(self, **kwargs)

        self.configure_opts = kwargs.get('configure_opts',
                                         ['--with-hdf5=/usr/local/hdf5',
                                          '--with-zlib'])
        self.prefix = kwargs.get('prefix', '/usr/local/cgns')

        self.__baseurl = kwargs.get('baseurl', 'https://github.com/CGNS/CGNS/archive')
        self.__check = kwargs.get('check', False)
        self.__ospackages = kwargs.get('ospackages', [])
        self.__toolchain = kwargs.get('toolchain', toolchain())
        self.__version = kwargs.get('version', '3.3.1')

        self.__commands = [] # Filled in by __setup()
        self.__wd = '/var/tmp' # working directory

        # Set the Linux distribution specific parameters
        self.__distro()

        # Construct the series of steps to execute
        self.__setup()

    def __str__(self):
        """String representation of the building block"""

        instructions = []
        instructions.append(comment(
            'CGNS version {}'.format(self.__version)))
        instructions.append(packages(ospackages=self.__ospackages))
        instructions.append(shell(commands=self.__commands))

        return '\n'.join(str(x) for x in instructions)

    def __distro(self):
        """Based on the Linux distribution, set values accordingly.  A user
        specified value overrides any defaults."""

        if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
            if not self.__ospackages:
                self.__ospackages = ['file', 'make', 'wget', 'zlib1g-dev']
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

        tarball = 'v{}.tar.gz'.format(self.__version)
        url = '{0}/{1}'.format(self.__baseurl, tarball)

        # Create a copy of the toolchain so that it can be modified
        # without impacting the original.
        toolchain = _copy(self.__toolchain)

        # See https://cgns.github.io/download.html, Known Bugs
        if not toolchain.LIBS:
            toolchain.LIBS = '-Wl,--no-as-needed -ldl'
        if not toolchain.FLIBS:
            toolchain.FLIBS = '-Wl,--no-as-needed -ldl'
        # See https://cgnsorg.atlassian.net/browse/CGNS-40
        if (not toolchain.FFLAGS and toolchain.FC and
            re.match('.*pgf.*', toolchain.FC)):
            toolchain.FFLAGS = '-Mx,125,0x200'

        # Download source from web
        self.__commands.append(self.download_step(url=url,
                                                  directory=self.__wd))
        self.__commands.append(self.untar_step(
            tarball=os.path.join(self.__wd, tarball), directory=self.__wd))
        self.__commands.append(self.configure_step(
            directory=os.path.join(self.__wd, 'CGNS-{}'.format(
                self.__version), 'src'),
            toolchain=toolchain))

        self.__commands.append(self.build_step())

        # Check the build
        if self.__check:
            self.__commands.append(self.check_step())

        self.__commands.append(self.install_step())

        # Cleanup tarball and directory
        self.__commands.append(self.cleanup_step(
            items=[os.path.join(self.__wd, tarball),
                   os.path.join(self.__wd,
                                'v{}'.format(self.__version))]))

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Example

        ```python
        c = cgns(...)
        Stage0 += c
        Stage1 += c.runtime()
        ```
        """
        instructions = []
        instructions.append(comment('CGNS'))
        instructions.append(packages(ospackages=self.__runtime_ospackages))
        instructions.append(copy(_from=_from, src=self.prefix,
                                 dest=self.prefix))
        return '\n'.join(str(x) for x in instructions)
