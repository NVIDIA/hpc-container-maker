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

"""Test cases for the user module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import bash, docker, invalid_ctype, singularity

from hpccm.primitives.user import user

class Test_user(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @docker
    def test_empty(self):
        """No user specified"""
        u = user()
        self.assertEqual(str(u), '')

    @invalid_ctype
    def test_invalid_ctype(self):
        """Invalid container type specified"""
        u = user(user='root')
        with self.assertRaises(RuntimeError):
            str(u)

    @docker
    def test_docker(self):
        """User specified"""
        u = user(user='root')
        self.assertEqual(str(u), 'USER root')

    @singularity
    def test_singularity(self):
        """User specified"""
        u = user(user='root')
        self.assertEqual(str(u), '')

    @bash
    def test_bash(self):
        """User specified"""
        u = user(user='root')
        self.assertEqual(str(u), '')
