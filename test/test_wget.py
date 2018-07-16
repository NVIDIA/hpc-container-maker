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

"""Test cases for the wget module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from hpccm.templates.wget import wget

class Test_wget(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    def test_missing_url(self):
        """Missing url option"""
        w = wget()
        self.assertEqual(w.download_step(), '')

    def test_basic(self):
        """Basic wget"""
        w = wget()
        self.assertEqual(w.download_step(url='http://mysite.com/foo.tgz'),
                         'mkdir -p /tmp && wget -q -nc --no-check-certificate -P /tmp http://mysite.com/foo.tgz')

    def test_referer(self):
        """wget with referer"""
        w = wget()
        self.assertEqual(w.download_step(url='http://mysite.com/foo.tgz',
                                         referer='http://mysite.com/foo.html'),
                         'mkdir -p /tmp && wget -q -nc --no-check-certificate --referer http://mysite.com/foo.html -P /tmp http://mysite.com/foo.tgz')

    def test_directory(self):
        """wget with non-default output directory"""
        w = wget()
        self.assertEqual(w.download_step(url='http://mysite.com/foo.tgz',
                                         directory='/scratch'),
                         'mkdir -p /scratch && wget -q -nc --no-check-certificate -P /scratch http://mysite.com/foo.tgz')

    def test_outfile(self):
        """wget with non-default output file"""
        w = wget()
        self.assertEqual(w.download_step(url='http://mysite.com/foo.tgz',
                                         outfile='bar.tgz'),
                         'mkdir -p /tmp && wget -q -nc --no-check-certificate -O bar.tgz -P /tmp http://mysite.com/foo.tgz')

    def test_opts(self):
        """wget with non-default command line options"""
        w = wget(opts=['-fast'])
        self.assertEqual(w.download_step(url='http://mysite.com/foo.tgz'),
                         'mkdir -p /tmp && wget -fast -P /tmp http://mysite.com/foo.tgz')
