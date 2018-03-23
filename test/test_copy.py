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

"""Test cases for the copy module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from hpccm.common import container_type
from hpccm.copy import copy

class Test_copy(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    def test_empty(self):
        """No source or destination specified"""
        c = copy()
        self.assertEqual(c.toString(container_type.DOCKER), '')

    def test_invalid_ctype(self):
        """Invalid container type specified"""
        c = copy(src='a', dest='b')
        self.assertEqual(c.toString(None), '')

    def test_single(self):
        """Single source file specified"""
        c = copy(src='a', dest='b')
        self.assertEqual(c.toString(container_type.DOCKER), 'COPY a b')
        self.assertEqual(c.toString(container_type.SINGULARITY),
                         '%files\n    a b')

    def test_multiple(self):
        """Multiple source files specified"""
        c = copy(src=['a1', 'a2', 'a3'], dest='b')
        self.assertEqual(c.toString(container_type.DOCKER),
                         'COPY a1 \\\n    a2 \\\n    a3 \\\n    b/')
        self.assertEqual(c.toString(container_type.SINGULARITY),
                         '%files\n    a1 b\n    a2 b\n    a3 b')

    def test_from(self):
        """Docker --from syntax"""
        c = copy(src='a', dest='b', _from='dev')
        self.assertEqual(c.toString(container_type.DOCKER),
                         'COPY --from=dev a b')
        self.assertEqual(c.toString(container_type.SINGULARITY),
                         '%files\n    a b')
