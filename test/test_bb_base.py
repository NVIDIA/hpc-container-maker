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

# pylint: disable=invalid-name, too-few-public-methods, bad-continuation

"""Test cases for the building block base class"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import centos, docker, ubuntu

from hpccm.building_blocks.base import bb_base
from hpccm.primitives import shell

class Test_bb_base(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @ubuntu
    @docker
    def test_defaults(self):
        """Default building block base class"""
        b = bb_base()
        self.assertEqual(str(b), '')

    @ubuntu
    @docker
    def test_instruction_manipulations(self):
        """Instruction manipulations"""
        b = bb_base()

        # Append instructions
        b += shell(commands=['echo a'])
        # Append directly to "private" class variable (not recommended)
        b._bb_base__instructions_bb.append(shell(commands=['echo b']))
        self.assertEqual(len(b), 2)
        self.assertEqual(str(b), 'RUN echo a\nRUN echo b')

        # Direct element access
        self.assertEqual(str(b[0]), 'RUN echo a')
        self.assertEqual(str(b[1]), 'RUN echo b')

        # Iterators
        i = iter(b)
        self.assertEqual(str(next(i)), 'RUN echo a')
        self.assertEqual(str(next(i)), 'RUN echo b')

        # Insertion, using "private" class variable (not recommended)
        b._bb_base__instructions_bb.insert(0, shell(commands=['echo c']))
        self.assertEqual(len(b), 3)
        self.assertEqual(str(b), 'RUN echo c\nRUN echo a\nRUN echo b')

        # Deletion (not allowed)
        with self.assertRaises(TypeError):
            del(b[1])

        # Deletion via "private" class variable (not recommended)
        del(b._bb_base__instructions_bb[1])
        self.assertEqual(len(b), 2)
        self.assertEqual(str(b), 'RUN echo c\nRUN echo b')
