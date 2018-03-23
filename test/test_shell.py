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

"""Test cases for the shell module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from hpccm.common import container_type
from hpccm.shell import shell

class Test_shell(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    def test_empty(self):
        """No commands specified"""
        s = shell()
        self.assertEqual(s.toString(container_type.DOCKER), '')

    def test_invalid_ctype(self):
        """Invalid container type specified"""
        s = shell(commands=['a'])
        self.assertEqual(s.toString(None), '')

    def test_single(self):
        """Single command specified"""
        cmd = ['z']

        s = shell(commands=cmd)

        self.assertEqual(s.toString(container_type.DOCKER), 'RUN z')
        self.assertEqual(s.toString(container_type.SINGULARITY),
                         '%post\n    z')

    def test_multiple(self):
        """List of commands specified"""
        cmds = ['a', 'b', 'c']

        s = shell(commands=cmds)

        self.assertEqual(s.toString(container_type.DOCKER),
                         'RUN a && \\\n    b && \\\n    c')
        self.assertEqual(s.toString(container_type.SINGULARITY),
                         '%post\n    a\n    b\n    c')
