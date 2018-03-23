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

from hpccm.common import container_type
from hpccm.raw import raw

class Test_raw(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    def test_empty(self):
        """No raw strings specified"""
        r = raw()
        self.assertEqual(r.toString(container_type.DOCKER), '')

    def test_invalid_ctype(self):
        """Invalid container type specified"""
        r = raw(docker='RAW')
        self.assertEqual(r.toString(None), '')

    def test_docker_only(self):
        """Only Docker string specified"""
        r = raw(docker='RAW string')
        self.assertEqual(r.toString(container_type.DOCKER), 'RAW string')
        self.assertEqual(r.toString(container_type.SINGULARITY), '')

    def test_singularity_only(self):
        """Only Singularity string specified"""
        r = raw(singularity='%raw\n    string')
        self.assertEqual(r.toString(container_type.DOCKER), '')
        self.assertEqual(r.toString(container_type.SINGULARITY),
                         '%raw\n    string')

    def test_all(self):
        """Both Docker and Singularity strings specified"""
        r = raw(docker='RAW string', singularity='%raw\n    string')
        self.assertEqual(r.toString(container_type.DOCKER), 'RAW string')
        self.assertEqual(r.toString(container_type.SINGULARITY),
                         '%raw\n    string')
