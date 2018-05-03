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

# pylint: disable=invalid-name, too-few-public-methods, bad-continuation

"""Test cases for the label module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import docker, invalid_ctype, singularity

from hpccm.label import label

class Test_label(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @docker
    def test_empty(self):
        """No label specified"""
        l = label()
        self.assertEqual(str(l), '')

    @invalid_ctype
    def test_invalid_ctype(self):
        """Invalid container type specified"""
        l = label(metadata={'A': 'B'})
        with self.assertRaises(RuntimeError):
            str(l)

    @docker
    def test_single_docker(self):
        """Single label specified"""
        l = label(metadata={'A': 'B'})
        self.assertEqual(str(l), 'LABEL A=B')

    @singularity
    def test_single_singularity(self):
        """Single label specified"""
        l = label(metadata={'A': 'B'})
        self.assertEqual(str(l), '%labels\n    A B')

    @docker
    def test_multiple_docker(self):
        """Multiple labels specified"""
        l = label(metadata={'ONE': 1, 'TWO': 2, 'THREE': 3})
        self.assertEqual(str(l),
'''LABEL ONE=1 \\
    THREE=3 \\
    TWO=2''')

    @singularity
    def test_multiple_singularity(self):
        """Multiple labels specified"""
        l = label(metadata={'ONE': 1, 'TWO': 2, 'THREE': 3})
        self.assertEqual(str(l),
'''%labels
    ONE 1
    THREE 3
    TWO 2''')
