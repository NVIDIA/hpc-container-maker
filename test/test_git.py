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

from hpccm.git import git

class Test_wget(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    def test_missing_repo(self):
        """Missing repository option"""
        g = git()
        self.assertEqual(g.clone_step(), '')

    def test_basic(self):
        """Basic wget"""
        g = git()
        self.assertEqual(g.clone_step(repository='https://github.com/NVIDIA/hpc-container-maker.git'),
                         'mkdir -p /tmp && git -C /tmp clone --depth=1 https://github.com/NVIDIA/hpc-container-maker.git')

    def test_branch(self):
        """git with specified branch"""
        g = git()
        self.assertEqual(g.clone_step(repository='https://github.com/NVIDIA/hpc-container-maker.git',
                                      branch='master'),
                         'mkdir -p /tmp && git -C /tmp clone --depth=1 --branch master https://github.com/NVIDIA/hpc-container-maker.git')

    def test_directory(self):
        """git with non-default base directory"""
        g = git()
        self.assertEqual(g.clone_step(repository='https://github.com/NVIDIA/hpc-container-maker.git',
                                      directory='/scratch'),
                         'mkdir -p /scratch && git -C /scratch clone --depth=1 https://github.com/NVIDIA/hpc-container-maker.git')

    def test_opts(self):
        """git with non-default command line options"""
        g = git(opts=['--single-branch'])
        self.assertEqual(g.clone_step(repository='https://github.com/NVIDIA/hpc-container-maker.git'),
                         'mkdir -p /tmp && git -C /tmp clone --single-branch https://github.com/NVIDIA/hpc-container-maker.git')
