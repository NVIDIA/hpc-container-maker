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

"""KNEM building block"""

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
from hpccm.primitives.environment import environment
from hpccm.primitives.shell import shell
from hpccm.templates.git import git
from hpccm.templates.rm import rm

class knem(git, rm):
    """The `knem` building block install the headers from the
    [KNEM](http://knem.gforge.inria.fr) component.

    As a side effect, this building block modifies `CPATH`,
    `LD_LIBRARY_PATH`, and `LIBRARY_PATH`.

    # Parameters

    ospackages: List of OS packages to install prior to installing.
    The default values are `ca-certificates` and `git`.

    prefix: The top level install location.  The default value is
    `/usr/local/knem`.

    version: The version of KNEM source to download.  The default
    value is `1.1.3`.

    # Examples

    ```python
    knem(prefix='/opt/knem/1.1.3', version='1.1.3')
    ```
    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        # Trouble getting MRO with kwargs working correctly, so just call
        # the parent class constructors manually for now.
        #super(knem, self).__init__(**kwargs)
        git.__init__(self, **kwargs)
        rm.__init__(self, **kwargs)

        self.__ospackages = kwargs.get('ospackages', ['ca-certificates', 'git'])
        self.__prefix = kwargs.get('prefix', '/usr/local/knem')
        self.__repository = kwargs.get('repository', 'https://gforge.inria.fr/git/knem/knem.git')
        self.__version = kwargs.get('version', '1.1.3')

        self.__commands = [] # Filled in by __setup()
        self.__environment_variables = {
            'CPATH':
            '{}:$CPATH'.format(os.path.join(self.__prefix, 'include'))}
        self.__wd = '/var/tmp' # working directory

        # Construct the series of steps to execute
        self.__setup()

    def __str__(self):
        """String representation of the building block"""

        instructions = []
        instructions.append(comment(
            'KNEM version {}'.format(self.__version)))
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
            branch='knem-{}'.format(self.__version),
            repository=self.__repository,
            path=self.__wd, directory='knem'))

        # Copy header(s)
        self.__commands.append('mkdir -p {}/include'.format(self.__prefix))
        self.__commands.append('cp {0}/common/*.h {1}/include'.format(
            os.path.join(self.__wd, 'knem'), self.__prefix))

        # Cleanup directory
        self.__commands.append(self.cleanup_step(
                   [os.path.join(self.__wd, 'knem')]))

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples

        ```python
        k = knem(...)
        Stage0 += k
        Stage1 += k.runtime()
        ```
        """
        instructions = []
        instructions.append(comment('KNEM'))
        instructions.append(copy(_from=_from, src=self.__prefix,
                                 dest=self.__prefix))
        instructions.append(
            environment(variables=self.__environment_variables))
        return '\n'.join(str(x) for x in instructions)
