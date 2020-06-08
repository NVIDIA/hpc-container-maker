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

"""Test cases for the zip module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from hpccm.templates.zipfile import zipfile

class Test_zipfile(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    def test_missing_zipfile(self):
        """Missing zipfile option"""
        z = zipfile()
        self.assertEqual(z.unzip_step(), '')

    def test_filetypes(self):
        z = zipfile()
        self.assertEqual(z.unzip_step('foo.zip'), 'unzip foo.zip')

    def test_directory(self):
        """Directory specified"""
        z = zipfile()
        self.assertEqual(z.unzip_step('foo.zip', 'bar'),
                         'mkdir -p bar && unzip -d bar foo.zip')
