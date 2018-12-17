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

# pylint: disable=invalid-name, too-few-public-methods, bad-continuation

"""Test cases for the gnu module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import centos, docker, ubuntu

from hpccm.building_blocks.gnu import gnu

class Test_gnu(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @ubuntu
    @docker
    def test_defaults_ubuntu(self):
        """Default gnu building block"""
        g = gnu()
        self.assertEqual(str(g),
r'''# GNU compiler
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        gfortran && \
    rm -rf /var/lib/apt/lists/*''')

    @centos
    @docker
    def test_defaults_centos(self):
        """Default gnu building block"""
        g = gnu()
        self.assertEqual(str(g),
r'''# GNU compiler
RUN yum install -y \
        gcc \
        gcc-c++ \
        gcc-gfortran && \
    rm -rf /var/cache/yum/*''')

    @ubuntu
    @docker
    def test_version_ubuntu(self):
        """GNU compiler version"""
        g = gnu(extra_repository=True, version='7')
        self.assertEqual(str(g),
r'''# GNU compiler
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends software-properties-common && \
    apt-add-repository ppa:ubuntu-toolchain-r/test -y && \
    apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        gcc-7 \
        g++-7 \
        gfortran-7 && \
    rm -rf /var/lib/apt/lists/*
RUN update-alternatives --install /usr/bin/gcc gcc $(which gcc-7) 30 && \
    update-alternatives --install /usr/bin/g++ g++ $(which g++-7) 30 && \
    update-alternatives --install /usr/bin/gfortran gfortran $(which gfortran-7) 30''')

    @centos
    @docker
    def test_version_centos(self):
        """GNU compiler version"""
        g = gnu(extra_repository=True, version='7')
        self.assertEqual(str(g),
r'''# GNU compiler
RUN yum install -y centos-release-scl && \
    yum install -y \
        devtoolset-7-gcc \
        devtoolset-7-gcc-c++ \
        devtoolset-7-gcc-gfortran && \
    rm -rf /var/cache/yum/*
ENV PATH=/opt/rh/devtoolset-7/root/usr/bin:$PATH''')

    @ubuntu
    @docker
    def test_runtime(self):
        """Runtime"""
        g = gnu()
        r = g.runtime()
        self.assertEqual(r,
r'''# GNU compiler runtime
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libgomp1 \
        libgfortran3 && \
    rm -rf /var/lib/apt/lists/*''')

    def test_toolchain(self):
        """Toolchain"""
        g = gnu()
        tc = g.toolchain
        self.assertEqual(tc.CC, 'gcc')
        self.assertEqual(tc.CXX, 'g++')
        self.assertEqual(tc.FC, 'gfortran')
        self.assertEqual(tc.F77, 'gfortran')
        self.assertEqual(tc.F90, 'gfortran')
