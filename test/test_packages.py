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

"""Test cases for the packages module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import centos, docker, invalid_distro, ubuntu

from hpccm.building_blocks.packages import packages 

class Test_packages(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @ubuntu
    @docker
    def test_basic_ubuntu(self):
        """Basic packages"""
        p = packages(ospackages=['gcc', 'g++', 'gfortran'])
        self.assertEqual(str(p),
r'''RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        g++ \
        gcc \
        gfortran && \
    rm -rf /var/lib/apt/lists/*''')

    @centos
    @docker
    def test_basic_centos(self):
        """Basic packages"""
        p = packages(ospackages=['gcc', 'gcc-c++', 'gcc-fortran'])
        self.assertEqual(str(p),
r'''RUN yum install -y \
        gcc \
        gcc-c++ \
        gcc-fortran && \
    rm -rf /var/cache/yum/*''')

    @invalid_distro
    def test_invalid_distro(self):
        """Invalid package type specified"""
        with self.assertRaises(RuntimeError):
            packages(ospackages=['gcc', 'g++', 'gfortran'])
