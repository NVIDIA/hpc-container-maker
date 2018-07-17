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

"""Test cases for the sed module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from hpccm.templates.sed import sed

class Test_sed(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    def test_basic(self):
        """Basic sed"""
        s = sed()
        self.assertEqual(s.sed_step(file='foo',
                                    patterns=[r's/a/A/g',
                                              r's/FOO = BAR/FOO = BAZ/g']),
r'''sed -i -e s/a/A/g \
        -e 's/FOO = BAR/FOO = BAZ/g' foo''')

    def test_nofile(self):
        """No file specified"""
        s = sed()
        self.assertEqual(s.sed_step(patterns=[r's/a/A/g']), '')

    def test_nopatterns(self):
        """No patterns specified"""
        s = sed()
        self.assertEqual(s.sed_step(file='foo'), '')
