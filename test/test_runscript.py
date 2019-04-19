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

"""Test cases for the runscript module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import bash, docker, invalid_ctype, singularity

from hpccm.primitives.runscript import runscript

class Test_runscript(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @docker
    def test_empty(self):
        """No commands specified"""
        s = runscript()
        self.assertEqual(str(s), '')

    @invalid_ctype
    def test_invalid_ctype(self):
        """Invalid container type specified"""
        s = runscript(commands=['a'])
        with self.assertRaises(RuntimeError):
            str(s)

    @docker
    def test_single_docker(self):
        """Single command specified"""
        cmd = ['z arg1 arg2']
        s = runscript(commands=cmd)
        self.assertEqual(str(s), 'ENTRYPOINT ["z", "arg1", "arg2"]')

    @singularity
    def test_single_singularity(self):
        """Single command specified"""
        cmd = ['z']
        s = runscript(commands=cmd)
        self.assertEqual(str(s), '%runscript\n    exec z "$@"')

    @docker
    def test_multiple_docker(self):
        """List of commands specified"""
        cmds = ['a', 'b', 'c']
        s = runscript(commands=cmds)
        self.assertEqual(str(s), 'ENTRYPOINT ["a"]')

    @singularity
    def test_multiple_singularity(self):
        """List of commands specified"""
        cmds = ['a arga', 'b argb', 'c']
        s = runscript(commands=cmds)
        self.assertEqual(str(s), '%runscript\n    a arga\n    b argb\n    exec c')

    @singularity
    def test_apprun_multiple_singularity(self):
        """List of commands specified"""
        cmds = ['a', 'b', 'c']
        s = runscript(commands=cmds, _app='foo')
        self.assertEqual(str(s), '%apprun foo\n    a\n    b\n    exec c')

    @docker
    def test_apprun_docker(self):
        """apprun not implemented in Docker"""
        cmds = ['a', 'b', 'c']
        s = runscript(commands=cmds, _app='foo')
        self.assertEqual(str(s), 'ENTRYPOINT ["a"]')

    @singularity
    def test_multiple_noexec_singularity(self):
        """exec option"""
        cmds = ['a', 'b', 'c']
        s = runscript(commands=cmds, _exec=False)
        self.assertEqual(str(s), '%runscript\n    a\n    b\n    c')

    @docker
    def test_merge_docker(self):
        """merge primitives"""
        r = []
        r.append(runscript(commands=['a', 'b']))
        r.append(runscript(commands=['c']))
        merged = r[0].merge(r)
        self.assertEqual(str(merged), 'ENTRYPOINT ["a"]')

    @singularity
    def test_merge_singularity(self):
        """merge primitives"""
        r = []
        r.append(runscript(commands=['a', 'b']))
        r.append(runscript(commands=['c']))
        merged = r[0].merge(r)
        self.assertEqual(str(merged), '%runscript\n    a\n    b\n    exec c')

    @bash
    def test_bash(self):
        """Single command specified"""
        cmd = ['z']
        s = runscript(commands=cmd)
        self.assertEqual(str(s), '')
