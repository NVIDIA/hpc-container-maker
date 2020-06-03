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

from hpccm.templates.zip import zip

class Test_zip(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    def test_missing_zipfile(self):
        """Missing zipfile option"""
        t = zip()
        self.assertEqual(t.unzip_step(), '')

    def test_filetypes(self):
        t = zip()
        zipfile='foo.zip'
        self.assertEqual(t.unzip_step(zipfile),
                         'unzip {0}'.format(zipfile))

    def test_directory(self):
        """Directory specified"""
        t = zip()
        zipfile='foo.zip'
        directory='bar'
        self.assertEqual(t.unzip_step(zipfile, directory),
                         'mkdir -p {0} && unzip -d {0} {1}'.format(directory,zipfile))
