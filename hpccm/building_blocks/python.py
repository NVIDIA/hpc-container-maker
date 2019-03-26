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

"""Python building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.packages import packages
from hpccm.primitives.comment import comment

class python(bb_base):
    """The `python` building block installs Python from the upstream Linux
    distribution.

    # Parameters

    devel: Boolean flag to specify whether to also install the Python
    development headers and libraries.  The default is False.

    python2: Boolean flag to specify whether to install Python version
    2.  The default is True.

    python3: Boolean flag to specify whether to install Python version
    3.  The default is True.

    # Examples

    ```python
    python()
    ```

    ```python
    python(python3=False)
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(python, self).__init__(**kwargs)

        self.__devel = kwargs.get('devel', False)
        self.__epel = False
        self.__python2 = kwargs.get('python2', True)
        self.__python3 = kwargs.get('python3', True)

        self.__debs = [] # Filled in below
        self.__rpms = [] # Filled in below

        if self.__python2:
            self.__debs.append('python')
            self.__rpms.append('python')
            if self.__devel:
                self.__debs.append('python-dev')
                self.__rpms.append('python-devel')

        if self.__python3:
            self.__debs.append('python3')
            self.__rpms.append('python34')  # EPEL package
            self.__epel = True
            if self.__devel:
                self.__debs.append('python3-dev')
                self.__rpms.append('python34-devel')  # EPEL package

        # Fill in container instructions
        self.__instructions()

    def __instructions(self):
        """Fill in container instructions"""

        self += comment('Python')
        self += packages(apt=self.__debs, epel=self.__epel, yum=self.__rpms)

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples

        ```python
        p = python(...)
        Stage0 += p
        Stage1 += p.runtime()
        ```
        """
        instructions = []
        instructions.append(comment('Python'))
        instructions.append(packages(apt=self.__debs, epel=self.__epel,
                                     yum=self.__rpms))
        return '\n'.join(str(x) for x in instructions)
