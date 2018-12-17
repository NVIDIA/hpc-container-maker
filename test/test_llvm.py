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

"""Test cases for the llvm module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import centos, docker, ubuntu

from hpccm.building_blocks.llvm import llvm

class Test_llvm(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @ubuntu
    @docker
    def test_defaults_ubuntu(self):
        """Default llvm building block"""
        l = llvm()
        self.assertEqual(str(l),
r'''# LLVM compiler
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        clang && \
    rm -rf /var/lib/apt/lists/*''')

    @centos
    @docker
    def test_defaults_centos(self):
        """Default llvm building block"""
        l = llvm()
        self.assertEqual(str(l),
r'''# LLVM compiler
RUN yum install -y \
        gcc \
        gcc-c++ && \
    rm -rf /var/cache/yum/*
RUN yum install -y \
        clang && \
    rm -rf /var/cache/yum/*''')

    @ubuntu
    @docker
    def test_version_ubuntu(self):
        """LLVM compiler version"""
        l = llvm(extra_repository=True, version='6.0')
        self.assertEqual(str(l),
r'''# LLVM compiler
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        clang-6.0 && \
    rm -rf /var/lib/apt/lists/*
RUN update-alternatives --install /usr/bin/clang clang $(which clang-6.0) 30 && \
    update-alternatives --install /usr/bin/clang++ clang++ $(which clang++-6.0) 30''')

    @centos
    @docker
    def test_version_centos(self):
        """LLVM compiler version"""
        l = llvm(extra_repository=True, version='7')
        self.assertEqual(str(l),
r'''# LLVM compiler
RUN yum install -y \
        gcc \
        gcc-c++ && \
    rm -rf /var/cache/yum/*
RUN yum install -y centos-release-scl && \
    yum install -y \
        llvm-toolset-7-clang && \
    rm -rf /var/cache/yum/*
ENV LD_LIBRARY_PATH=/opt/rh/llvm-toolset-7/root/usr/lib64:$LD_LIBRARY_PATH \
    PATH=/opt/rh/llvm-toolset-7/root/usr/bin:$PATH''')

    @ubuntu
    @docker
    def test_runtime(self):
        """Runtime"""
        l = llvm()
        r = l.runtime()
        self.assertEqual(r,
r'''# LLVM compiler runtime
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libclang1 && \
    rm -rf /var/lib/apt/lists/*''')

    def test_toolchain(self):
        """Toolchain"""
        l = llvm()
        tc = l.toolchain
        self.assertEqual(tc.CC, 'clang')
        self.assertEqual(tc.CXX, 'clang++')
