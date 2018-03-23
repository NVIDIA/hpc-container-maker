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

"""Test cases for the environment module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from hpccm.common import container_type
from hpccm.environment import environment

class Test_environment(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    def test_empty(self):
        """No environment specified"""
        e = environment()
        self.assertEqual(e.toString(container_type.DOCKER), '')

    def test_invalid_ctype(self):
        """Invalid container type specified"""
        e = environment(variables={'A': 'B'})
        self.assertEqual(e.toString(None), '')

    def test_single(self):
        """Single environment variable specified"""
        e = environment(variables={'A': 'B'}, _export=False)
        self.assertEqual(e.toString(container_type.DOCKER), 'ENV A=B')
        self.assertEqual(e.toString(container_type.SINGULARITY),
                         '%environment\n    export A=B')

    def test_single_export(self):
        """Single environment variable specified"""
        e = environment(variables={'A': 'B'})
        self.assertEqual(e.toString(container_type.DOCKER), 'ENV A=B')
        self.assertEqual(e.toString(container_type.SINGULARITY),
                         '%environment\n    export A=B\n%post\n    export A=B')

    def test_multiple(self):
        """Multiple environment variables specified"""
        e = environment(variables={'ONE': 1, 'TWO': 2, 'THREE': 3},
                        _export=False)
        self.assertEqual(e.toString(container_type.DOCKER),
'''ENV ONE=1 \\
    THREE=3 \\
    TWO=2''')
        self.assertEqual(e.toString(container_type.SINGULARITY),
'''%environment
    export ONE=1
    export THREE=3
    export TWO=2''')
