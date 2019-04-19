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

"""Test cases for the workdir module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import bash, docker, invalid_ctype, singularity

from hpccm.primitives.workdir import workdir

class Test_workdir(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @docker
    def test_empty(self):
        """No workdir specified"""
        w = workdir()
        self.assertEqual(str(w), '')

    @invalid_ctype
    def test_invalid_ctype(self):
        """Invalid container type specified"""
        w = workdir(directory='foo')
        with self.assertRaises(RuntimeError):
            str(w)

    @docker
    def test_dir_docker(self):
        """Working directory specified"""
        w = workdir(directory='foo')
        self.assertEqual(str(w), 'WORKDIR foo')

    @singularity
    def test_dir_singularity(self):
        """Working directory specified"""
        w = workdir(directory='foo')
        self.assertEqual(str(w), '%post\n    cd /\n    mkdir -p foo\n    cd foo')

    @bash
    def test_dir_bash(self):
        """Working directory specified"""
        w = workdir(directory='foo')
        self.assertEqual(str(w), '')
