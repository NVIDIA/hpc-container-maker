# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
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

"""Test cases for the toolchain module"""

from __future__ import unicode_literals
from __future__ import print_function

from copy import copy, deepcopy
import logging # pylint: disable=unused-import
import unittest

from hpccm.toolchain import toolchain

class Test_toolchain(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    def test_creation(self):
        """Toolchain creation"""
        t = toolchain(CC='gcc', CXX='g++', FC='gfortran')
        self.assertEqual(t.CC, 'gcc')
        self.assertEqual(t.CXX, 'g++')
        self.assertEqual(t.FC, 'gfortran')

    def test_modification(self):
        """Toolchain modification"""
        t = toolchain(CC='gcc', CXX='g++', FC='gfortran')
        t.CC = 'mygcc'
        self.assertEqual(t.CC, 'mygcc')
        self.assertEqual(t.CXX, 'g++')
        self.assertEqual(t.FC, 'gfortran')

    def test_copy(self):
        """Toolchain copies"""
        t = toolchain(CC='gcc', CXX='g++', FC='gfortran')
        r = t # ref
        c = copy(t)
        d = deepcopy(t)
        t.CC = 'mygcc'
        c.CC = 'cc'
        self.assertEqual(t.CC, 'mygcc')
        self.assertEqual(r.CC, 'mygcc')
        self.assertEqual(c.CC, 'cc')
        self.assertEqual(d.CC, 'gcc')

    def test_vars(self):
        """Toolchain dictionaries"""
        t = toolchain(CC='gcc', CXX='g++', FC='gfortran')
        v = vars(t)
        self.assertDictEqual(v, {'CC': 'gcc', 'CXX': 'g++', 'FC': 'gfortran'})

    def test_unknown_keys(self):
        """Toolchain unknown keys"""
        t = toolchain(FOO='bar')
        with self.assertRaises(AttributeError):
            f = t.FOO
