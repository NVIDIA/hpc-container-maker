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

from helpers import aarch64, centos, centos8, docker, ppc64le, ubuntu, ubuntu18, ubuntu20, x86_64, zen2

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
        clang \
        libomp \
        llvm-libs && \
    rm -rf /var/cache/yum/*
ENV CPATH=/usr/lib/gcc/x86_64-redhat-linux/8/include:$CPATH''')

    @x86_64
    @ubuntu
    @docker
    def test_version_ubuntu(self):
        """LLVM compiler version"""
        l = llvm(extra_tools=True, version='6.0')
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
        l = llvm(extra_tools=True, version='7')
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
    def test_openmp_ubuntu(self):
        """openmp disabled"""
        l = llvm(openmp=False)
        self.assertEqual(str(l),
r'''# LLVM compiler
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        clang && \
    rm -rf /var/lib/apt/lists/*''')

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
    @ubuntu
    @docker
    def test_toolset8_ubuntu(self):
        """full toolset"""
        l = llvm(toolset=True, version='8')
        self.assertEqual(str(l),
r'''# LLVM compiler
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        clang-8 \
        clang-format-8 \
        clang-tidy-8 \
        clang-tools-8 \
        libc++-8-dev \
        libc++1-8 \
        libc++abi1-8 \
        libclang-8-dev \
        libclang1-8 \
        liblldb-8-dev \
        libomp-8-dev \
        lld-8 \
        lldb-8 \
        llvm-8 \
        llvm-8-dev \
        llvm-8-runtime && \
    rm -rf /var/lib/apt/lists/*
RUN update-alternatives --install /usr/bin/clang clang $(which clang-8) 30 && \
    update-alternatives --install /usr/bin/clang++ clang++ $(which clang++-8) 30 && \
    update-alternatives --install /usr/bin/clang-format clang-format $(which clang-format-8) 30 && \
    update-alternatives --install /usr/bin/clang-tidy clang-tidy $(which clang-tidy-8) 30 && \
    update-alternatives --install /usr/bin/lldb lldb $(which lldb-8) 30 && \
    update-alternatives --install /usr/bin/llvm-config llvm-config $(which llvm-config-8) 30 && \
    update-alternatives --install /usr/bin/llvm-cov llvm-cov $(which llvm-cov-8) 30''')

    @x86_64
    @ubuntu18
    @docker
    def test_toolset_ubuntu18(self):
        """full toolset"""
        l = llvm(toolset=True)
        self.assertEqual(str(l),
r'''# LLVM compiler
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        clang \
        clang-format \
        clang-tidy \
        libc++-dev \
        libc++1 \
        libc++abi1 \
        libclang-dev \
        libclang1 \
        libomp-dev \
        lldb \
        llvm \
        llvm-dev \
        llvm-runtime && \
    rm -rf /var/lib/apt/lists/*''')

    @x86_64
    @centos
    @docker
    def test_toolset_centos7(self):
        """full toolset"""
        l = llvm(toolset=True)
        self.assertEqual(str(l),
r'''# LLVM compiler
RUN yum install -y \
        gcc \
        gcc-c++ && \
    rm -rf /var/cache/yum/*
RUN yum install -y \
        clang \
        llvm && \
    rm -rf /var/cache/yum/*
ENV CPATH=/usr/lib/gcc/x86_64-redhat-linux/4.8.2/include:$CPATH''')

    @x86_64
    @centos8
    @docker
    def test_toolset_centos8(self):
        """full toolset"""
        l = llvm(toolset=True)
        self.assertEqual(str(l),
r'''# LLVM compiler
RUN yum install -y \
        gcc \
        gcc-c++ && \
    rm -rf /var/cache/yum/*
RUN yum install -y \
        clang \
        clang-tools-extra \
        llvm-toolset && \
    rm -rf /var/cache/yum/*
ENV CPATH=/usr/lib/gcc/x86_64-redhat-linux/8/include:$CPATH''')

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
        clang \
        clang-tools-extra \
        libomp \
        llvm-libs && \
    rm -rf /var/cache/yum/*
ENV CPATH=/usr/lib/gcc/x86_64-redhat-linux/8/include:$CPATH''')

    @x86_64
    @ubuntu
    @docker
    def test_upstream_ubuntu16(self):
        """Upstream builds"""
        l = llvm(upstream=True, version='10')
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
    def test_upstream_ubuntu18(self):
        """Upstream builds"""
        l = llvm(extra_tools=True, upstream=True)
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
        clang-15 \
        clang-format-15 \
        clang-tidy-15 \
        libomp-15-dev && \
    rm -rf /var/lib/apt/lists/*
RUN update-alternatives --install /usr/bin/clang clang $(which clang-15) 30 && \
    update-alternatives --install /usr/bin/clang++ clang++ $(which clang++-15) 30 && \
    update-alternatives --install /usr/bin/clang-format clang-format $(which clang-format-15) 30 && \
    update-alternatives --install /usr/bin/clang-tidy clang-tidy $(which clang-tidy-15) 30''')

    @x86_64
    @ubuntu20
    @docker
    def test_upstream_ubuntu20(self):
        """Upstream builds"""
        l = llvm(extra_tools=True, upstream=True)
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
    echo "deb http://apt.llvm.org/focal/ llvm-toolchain-focal main" >> /etc/apt/sources.list.d/hpccm.list && \
    echo "deb-src http://apt.llvm.org/focal/ llvm-toolchain-focal main" >> /etc/apt/sources.list.d/hpccm.list && \
    apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        clang-15 \
        clang-format-15 \
        clang-tidy-15 \
        libomp-15-dev && \
    rm -rf /var/lib/apt/lists/*
RUN update-alternatives --install /usr/bin/clang clang $(which clang-15) 30 && \
    update-alternatives --install /usr/bin/clang++ clang++ $(which clang++-15) 30 && \
    update-alternatives --install /usr/bin/clang-format clang-format $(which clang-format-15) 30 && \
    update-alternatives --install /usr/bin/clang-tidy clang-tidy $(which clang-tidy-15) 30''')

    @aarch64
    @ubuntu
    @docker
    def test_upstream_aarch64(self):
        """Upstream builds for aarch64"""
        l = llvm(upstream=True, version='11')
        self.assertMultiLineEqual(str(l),
r'''# LLVM compiler
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        apt-transport-https \
        ca-certificates \
        gnupg \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN wget -qO - https://apt.llvm.org/llvm-snapshot.gpg.key | apt-key add - && \
    echo "deb http://apt.llvm.org/xenial/ llvm-toolchain-xenial-11 main" >> /etc/apt/sources.list.d/hpccm.list && \
    echo "deb-src http://apt.llvm.org/xenial/ llvm-toolchain-xenial-11 main" >> /etc/apt/sources.list.d/hpccm.list && \
    apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        clang-11 \
        libomp-11-dev && \
    rm -rf /var/lib/apt/lists/*
RUN update-alternatives --install /usr/bin/clang clang $(which clang-11) 30 && \
    update-alternatives --install /usr/bin/clang++ clang++ $(which clang++-11) 30''')

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

    @zen2
    def test_toolchain_zen2(self):
        """CPU arch optimization flags"""
        l = llvm()
        tc = l.toolchain
        self.assertEqual(tc.CFLAGS, '-march=znver2 -mtune=znver2')
        self.assertEqual(tc.CXXFLAGS, '-march=znver2 -mtune=znver2')
