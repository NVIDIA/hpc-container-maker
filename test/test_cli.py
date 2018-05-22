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

"""Test cases for the cli module"""

from __future__ import unicode_literals
from __future__ import print_function

import argparse
import logging # pylint: disable=unused-import
import unittest

from hpccm.cli import KeyValue

class Test_cli(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    def test_argparse_userarg(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--userarg', action=KeyValue, nargs='+')
        args = parser.parse_args(['--userarg',  'a=b', 'c=d', 'e="f f f"'])
        self.assertEqual(args.userarg['a'], 'b')
        self.assertEqual(args.userarg['c'], 'd')
        self.assertEqual(args.userarg['e'], '"f f f"')
