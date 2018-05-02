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

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import

from .apt_get import apt_get
from .comment import comment

class python(object):
    """Python building block"""

    def __init__(self, **kwargs):
        """Initialize building block"""

        # Trouble getting MRO with kwargs working correctly, so just call
        # the parent class constructors manually for now.
        #super(python, self).__init__(**kwargs)

        self.__python2 = kwargs.get('python2', True)
        self.__python3 = kwargs.get('python3', True)

        self.__packages = [] # Filled in below

        if self.__python2:
            self.__packages.append('python')

        if self.__python3:
            self.__packages.append('python3')

    def runtime(self, _from='0'):
        """Runtime specification"""
        instructions = []
        instructions.append(comment('Python'))
        instructions.append(apt_get(ospackages=self.__packages))
        return instructions

    def toString(self, ctype):
        """Building block container specification"""
        instructions = []
        instructions.append(comment('Python'))
        instructions.append(apt_get(ospackages=self.__packages))

        return '\n'.join([x.toString(ctype) for x in instructions])
