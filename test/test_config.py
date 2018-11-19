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

"""Test cases for the config module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import docker, singularity

import hpccm.config

class Test_config(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @singularity
    def test_set_container_format_docker(self):
        """Set container format to Docker"""
        hpccm.config.set_container_format('docker')
        self.assertEqual(hpccm.config.g_ctype, hpccm.container_type.DOCKER)

    @docker
    def test_set_container_format_singularity(self):
        """Set container format to Singularity"""
        hpccm.config.set_container_format('singularity')
        self.assertEqual(hpccm.config.g_ctype, hpccm.container_type.SINGULARITY)

    @docker
    def test_set_container_format_invalid(self):
        """Set container format to invalid value"""
        with self.assertRaises(RuntimeError):
            hpccm.config.set_container_format('invalid')
