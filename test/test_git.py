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

"""Test cases for the git module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from hpccm.templates.git import git

class Test_git(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    def test_missing_repo(self):
        """Missing repository option"""
        g = git()
        self.assertEqual(g.clone_step(), '')

    def test_basic(self):
        """Basic git"""
        g = git()
        self.assertEqual(g.clone_step(repository='https://github.com/NVIDIA/hpc-container-maker.git'),
                         'mkdir -p /tmp && cd /tmp && git clone --depth=1 https://github.com/NVIDIA/hpc-container-maker.git hpc-container-maker && cd -')

    def test_branch_recursive(self):
        """git with specified branch and recursive"""
        g = git()
        self.assertEqual(g.clone_step(repository='https://github.com/NVIDIA/hpc-container-maker.git',
                                      branch='master',
                                      recursive=True),
                         'mkdir -p /tmp && cd /tmp && git clone --depth=1 --branch master --recursive https://github.com/NVIDIA/hpc-container-maker.git hpc-container-maker && cd -')

    def test_commit(self):
        """git with specified commit"""
        g = git()
        self.assertEqual(g.clone_step(repository='https://github.com/NVIDIA/hpc-container-maker.git',
                                      commit='ac6ca95d0b20ed1efaffa6d58945a4dd2d80780c'),
                         'mkdir -p /tmp && cd /tmp && git clone  https://github.com/NVIDIA/hpc-container-maker.git hpc-container-maker && cd - && cd /tmp/hpc-container-maker && git checkout ac6ca95d0b20ed1efaffa6d58945a4dd2d80780c && cd -')
        self.assertEqual(g.clone_step(repository='https://github.com/NVIDIA/hpc-container-maker.git',
                                      commit='ac6ca95d0b20ed1efaffa6d58945a4dd2d80780c',
                                      verify='fatal'),
                         'mkdir -p /tmp && cd /tmp && git clone  https://github.com/NVIDIA/hpc-container-maker.git hpc-container-maker && cd - && cd /tmp/hpc-container-maker && git checkout ac6ca95d0b20ed1efaffa6d58945a4dd2d80780c && cd -')

    def test_branch_and_commit(self):
        """git with both specified branch and specified commit"""
        g = git()
        self.assertEqual(g.clone_step(repository='https://github.com/NVIDIA/hpc-container-maker.git',
                                      branch='master',
                                      commit='ac6ca95d0b20ed1efaffa6d58945a4dd2d80780c'),
                         'mkdir -p /tmp && cd /tmp && git clone  https://github.com/NVIDIA/hpc-container-maker.git hpc-container-maker && cd - && cd /tmp/hpc-container-maker && git checkout ac6ca95d0b20ed1efaffa6d58945a4dd2d80780c && cd -')

    def test_tag(self):
        """git with specified tag"""
        g = git()
        valid_tag='v20.5.0'
        invalid_tag='v-1.-2.-3'
        self.assertEqual(g.clone_step(repository='https://github.com/NVIDIA/hpc-container-maker.git',
                                      branch=valid_tag),
                         'mkdir -p /tmp && cd /tmp && git clone --depth=1 --branch v20.5.0 https://github.com/NVIDIA/hpc-container-maker.git hpc-container-maker && cd -')

        self.assertEqual(g.clone_step(repository='https://github.com/NVIDIA/hpc-container-maker.git',
                                      branch=invalid_tag),
                         'mkdir -p /tmp && cd /tmp && git clone --depth=1 --branch v-1.-2.-3 https://github.com/NVIDIA/hpc-container-maker.git hpc-container-maker && cd -')

        self.assertEqual(g.clone_step(repository='https://github.com/NVIDIA/hpc-container-maker.git',
                                      branch=valid_tag, verify='fatal'),
                         'mkdir -p /tmp && cd /tmp && git clone --depth=1 --branch v20.5.0 https://github.com/NVIDIA/hpc-container-maker.git hpc-container-maker && cd -')

        with self.assertRaises(RuntimeError):
            g.clone_step(repository='https://github.com/NVIDIA/hpc-container-maker.git',
                                      branch=invalid_tag, verify='fatal')

    def test_path(self):
        """git with non-default base path"""
        g = git()
        self.assertEqual(g.clone_step(repository='https://github.com/NVIDIA/hpc-container-maker.git',
                                      path='/scratch'),
                         'mkdir -p /scratch && cd /scratch && git clone --depth=1 https://github.com/NVIDIA/hpc-container-maker.git hpc-container-maker && cd -')

    def test_directory(self):
        """git with non-default directory to clone into"""
        g = git()
        self.assertEqual(g.clone_step(repository='https://github.com/NVIDIA/hpc-container-maker.git',
                                      directory='hpccm'),
                         'mkdir -p /tmp && cd /tmp && git clone --depth=1 https://github.com/NVIDIA/hpc-container-maker.git hpccm && cd -')

    def test_lfs(self):
        """Basic git"""
        g = git()
        self.assertEqual(g.clone_step(repository='https://github.com/NVIDIA/hpc-container-maker.git',
                                      lfs=True),
                         'mkdir -p /tmp && cd /tmp && git lfs clone --depth=1 https://github.com/NVIDIA/hpc-container-maker.git hpc-container-maker && cd -')

    def test_opts(self):
        """git with non-default command line options"""
        g = git(opts=['--single-branch'])
        self.assertEqual(g.clone_step(repository='https://github.com/NVIDIA/hpc-container-maker.git'),
                         'mkdir -p /tmp && cd /tmp && git clone --single-branch https://github.com/NVIDIA/hpc-container-maker.git hpc-container-maker && cd -')

    # This test will fail if git is not installed on the system
    def test_verify(self):
        """git with verification enabled"""
        g = git()
        repository = 'https://github.com/NVIDIA/hpc-container-maker.git'
        valid_branch = 'master'
        invalid_branch = 'does_not_exist'
        valid_commit = '23996b03b3e72f77a41498e94d90de920935644a'
        invalid_commit = 'deadbeef'

        self.assertEqual(g.clone_step(repository=repository,
                                      branch=valid_branch, verify=True),
                         'mkdir -p /tmp && cd /tmp && git clone --depth=1 --branch master https://github.com/NVIDIA/hpc-container-maker.git hpc-container-maker && cd -')

        self.assertEqual(g.clone_step(repository=repository,
                                      branch=invalid_branch, verify=True),
                         'mkdir -p /tmp && cd /tmp && git clone --depth=1 --branch does_not_exist https://github.com/NVIDIA/hpc-container-maker.git hpc-container-maker && cd -')

        self.assertEqual(g.clone_step(repository=repository,
                                      commit=valid_commit, verify=True),
                         'mkdir -p /tmp && cd /tmp && git clone  https://github.com/NVIDIA/hpc-container-maker.git hpc-container-maker && cd - && cd /tmp/hpc-container-maker && git checkout 23996b03b3e72f77a41498e94d90de920935644a && cd -')

        self.assertEqual(g.clone_step(repository=repository,
                                      commit=invalid_commit, verify=True),
                         'mkdir -p /tmp && cd /tmp && git clone  https://github.com/NVIDIA/hpc-container-maker.git hpc-container-maker && cd - && cd /tmp/hpc-container-maker && git checkout deadbeef && cd -')

        with self.assertRaises(RuntimeError):
            g.clone_step(repository=repository,
                         branch=invalid_branch, verify='fatal')
