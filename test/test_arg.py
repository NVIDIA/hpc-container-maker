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

"""Test cases for the arg module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import bash, docker, invalid_ctype, singularity

from hpccm.primitives.arg import arg

class Test_arg(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @docker
    def test_empty(self):
        """No arg specified"""
        e = arg()
        self.assertEqual(str(e), '')

    @invalid_ctype
    def test_invalid_ctype(self):
        """Invalid container type specified"""
        e = arg(variables={'A': 'B'})
        with self.assertRaises(RuntimeError):
            str(e)

    @docker
    def test_single_docker(self):
        """Single arg variable specified"""
        e = arg(variables={'A': 'B'})
        self.assertEqual(str(e), 'ARG A=B')

    @docker
    def test_single_docker_nodefault(self):
        """Single arg variable specified (no default value)"""
        e = arg(variables={'A': ''})
        self.assertEqual(str(e), 'ARG A')

    @singularity
    def test_single_singularity(self):
        """Single arg variable specified"""
        e = arg(variables={'A': 'B'})
        self.assertEqual(str(e), '%post\n    A=${A:-"B"}')

    @singularity
    def test_single_singularity_nodefault(self):
        """Single arg variable specified"""
        e = arg(variables={'A': ''})
        self.assertEqual(str(e), '%post\n    A=${A:-""}')

    @bash
    def test_single_bash(self):
        """Single arg variable specified"""
        e = arg(variables={'A': 'B'})
        self.assertEqual(str(e), 'A=${A:-"B"}')

    @bash
    def test_single_bash_nodefault(self):
        """Single arg variable specified"""
        e = arg(variables={'A': ''})
        self.assertEqual(str(e), 'A=${A:-""}')

    @docker
    def test_multiple_docker(self):
        """Multiple arg variables specified"""
        e = arg(variables={'ONE': 1, 'TWO': 2, 'THREE': 3})
        self.assertEqual(str(e),
'''ARG ONE=1
ARG THREE=3
ARG TWO=2''')

    @docker
    def test_multiple_docker_nodefault(self):
        """Multiple arg variables specified (no default value)"""
        e = arg(variables={'ONE': '', 'TWO': '', 'THREE': ''})
        self.assertEqual(str(e),
'''ARG ONE
ARG THREE
ARG TWO''')

    @singularity
    def test_multiple_singularity(self):
        """Multiple arg variables specified"""
        e = arg(variables={'ONE': 1, 'TWO': 2, 'THREE': 3})
        self.assertEqual(str(e),
'''%post
    ONE=${ONE:-"1"}
    THREE=${THREE:-"3"}
    TWO=${TWO:-"2"}''')

    @singularity
    def test_multiple_singularity_nodefault(self):
        """Multiple arg variables specified"""
        e = arg(variables={'ONE':"", 'TWO':"", 'THREE':""})
        self.assertEqual(str(e),
'''%post
    ONE=${ONE:-""}
    THREE=${THREE:-""}
    TWO=${TWO:-""}''')

    @bash
    def test_multiple_bash(self):
        """Multiple arg variables specified"""
        e = arg(variables={'ONE': 1, 'TWO': 2, 'THREE': 3})
        self.assertEqual(str(e),
'''ONE=${ONE:-"1"}
THREE=${THREE:-"3"}
TWO=${TWO:-"2"}''')

    @bash
    def test_multiple_bash_nodefault(self):
        """Multiple arg variables specified"""
        e = arg(variables={'ONE': "", 'TWO': "", 'THREE': ""})
        self.assertEqual(str(e),
'''ONE=${ONE:-""}
THREE=${THREE:-""}
TWO=${TWO:-""}''')