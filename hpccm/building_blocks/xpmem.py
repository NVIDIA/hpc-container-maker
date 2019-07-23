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

"""XPMEM building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import posixpath

import hpccm.templates.ConfigureMake
import hpccm.templates.envvars
import hpccm.templates.git
import hpccm.templates.ldconfig
import hpccm.templates.rm
import hpccm.templates.tar

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.packages import packages
from hpccm.primitives.comment import comment
from hpccm.primitives.copy import copy
from hpccm.primitives.environment import environment
from hpccm.primitives.shell import shell
from hpccm.toolchain import toolchain

class xpmem(bb_base, hpccm.templates.ConfigureMake, hpccm.templates.envvars,
            hpccm.templates.ldconfig, hpccm.templates.git, hpccm.templates.rm,
            hpccm.templates.tar):
    """The `xpmem` building block builds and installs the user space
    library from the [XPMEM](https://gitlab.com/hjelmn/xpmem)
    component.

    # Parameters

    branch: The branch of XPMEM to use.  The default value is
    `master`.

    configure_opts: List of options to pass to `configure`.  The
    default values are `--disable-kernel-module`.

    environment: Boolean flag to specify whether the environment
    (`CPATH`, `LD_LIBRARY_PATH` and `LIBRARY_PATH`) should be modified
    to include XPMEM. The default is True.

    ldconfig: Boolean flag to specify whether the XPMEM library
    directory should be added dynamic linker cache.  If False, then
    `LD_LIBRARY_PATH` is modified to include the XPMEM library
    directory. The default value is False.

    ospackages: List of OS packages to install prior to configuring
    and building.  The default value are `autoconf`, `automake`,
    `ca-certificates`, `file, `git`, `libtool`, and `make`.

    prefix: The top level install location.  The default value is
    `/usr/local/xpmem`.

    toolchain: The toolchain object.  This should be used if
    non-default compilers or other toolchain options are needed.  The
    default is empty.

    # Examples

    ```python
    xpmem(prefix='/opt/xpmem', branch='master')
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(xpmem, self).__init__(**kwargs)

        self.configure_opts = kwargs.get('configure_opts',
                                         ['--disable-kernel-module'])
        self.prefix = kwargs.get('prefix', '/usr/local/xpmem')

        self.__branch = kwargs.get('branch', 'master')
        self.__ospackages = kwargs.get('ospackages', ['autoconf', 'automake',
                                                      'ca-certificates',
                                                      'file', 'git',
                                                      'libtool', 'make'])
        self.__repository = kwargs.get('repository',
                                       'https://gitlab.com/hjelmn/xpmem.git')
        self.__toolchain = kwargs.get('toolchain', toolchain())

        self.__commands = [] # Filled in by __setup()
        self.__wd = '/var/tmp' # working directory

        # Construct the series of steps to execute
        self.__setup()

        # Fill in container instructions
        self.__instructions()

    def __instructions(self):
        """Fill in container instructions"""

        self += comment('XPMEM branch {}'.format(self.__branch))
        self += packages(ospackages=self.__ospackages)
        self += shell(commands=self.__commands)
        self += environment(variables=self.environment_step())

    def __setup(self):
        """Construct the series of shell commands, i.e., fill in
           self.__commands"""

        # Clone source
        self.__commands.append(self.clone_step(
            branch=self.__branch, repository=self.__repository,
            path=self.__wd, directory='xpmem'))
        # Build
        self.__commands.append('cd {} && autoreconf --install'.format(
            posixpath.join(self.__wd, 'xpmem')))
        self.__commands.append(self.configure_step(
            directory=posixpath.join(self.__wd, 'xpmem'),
            toolchain=self.__toolchain))

        self.__commands.append(self.build_step())
        self.__commands.append(self.install_step())

        # Set library path
        libpath = posixpath.join(self.prefix, 'lib')
        if self.ldconfig:
            self.__commands.append(self.ldcache_step(directory=libpath))
        else:
            self.environment_variables['LD_LIBRARY_PATH'] = '{}:$LD_LIBRARY_PATH'.format(libpath)

        # Cleanup directory
        self.__commands.append(self.cleanup_step(
                   [posixpath.join(self.__wd, 'xpmem')]))

        # Set the environment
        self.environment_variables['CPATH'] = '{}:$CPATH'.format(
            posixpath.join(self.prefix, 'include'))
        self.environment_variables['LIBRARY_PATH'] = '{}:$LIBRARY_PATH'.format(
            posixpath.join(self.prefix, 'lib'))

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples

        ```python
        x = xpmem(...)
        Stage0 += x
        Stage1 += x.runtime()
        ```
        """
        instructions = []
        instructions.append(comment('XPMEM'))
        instructions.append(copy(_from=_from, src=self.prefix,
                                 dest=self.prefix))
        if self.ldconfig:
            instructions.append(shell(
                commands=[self.ldcache_step(
                    directory=posixpath.join(self.prefix, 'lib'))]))
        instructions.append(environment(variables=self.environment_step()))
        return '\n'.join(str(x) for x in instructions)
