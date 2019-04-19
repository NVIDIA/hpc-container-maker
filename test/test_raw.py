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

"""Test cases for the raw module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import bash, docker, invalid_ctype, singularity

from hpccm.primitives.raw import raw

class Test_raw(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @docker
    def test_empty(self):
        """No raw strings specified"""
        r = raw()
        self.assertEqual(str(r), '')

    @invalid_ctype
    def test_invalid_ctype(self):
        """Invalid container type specified"""
        r = raw(docker='RAW')
        with self.assertRaises(RuntimeError):
            str(r)

    @docker
    def test_docker_only_docker(self):
        """Only Docker string specified"""
        r = raw(docker='RAW string')
        self.assertEqual(str(r), 'RAW string')

    @singularity
    def test_docker_only_singularity(self):
        """Only Docker string specified"""
        r = raw(docker='RAW string')
        self.assertEqual(str(r), '')

    @docker
    def test_singularity_only_docker(self):
        """Only Singularity string specified"""
        r = raw(singularity='%raw\n    string')
        self.assertEqual(str(r), '')

    @singularity
    def test_singularity_only_singularity(self):
        """Only Singularity string specified"""
        r = raw(singularity='%raw\n    string')
        self.assertEqual(str(r), '%raw\n    string')

    @docker
    def test_all_docker(self):
        """Both Docker and Singularity strings specified"""
        r = raw(docker='RAW string', singularity='%raw\n    string')
        self.assertEqual(str(r), 'RAW string')

    @singularity
    def test_all_singularity(self):
        """Both Docker and Singularity strings specified"""
        r = raw(docker='RAW string', singularity='%raw\n    string')
        self.assertEqual(str(r), '%raw\n    string')

    @bash
    def test_all_bash(self):
        """Both Docker and Singularity strings specified"""
        r = raw(docker='RAW string', singularity='%raw\n    string')
        self.assertEqual(str(r), '')
