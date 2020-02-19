# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
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

"""Test cases for the downloader module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from hpccm.templates.downloader import downloader

class Test_downloader(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    def test_missing_url(self):
        """Missing url option"""
        d = downloader()
        with self.assertRaises(RuntimeError):
            d.download_step()

    def test_url_and_repository(self):
        """Both URL and repository specified"""
        d = downloader(repository='https://github.com/foo/bar',
                       url='http://mysite.com/foo.tgz')
        with self.assertRaises(RuntimeError):
            d.download_step()

    def test_basic_wget(self):
        """Basic wget"""
        d = downloader(url='http://mysite.com/foo.tgz')
        self.assertEqual(d.download_step(),
r'''mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp http://mysite.com/foo.tgz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/foo.tgz -C /var/tmp -z''')
        self.assertEqual(d.src_directory, '/var/tmp/foo')

    def test_bad_url(self):
        """Unrecognized package format"""
        d = downloader(url='http://mysite.com/foo.Z')
        with self.assertRaises(RuntimeError):
            d.download_step()

    def test_basic_git(self):
        """Basic git"""
        d = downloader(repository='https://github.com/foo/bar.git')
        self.assertEqual(d.download_step(),
r'''mkdir -p /var/tmp && cd /var/tmp && git clone --depth=1 https://github.com/foo/bar.git bar && cd -''')
        self.assertEqual(d.src_directory, '/var/tmp/bar')

    def test_git_recursive_branch(self):
        """Recursive clone of a branch"""
        d = downloader(branch='dev', repository='https://github.com/foo/bar')
        self.assertEqual(d.download_step(recursive=True),
r'''mkdir -p /var/tmp && cd /var/tmp && git clone --depth=1 --branch dev --recursive https://github.com/foo/bar bar && cd -''')

    def test_git_commit_wd(self):
        """Git commit into an alternative working directory"""
        d = downloader(commit='deadbeef',
                       repository='https://github.com/foo/bar')
        self.assertEqual(d.download_step(wd='/tmp/git'),
r'''mkdir -p /tmp/git && cd /tmp/git && git clone  https://github.com/foo/bar bar && cd - && cd /tmp/git/bar && git checkout deadbeef && cd -''')
        self.assertEqual(d.src_directory, '/tmp/git/bar')
