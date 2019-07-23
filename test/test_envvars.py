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

"""Test cases for the envvars module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from hpccm.templates.envvars import envvars

class Test_envvars(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    def test_no_variables(self):
        """No variables specified"""
        e = envvars()

        self.assertDictEqual(e.environment_step(), {})

    def test_basic(self):
        """Basic envvars"""
        d = {'A': 'a', 'B': 'b', 'one': 1}
        e = envvars()
        e.environment_variables = d

        self.assertDictEqual(e.environment_step(), d)

        e.environment = False
        self.assertDictEqual(e.environment_step(), {})

    def test_include_exclude(self):
        """Include / exclude keys"""
        d = {'A': 'a', 'B': 'b', 'one': 1}
        e = envvars()
        e.environment_variables = d

        self.assertDictEqual(e.environment_step(exclude=['B']),
                             {'A': 'a', 'one': 1})

        self.assertDictEqual(e.environment_step(include_only=['A', 'one']),
                             {'A': 'a', 'one': 1})

    def test_runtime(self):
        """Runtime environment variables"""
        d = {'A': 'a', 'B': 'b', 'one': 1}
        r = {'A': 'alpha', 'B': 'b'}
        e = envvars()
        e.environment_variables = d
        e.runtime_environment_variables = r

        self.assertDictEqual(e.environment_step(runtime=True),
                             {'A': 'alpha', 'B': 'b'})
