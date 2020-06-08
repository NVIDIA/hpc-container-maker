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

"""Test cases for the tar module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from hpccm.templates.tar import tar

class Test_tar(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    def test_missing_tarball(self):
        """Missing tarball option"""
        t = tar()
        self.assertEqual(t.untar_step(), '')

    def test_filetypes(self):
        t = tar()

        self.assertEqual(t.untar_step(tarball='foo.tar.bz2'),
                         'tar -x -f foo.tar.bz2 -j')

        self.assertEqual(t.untar_step(tarball='foo.tar.gz'),
                         'tar -x -f foo.tar.gz -z')

        self.assertEqual(t.untar_step(tarball='foo.tar.xz'),
                         'tar -x -f foo.tar.xz -J')

        self.assertEqual(t.untar_step(tarball='foo.txz'),
                         'tar -x -f foo.txz -J')

        self.assertEqual(t.untar_step(tarball='foo.tgz'),
                         'tar -x -f foo.tgz -z')

        self.assertEqual(t.untar_step(tarball='foo.tar'),
                         'tar -x -f foo.tar')

        self.assertEqual(t.untar_step(tarball='foo.unknown'),
                         'tar -x -f foo.unknown')

    def test_directory(self):
        """Directory specified"""
        t = tar()
        self.assertEqual(t.untar_step(tarball='foo.tgz', directory='bar'),
                         'mkdir -p bar && tar -x -f foo.tgz -C bar -z')

    def test_args(self):
        """Argument given"""
        t = tar()
        self.assertEqual(t.untar_step(tarball="foo.tar.gz",
                                      args=["--strip-components=1"]),
                         'tar -x -f foo.tar.gz -z --strip-components=1')
