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

"""Test cases for the comment module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import docker, invalid_ctype, singularity

from hpccm.primitives.comment import comment

class Test_comment(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @docker
    def test_empty(self):
        """No comment string specified"""
        c = comment()
        self.assertEqual(str(c), '')

    @docker
    def test_empty_noreformat(self):
        """No comment string specified, reformatting disabled"""
        c = comment(reformat=False)
        self.assertEqual(str(c), '')

    @invalid_ctype
    def test_invalid_ctype(self):
        """Invalid container type specified
           Assumes default comment format."""
        c = comment('foo')
        self.assertEqual(str(c), '# foo')

    @docker
    def test_comment_docker(self):
        """Comment string specified"""
        c = comment('foo')
        self.assertEqual(str(c), '# foo')

    @singularity
    def test_comment_singularity(self):
        """Comment string specified"""
        c = comment('foo')
        self.assertEqual(str(c), '# foo')

    @docker
    def test_noreformat(self):
        """Disable reformatting"""
        c = comment('foo\nbar', reformat=False)
        self.assertEqual(str(c), '# foo\n# bar')

    @docker
    def test_wrap(self):
        """Comment wrapping"""
        c = comment('foo\nbar')
        self.assertEqual(str(c), '# foo bar')

    @docker
    def test_merge_docker(self):
        """Comment merge"""
        c = []
        c.append(comment('a'))
        c.append(comment('b'))
        merged = c[0].merge(c)
        self.assertEqual(str(merged), '# a\n# b')

    @singularity
    def test_merge_singularity(self):
        """Comment merge"""
        c = []
        c.append(comment('a'))
        c.append(comment('b'))
        merged = c[0].merge(c)
        self.assertEqual(str(merged), '# a\n# b')

        apphelp = c[0].merge(c, _app='foo')
        self.assertEqual(str(apphelp), '%apphelp foo\na\nb')
