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

# pylint: disable=invalid-name, too-few-public-methods

"""Test cases for the ldconfig module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from hpccm.templates.ldconfig import ldconfig

class Test_ldconfig(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    def test_no_directory(self):
        """No directory specified"""
        l = ldconfig()

        self.assertEqual(l.ldcache_step(directory=None), '')

    def test_basic(self):
        """Basic ldconfig"""
        l = ldconfig()

        self.assertEqual(l.ldcache_step(directory='/usr/local/lib'),
                         'echo "/usr/local/lib" >> /etc/ld.so.conf.d/hpccm.conf && ldconfig')
