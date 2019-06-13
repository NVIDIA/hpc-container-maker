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

from helpers import bash, docker, invalid_ctype, singularity, singularity26, singularity32

from hpccm.primitives.copy import copy

class Test_copy(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @docker
    def test_empty(self):
        """No source or destination specified"""
        c = copy()
        self.assertEqual(str(c), '')

    @invalid_ctype
    def test_invalid_ctype(self):
        """Invalid container type specified"""
        c = copy(src='a', dest='b')
        with self.assertRaises(RuntimeError):
            str(c)

    @docker
    def test_single_docker(self):
        """Single source file specified"""
        c = copy(src='a', dest='b')
        self.assertEqual(str(c), 'COPY a b')

    @singularity
    def test_single_singularity(self):
        """Single source file specified"""
        c = copy(src='a', dest='b')
        self.assertEqual(str(c), '%files\n    a b')

    @bash
    def test_single_bash(self):
        """Single source file specified"""
        c = copy(src='a', dest='b')
        self.assertEqual(str(c), '')

    @docker
    def test_multiple_docker(self):
        """Multiple source files specified"""
        c = copy(src=['a1', 'a2', 'a3'], dest='b')
        self.assertEqual(str(c), 'COPY a1 \\\n    a2 \\\n    a3 \\\n    b/')

    @singularity
    def test_multiple_singularity(self):
        """Multiple source files specified"""
        c = copy(src=['a1', 'a2', 'a3'], dest='b')
        self.assertEqual(str(c), '%files\n    a1 b\n    a2 b\n    a3 b')

    @docker
    def test_files_docker(self):
        """Pairs of files specified"""
        c = copy(files={'a1': 'b1', 'a2': 'b2', 'a3': 'b3'})
        self.assertEqual(str(c), 'COPY a1 b1\nCOPY a2 b2\nCOPY a3 b3')

    @singularity
    def test_files_singularity(self):
        """Pairs of files specified"""
        c = copy(files={'a1': 'b1', 'a2': 'b2', 'a3': 'b3'})
        self.assertEqual(str(c), '%files\n    a1 b1\n    a2 b2\n    a3 b3')

    @docker
    def test_from_docker(self):
        """Docker --from syntax"""
        c = copy(src='a', dest='b', _from='dev')
        self.assertEqual(str(c), 'COPY --from=dev a b')

    @singularity26
    def test_from_singularity26(self):
        """Singularity from syntax"""
        c = copy(src='a', dest='b', _from='dev')
        self.assertEqual(str(c), '%files\n    a b')

    @singularity32
    def test_from_singularity32(self):
        """Singularity from syntax"""
        c = copy(src='a', dest='b', _from='dev')
        self.assertEqual(str(c), '%files from dev\n    a b')

    @singularity
    def test_appfiles_multiple_singularity(self):
        """Multiple app-specific source files specified"""
        c = copy(src=['a1', 'a2', 'a3'], dest='b', _app='foo')
        self.assertEqual(str(c),
                         '%appfiles foo\n    a1 b\n    a2 b\n    a3 b')

    @singularity
    def test_appfiles_files_singularity(self):
        """Pairs of app-specific files specified"""
        c = copy(files={'a1': 'b1', 'a2': 'b2', 'a3': 'b3'}, _app='foo')
        self.assertEqual(str(c),
                         '%appfiles foo\n    a1 b1\n    a2 b2\n    a3 b3')

    @docker
    def test_appfiles_docker(self):
        """app-parameter is ignored in Docker"""
        c = copy(src=['a1', 'a2', 'a3'], dest='b', _app='foo')
        self.assertEqual(str(c), 'COPY a1 \\\n    a2 \\\n    a3 \\\n    b/')

    @singularity
    def test_post_file_singularity(self):
        """Move file during post"""
        c = copy(src='a', dest='/opt/a', _post=True)
        self.assertEqual(str(c),
                         '%files\n    a /\n%post\n    mv /a /opt/a')

        c = copy(src='a', dest='/opt/', _post=True)
        self.assertEqual(str(c),
                         '%files\n    a /\n%post\n    mv /a /opt/')

    @singularity
    def test_post_multiple_singularity(self):
        """move file during post"""
        c = copy(src=['a', 'b'], dest='/opt', _post=True)
        self.assertEqual(str(c),
                         '%files\n    a /\n    b /\n%post\n    mv /a /opt/a\n    mv /b /opt/b')

    @singularity
    def test_mkdir_file_singularity(self):
        """mkdir folder with setup, single file"""
        c = copy(src='a', dest='/opt/foo/a', _mkdir=True)
        self.assertEqual(str(c),
                         '%setup\n    mkdir -p ${SINGULARITY_ROOTFS}/opt/foo\n%files\n    a /opt/foo/a')

    @singularity
    def test_mkdir_files_singularity(self):
        """mkdir folder with setup, multiple files"""
        c = copy(src=['a', 'b'], dest='/opt/foo', _mkdir=True)
        self.assertEqual(str(c),
                         '%setup\n    mkdir -p ${SINGULARITY_ROOTFS}/opt/foo\n%files\n    a /opt/foo\n    b /opt/foo')

    @docker
    def test_merge_file_docker(self):
        """merge primitives"""
        c = []
        c.append(copy(src='a', dest='A'))
        c.append(copy(src='b', dest='B'))

        merged = c[0].merge(c)
        self.assertEqual(str(merged), 'COPY a A\nCOPY b B')

    @singularity
    def test_merge_file_singularity(self):
        """merge primitives"""
        c = []
        c.append(copy(src='a', dest='A'))
        c.append(copy(src='b', dest='B'))

        merged = c[0].merge(c)
        self.assertEqual(str(merged), '%files\n    a A\n    b B')

    @docker
    def test_merge_multiple_docker(self):
        """merge primitives"""
        c = []
        c.append(copy(src=['a1', 'a2'], dest='A'))
        c.append(copy(src='b', dest='B'))

        merged = c[0].merge(c)
        self.assertEqual(str(merged), 'COPY a1 A\nCOPY a2 A\nCOPY b B')

    @singularity
    def test_merge_multiple_singularity(self):
        """merge primitives"""
        c = []
        c.append(copy(src=['a1', 'a2'], dest='A'))
        c.append(copy(src='b', dest='B'))

        merged = c[0].merge(c)
        self.assertEqual(str(merged), '%files\n    a1 A\n    a2 A\n    b B')

    @docker
    def test_merge_mixed_docker(self):
        """merge primitives"""
        c = []
        c.append(copy(src='foo', dest='bar'))
        c.append(copy(src=['1', '2', '3'], dest='/infinity'))
        c.append(copy(files={'a': '/A', 'b': '/B'}))

        merged = c[0].merge(c)
        self.assertEqual(str(merged),
r'''COPY 1 /infinity
COPY 2 /infinity
COPY 3 /infinity
COPY a /A
COPY b /B
COPY foo bar''')

    @singularity
    def test_merge_mixed_singularity(self):
        """merge primitives"""
        c = []
        c.append(copy(src='foo', dest='bar'))
        c.append(copy(src=['1', '2', '3'], dest='/infinity'))
        c.append(copy(files={'a': '/A', 'b': '/B'}))

        merged = c[0].merge(c)
        self.assertEqual(str(merged),
r'''%files
    1 /infinity
    2 /infinity
    3 /infinity
    a /A
    b /B
    foo bar''')

    @docker
    def test_chown_docker(self):
        """Docker --chown syntax"""
        c = copy(_chown='alice:alice', src='foo', dest='bar')
        self.assertEqual(str(c), 'COPY --chown=alice:alice foo bar')

    @singularity
    def test_chown_singularity(self):
        """Docker --chown syntax"""
        c = copy(_chown='alice:alice', src='foo', dest='bar')
        self.assertEqual(str(c), '%files\n    foo bar')
