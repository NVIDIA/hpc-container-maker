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

"""Test cases for the Stage module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import docker

from hpccm.shell import shell
from hpccm.Stage import Stage

class Test_Stage(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    def test_value(self):
        """Single layer"""
        s = Stage()
        self.assertFalse(s.is_defined())
        s += 1
        self.assertTrue(s.is_defined())

    def test_list(self):
        """List of layers"""
        s = Stage()
        self.assertFalse(s.is_defined())
        s += [1, 2]
        self.assertTrue(s.is_defined())

    @docker
    def test_baseimage(self):
        """Base image specification"""
        s = Stage()
        s.name = 'bar'
        s.baseimage('foo')
        self.assertEqual(str(s), 'FROM foo AS bar')

    @docker
    def test_baseimage_first(self):
        """Base image is always first"""
        s = Stage()
        s += shell(commands=['abc'])
        s.name = 'bar'
        s.baseimage('foo')
        self.assertEqual(str(s), 'FROM foo AS bar\n\nRUN abc')
