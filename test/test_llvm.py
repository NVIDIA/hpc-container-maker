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

from helpers import aarch64, centos, centos8, docker, ppc64le, ubuntu, ubuntu18, x86_64

from hpccm.building_blocks.llvm import llvm

class Test_llvm(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @x86_64
    @ubuntu
    @docker
    def test_defaults_ubuntu(self):
        """Default llvm building block"""
        l = llvm()
        self.assertEqual(str(l),
r'''# LLVM compiler
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        clang \
        libomp-dev && \
    rm -rf /var/lib/apt/lists/*''')

    @x86_64
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
    rm -rf /var/cache/yum/*
ENV CPATH=/usr/lib/gcc/x86_64-redhat-linux/4.8.2/include:$CPATH''')

    @x86_64
    @centos8
    @docker
    def test_defaults_centos8(self):
        """Default llvm building block"""
        l = llvm(version='8')
        self.assertEqual(str(l),
r'''# LLVM compiler
RUN yum install -y \
        gcc \
        gcc-c++ && \
    rm -rf /var/cache/yum/*
RUN yum install -y \
        llvm-toolset-8.0.1 && \
    rm -rf /var/cache/yum/*
ENV CPATH=/usr/lib/gcc/x86_64-redhat-linux/8/include:$CPATH''')

    @x86_64
    @ubuntu
    @docker
    def test_version_ubuntu(self):
        """LLVM compiler version"""
        l = llvm(extra_repository=True, extra_tools=True, version='6.0')
        self.assertEqual(str(l),
r'''# LLVM compiler
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        clang-6.0 \
        clang-format-6.0 \
        clang-tidy-6.0 \
        libomp-dev && \
    rm -rf /var/lib/apt/lists/*
RUN update-alternatives --install /usr/bin/clang clang $(which clang-6.0) 30 && \
    update-alternatives --install /usr/bin/clang++ clang++ $(which clang++-6.0) 30 && \
    update-alternatives --install /usr/bin/clang-format clang-format $(which clang-format-6.0) 30 && \
    update-alternatives --install /usr/bin/clang-tidy clang-tidy $(which clang-tidy-6.0) 30''')

    @x86_64
    @centos
    @docker
    def test_version_centos(self):
        """LLVM compiler version"""
        l = llvm(extra_repository=True, extra_tools=True, version='7')
        self.assertEqual(str(l),
r'''# LLVM compiler
RUN yum install -y \
        gcc \
        gcc-c++ && \
    rm -rf /var/cache/yum/*
RUN yum install -y centos-release-scl && \
    yum install -y \
        llvm-toolset-7-clang \
        llvm-toolset-7-clang-tools-extra \
        llvm-toolset-7-libomp-devel && \
    rm -rf /var/cache/yum/*
ENV CPATH=/usr/lib/gcc/x86_64-redhat-linux/4.8.2/include:$CPATH \
    LD_LIBRARY_PATH=/opt/rh/llvm-toolset-7/root/usr/lib64:$LD_LIBRARY_PATH \
    PATH=/opt/rh/llvm-toolset-7/root/usr/bin:$PATH''')

    @aarch64
    @centos
    @docker
    def test_aarch64_centos(self):
        """aarch64"""
        l = llvm()
        self.assertEqual(str(l),
r'''# LLVM compiler
RUN yum install -y \
        gcc \
        gcc-c++ && \
    rm -rf /var/cache/yum/*
RUN yum install -y \
        clang && \
    rm -rf /var/cache/yum/*
ENV COMPILER_PATH=/usr/lib/gcc/aarch64-redhat-linux/4.8.2:$COMPILER_PATH \
    CPATH=/usr/include/c++/4.8.2:/usr/include/c++/4.8.2/aarch64-redhat-linux:/usr/lib/gcc/aarch64-redhat-linux/4.8.2/include:$CPATH \
    LIBRARY_PATH=/usr/lib/gcc/aarch64-redhat-linux/4.8.2''')

    @aarch64
    @centos8
    @docker
    def test_aarch64_centos8(self):
        """aarch64"""
        l = llvm()
        self.assertEqual(str(l),
r'''# LLVM compiler
RUN yum install -y \
        gcc \
        gcc-c++ && \
    rm -rf /var/cache/yum/*
RUN yum install -y \
        clang && \
    rm -rf /var/cache/yum/*
ENV COMPILER_PATH=/usr/lib/gcc/aarch64-redhat-linux/8:$COMPILER_PATH \
    CPATH=/usr/include/c++/8:/usr/include/c++/8/aarch64-redhat-linux:/usr/lib/gcc/aarch64-redhat-linux/8/include:$CPATH \
    LIBRARY_PATH=/usr/lib/gcc/aarch64-redhat-linux/8''')

    @ppc64le
    @centos
    @docker
    def test_ppc64le_centos(self):
        """ppc64le"""
        with self.assertRaises(RuntimeError):
            llvm()

    @x86_64
    @ubuntu
    @docker
    def test_extra_tools_ubuntu(self):
        """clang-format and clang-tidy"""
        l = llvm(extra_tools=True)
        self.assertEqual(str(l),
r'''# LLVM compiler
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        clang \
        clang-format \
        clang-tidy \
        libomp-dev && \
    rm -rf /var/lib/apt/lists/*''')

    @x86_64
    @centos8
    @docker
    def test_extra_tools_centos8(self):
        """Default llvm building block"""
        l = llvm(extra_tools=True, version='8')
        self.assertEqual(str(l),
r'''# LLVM compiler
RUN yum install -y \
        gcc \
        gcc-c++ && \
    rm -rf /var/cache/yum/*
RUN yum install -y \
        clang-tools-extra-8.0.1 \
        llvm-toolset-8.0.1 && \
    rm -rf /var/cache/yum/*
ENV CPATH=/usr/lib/gcc/x86_64-redhat-linux/8/include:$CPATH''')

    @x86_64
    @ubuntu
    @docker
    def test_nightly_ubuntu16(self):
        """Nightly builds"""
        l = llvm(nightly=True, version='10')
        self.assertEqual(str(l),
r'''# LLVM compiler
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        apt-transport-https \
        ca-certificates \
        gnupg \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN wget -qO - https://apt.llvm.org/llvm-snapshot.gpg.key | apt-key add - && \
    echo "deb http://apt.llvm.org/xenial/ llvm-toolchain-xenial-10 main" >> /etc/apt/sources.list.d/hpccm.list && \
    echo "deb-src http://apt.llvm.org/xenial/ llvm-toolchain-xenial-10 main" >> /etc/apt/sources.list.d/hpccm.list && \
    apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        clang-10 \
        libomp-10-dev && \
    rm -rf /var/lib/apt/lists/*
RUN update-alternatives --install /usr/bin/clang clang $(which clang-10) 30 && \
    update-alternatives --install /usr/bin/clang++ clang++ $(which clang++-10) 30''')

    @x86_64
    @ubuntu18
    @docker
    def test_nightly_ubuntu18(self):
        """Nightly builds"""
        l = llvm(extra_tools=True, nightly=True, version='11')
        self.assertEqual(str(l),
r'''# LLVM compiler
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        apt-transport-https \
        ca-certificates \
        gnupg \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN wget -qO - https://apt.llvm.org/llvm-snapshot.gpg.key | apt-key add - && \
    echo "deb http://apt.llvm.org/bionic/ llvm-toolchain-bionic main" >> /etc/apt/sources.list.d/hpccm.list && \
    echo "deb-src http://apt.llvm.org/bionic/ llvm-toolchain-bionic main" >> /etc/apt/sources.list.d/hpccm.list && \
    apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        clang-11 \
        clang-format-11 \
        clang-tidy-11 \
        libomp-11-dev && \
    rm -rf /var/lib/apt/lists/*
RUN update-alternatives --install /usr/bin/clang clang $(which clang-11) 30 && \
    update-alternatives --install /usr/bin/clang++ clang++ $(which clang++-11) 30 && \
    update-alternatives --install /usr/bin/clang-format clang-format $(which clang-format-11) 30 && \
    update-alternatives --install /usr/bin/clang-tidy clang-tidy $(which clang-tidy-11) 30''')

    @aarch64
    @ubuntu
    @docker
    def test_nightly_aarch64(self):
        """Nightly builds for aarch64"""
        with self.assertRaises(RuntimeError):
            llvm(nightly=True, version='11')

    @x86_64
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
        libclang1 \
        libomp5 && \
    rm -rf /var/lib/apt/lists/*''')

    def test_toolchain(self):
        """Toolchain"""
        l = llvm()
        tc = l.toolchain
        self.assertEqual(tc.CC, 'clang')
        self.assertEqual(tc.CXX, 'clang++')
