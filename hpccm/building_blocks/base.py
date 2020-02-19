# Copyright (c) 2019, NVIDIA CORPORATION.  All rights reserved.
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

"""Building block base class"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import hpccm.base_object

class bb_base(hpccm.base_object):
    """Base class for building blocks."""

    def __init__(self, **kwargs):
        """Initialize building block base class"""

        super(bb_base, self).__init__(**kwargs)

        self.__instructions_bb = []

    def __iadd__(self, instruction):
        """Add the instruction to the list of instructions.  Allows "+="
        syntax."""

        if isinstance(instruction, list):
            self.__instructions_bb.extend(instruction)
        else:
            self.__instructions_bb.append(instruction)
        return self

    def __getitem__(self, key):
        """Return the specified element from the list of instructions"""
        return self.__instructions_bb[key]

    def __len__(self):
        """Return the size of the list of instructions"""
        return len(self.__instructions_bb)

    def __str__(self):
        """String representation of the building block"""
        return '\n'.join(str(x) for x in self.__instructions_bb if str(x))
