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

"""OpenBLAS building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import posixpath

import hpccm.config
import hpccm.templates.envvars
import hpccm.templates.ldconfig
import hpccm.templates.rm
import hpccm.templates.tar
import hpccm.templates.wget

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.packages import packages
from hpccm.common import cpu_arch
from hpccm.primitives.comment import comment
from hpccm.primitives.copy import copy
from hpccm.primitives.environment import environment
from hpccm.primitives.shell import shell
from hpccm.toolchain import toolchain

class openblas(bb_base, hpccm.templates.envvars, hpccm.templates.ldconfig,
               hpccm.templates.rm, hpccm.templates.tar, hpccm.templates.wget):
    """The `openblas` building block builds and installs the
    [OpenBLAS](https://www.openblas.net) component.

    # Parameters

    environment: Boolean flag to specify whether the environment
    (`LD_LIBRARY_PATH` and `PATH`) should be modified to include
    OpenBLAS. The default is True.

    ldconfig: Boolean flag to specify whether the OpenBLAS library
    directory should be added dynamic linker cache.  If False, then
    `LD_LIBRARY_PATH` is modified to include the OpenBLAS library
    directory. The default value is False.

    make_opts: List of options to pass to `make`.  For aarch64
    processors, the default values are `TARGET=ARMV8` and
    `USE_OPENMP=1`.  For ppc64le processors, the default values are
    `TARGET=POWER8` and `USE_OPENMP=1`.  For x86_64 processors, the
    default value is `USE_OPENMP=1`.

    ospackages: List of OS packages to install prior to building.  The
    default values are `make`, `perl`, `tar`, and `wget`.

    prefix: The top level installation location.  The default value is
    `/usr/local/openblas`.

    toolchain: The toolchain object.  This should be used if
    non-default compilers or other toolchain options are needed.  The
    default is empty.

    version: The version of OpenBLAS source to download.  The default
    value is `0.3.6`.

    # Examples

    ```python
    openblas(prefix='/opt/openblas/0.3.1', version='0.3.1')
    ```

    ```python
    p = pgi(eula=True)
    openblas(toolchain=p.toolchain)
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(openblas, self).__init__(**kwargs)

        self.__baseurl = kwargs.get('baseurl', 'https://github.com/xianyi/OpenBLAS/archive')
        self.__make_opts = kwargs.get('make_opts',
                                      []) # Filled in by __cpu_arch()
        self.__ospackages = kwargs.get('ospackages', ['make', 'perl', 'tar',
                                                      'wget'])
        self.__prefix = kwargs.get('prefix', '/usr/local/openblas')
        self.__toolchain = kwargs.get('toolchain', toolchain())
        self.__version = kwargs.get('version', '0.3.6')

        self.__commands = [] # Filled in by __setup()
        self.__wd = '/var/tmp' # working directory

        # Set the CPU architecture specific parameters
        self.__cpu_arch()

        # Construct the series of steps to execute
        self.__setup()

        # Fill in container instructions
        self.__instructions()

    def __instructions(self):
        """Fill in container instructions"""

        self += comment('OpenBLAS version {}'.format(self.__version))
        self += packages(ospackages=self.__ospackages)
        self += shell(commands=self.__commands)
        self += environment(variables=self.environment_step())

    def __cpu_arch(self):
        """Based on the CPU architecture, set values accordingly.  A user
        specified value overrides any defaults."""

        if hpccm.config.g_cpu_arch == cpu_arch.AARCH64:
            if not self.__make_opts:
                self.__make_opts = ['TARGET=ARMV8', 'USE_OPENMP=1']
        elif hpccm.config.g_cpu_arch == cpu_arch.PPC64LE:
            if not self.__make_opts:
                self.__make_opts = ['TARGET=POWER8', 'USE_OPENMP=1']
        elif hpccm.config.g_cpu_arch == cpu_arch.X86_64:
            if not self.__make_opts:
                self.__make_opts = ['USE_OPENMP=1']
        else: # pragma: no cover
            raise RuntimeError('Unknown CPU architecture')

    def __setup(self):
        """Construct the series of shell commands, i.e., fill in
           self.__commands"""

        tarball = 'v{}.tar.gz'.format(self.__version)
        url = '{0}/{1}'.format(self.__baseurl, tarball)

        # Download source from web
        self.__commands.append(self.download_step(url=url,
                                                  directory=self.__wd))
        self.__commands.append(self.untar_step(
            tarball=posixpath.join(self.__wd, tarball), directory=self.__wd))

        compilers = []
        if self.__toolchain.CC:
            compilers.append('CC={}'.format(self.__toolchain.CC))
        if self.__toolchain.FC:
            compilers.append('FC={}'.format(self.__toolchain.FC))

        # Build
        self.__commands.append(
            'cd {} && make {} {}'.format(
                posixpath.join(self.__wd,
                               'OpenBLAS-{}'.format(self.__version)),
                ' '.join(compilers), ' '.join(self.__make_opts)))

        # Install
        self.__commands.append('make install PREFIX={}'.format(self.__prefix))

        # Set library path
        libpath = posixpath.join(self.__prefix, 'lib')
        if self.ldconfig:
            self.__commands.append(self.ldcache_step(directory=libpath))
        else:
            self.environment_variables['LD_LIBRARY_PATH'] = '{}:$LD_LIBRARY_PATH'.format(libpath)

        # Cleanup tarball and directory
        self.__commands.append(self.cleanup_step(
            items=[posixpath.join(self.__wd, tarball),
                   posixpath.join(self.__wd,
                                  'OpenBLAS-{}'.format(self.__version))]))

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples

        ```python
        o = openblas(...)
        Stage0 += o
        Stage1 += o.runtime()
        ```
        """
        instructions = []
        instructions.append(comment('OpenBLAS'))
        instructions.append(copy(_from=_from, src=self.__prefix,
                                 dest=self.__prefix))
        if self.ldconfig:
            instructions.append(shell(
                commands=[self.ldcache_step(
                    directory=posixpath.join(self.__prefix, 'lib'))]))
        instructions.append(environment(variables=self.environment_step()))
        return '\n'.join(str(x) for x in instructions)
