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
import os

from hpccm.building_blocks.packages import packages
from hpccm.primitives.comment import comment
from hpccm.primitives.copy import copy
from hpccm.primitives.environment import environment
from hpccm.primitives.shell import shell
from hpccm.templates.ConfigureMake import ConfigureMake
from hpccm.templates.git import git
from hpccm.templates.rm import rm
from hpccm.templates.tar import tar
from hpccm.toolchain import toolchain

class xpmem(ConfigureMake, git, rm, tar):
    """The `xpmem` building block builds and installs the user space
    library from the [XPMEM](https://gitlab.com/hjelmn/xpmem)
    component.

    As a side effect, this building block modifies `CPATH`,
    `LD_LIBRARY_PATH`, and `LIBRARY_PATH`.

    # Parameters

    branch: The branch of XPMEM to use.  The default value is
    `master`.

    configure_opts: List of options to pass to `configure`.  The
    default values are `--disable-kernel-module`.

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

        # Trouble getting MRO with kwargs working correctly, so just call
        # the parent class constructors manually for now.
        #super(xpmem, self).__init__(**kwargs)
        ConfigureMake.__init__(self, **kwargs)
        git.__init__(self, **kwargs)
        tar.__init__(self, **kwargs)
        rm.__init__(self, **kwargs)

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
        self.__environment_variables = {
            'CPATH':
            '{}:$CPATH'.format(os.path.join(self.prefix, 'include')),
            'LD_LIBRARY_PATH':
            '{}:$LD_LIBRARY_PATH'.format(os.path.join(self.prefix, 'lib')),
            'LIBRARY_PATH':
            '{}:$LIBRARY_PATH'.format(os.path.join(self.prefix, 'lib'))}
        self.__wd = '/var/tmp' # working directory

        # Construct the series of steps to execute
        self.__setup()

    def __str__(self):
        """String representation of the building block"""

        instructions = []
        instructions.append(comment(
            'XPMEM branch {}'.format(self.__branch)))
        instructions.append(packages(ospackages=self.__ospackages))
        instructions.append(shell(commands=self.__commands))
        instructions.append(
            environment(variables=self.__environment_variables))

        return '\n'.join(str(x) for x in instructions)

    def __setup(self):
        """Construct the series of shell commands, i.e., fill in
           self.__commands"""

        # Clone source
        self.__commands.append(self.clone_step(
            branch=self.__branch, repository=self.__repository,
            path=self.__wd, directory='xpmem'))
        # Build
        self.__commands.append('cd {} && autoreconf --install'.format(
            os.path.join(self.__wd, 'xpmem')))
        self.__commands.append(self.configure_step(
            directory=os.path.join(self.__wd, 'xpmem'),
            toolchain=self.__toolchain))

        self.__commands.append(self.build_step())
        self.__commands.append(self.install_step())

        # Cleanup directory
        self.__commands.append(self.cleanup_step(
                   [os.path.join(self.__wd, 'xpmem')]))

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
        instructions.append(
            environment(variables=self.__environment_variables))
        return '\n'.join(str(x) for x in instructions)
