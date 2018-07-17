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

"""Test cases for the yum module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import centos, docker

from hpccm.building_blocks.yum import yum

class Test_yum(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @centos
    @docker
    def test_basic(self):
        """Basic yum"""
        y = yum(ospackages=['gcc', 'gcc-c++', 'gcc-fortran'])
        self.assertEqual(str(y),
r'''RUN yum install -y \
        gcc \
        gcc-c++ \
        gcc-fortran && \
    rm -rf /var/cache/yum/*''')

    @centos
    @docker
    def test_add_repo(self):
        """Add repo and key"""
        y = yum(keys=['https://www.example.com/key.pub'],
                ospackages=['example'],
                repositories=['http://www.example.com/example.repo'])
        self.assertEqual(str(y),
r'''RUN rpm --import https://www.example.com/key.pub && \
    yum-config-manager --add-repo http://www.example.com/example.repo && \
    yum install -y \
        example && \
    rm -rf /var/cache/yum/*''')
