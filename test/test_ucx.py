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

"""Test cases for the ucx module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import centos, docker, ubuntu

from hpccm.building_blocks.ucx import ucx

class Test_ucx(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @ubuntu
    @docker
    def test_defaults_ubuntu(self):
        """Default ucx building block"""
        u = ucx()
        self.assertEqual(str(u),
r'''# UCX version 1.4.0
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        binutils-dev \
        file \
        libnuma-dev \
        make \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/openucx/ucx/releases/download/v1.4.0/ucx-1.4.0.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/ucx-1.4.0.tar.gz -C /var/tmp -z && \
    cd /var/tmp/ucx-1.4.0 &&   ./configure --prefix=/usr/local/ucx --enable-optimizations --disable-logging --disable-debug --disable-assertions --disable-params-check --disable-doxygen-doc --with-cuda=/usr/local/cuda && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/ucx-1.4.0.tar.gz /var/tmp/ucx-1.4.0
ENV LD_LIBRARY_PATH=/usr/local/ucx/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/ucx/bin:$PATH''')

    @centos
    @docker
    def test_defaults_centos(self):
        """Default ucx building block"""
        u = ucx()
        self.assertEqual(str(u),
r'''# UCX version 1.4.0
RUN yum install -y \
        binutils-devel \
        file \
        make \
        numactl-devel \
        wget && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/openucx/ucx/releases/download/v1.4.0/ucx-1.4.0.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/ucx-1.4.0.tar.gz -C /var/tmp -z && \
    cd /var/tmp/ucx-1.4.0 &&   ./configure --prefix=/usr/local/ucx --enable-optimizations --disable-logging --disable-debug --disable-assertions --disable-params-check --disable-doxygen-doc --with-cuda=/usr/local/cuda && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/ucx-1.4.0.tar.gz /var/tmp/ucx-1.4.0
ENV LD_LIBRARY_PATH=/usr/local/ucx/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/ucx/bin:$PATH''')

    @ubuntu
    @docker
    def test_with_paths_ubuntu(self):
        """ucx building block with paths"""
        u = ucx(cuda='/cuda', gdrcopy='/gdrcopy', knem='/knem', xpmem='/xpmem')
        self.assertEqual(str(u),
r'''# UCX version 1.4.0
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        binutils-dev \
        file \
        libnuma-dev \
        make \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/openucx/ucx/releases/download/v1.4.0/ucx-1.4.0.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/ucx-1.4.0.tar.gz -C /var/tmp -z && \
    cd /var/tmp/ucx-1.4.0 &&   ./configure --prefix=/usr/local/ucx --enable-optimizations --disable-logging --disable-debug --disable-assertions --disable-params-check --disable-doxygen-doc --with-cuda=/cuda --with-gdrcopy=/gdrcopy --with-knem=/knem --with-xpmem=/xpmem && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/ucx-1.4.0.tar.gz /var/tmp/ucx-1.4.0
ENV LD_LIBRARY_PATH=/usr/local/ucx/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/ucx/bin:$PATH''')

    @ubuntu
    @docker
    def test_with_true_ubuntu(self):
        """ucx building block with True values"""
        u = ucx(cuda=True, gdrcopy=True, knem=True, xpmem=True)
        self.assertEqual(str(u),
r'''# UCX version 1.4.0
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        binutils-dev \
        file \
        libnuma-dev \
        make \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/openucx/ucx/releases/download/v1.4.0/ucx-1.4.0.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/ucx-1.4.0.tar.gz -C /var/tmp -z && \
    cd /var/tmp/ucx-1.4.0 &&   ./configure --prefix=/usr/local/ucx --enable-optimizations --disable-logging --disable-debug --disable-assertions --disable-params-check --disable-doxygen-doc --with-cuda=/usr/local/cuda --with-gdrcopy --with-knem --with-xpmem && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/ucx-1.4.0.tar.gz /var/tmp/ucx-1.4.0
ENV LD_LIBRARY_PATH=/usr/local/ucx/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/ucx/bin:$PATH''')

    @ubuntu
    @docker
    def test_with_false_ubuntu(self):
        """ucx building block with False values"""
        u = ucx(cuda=False, gdrcopy=False, knem=False, xpmem=False)
        self.assertEqual(str(u),
r'''# UCX version 1.4.0
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        binutils-dev \
        file \
        libnuma-dev \
        make \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/openucx/ucx/releases/download/v1.4.0/ucx-1.4.0.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/ucx-1.4.0.tar.gz -C /var/tmp -z && \
    cd /var/tmp/ucx-1.4.0 &&   ./configure --prefix=/usr/local/ucx --enable-optimizations --disable-logging --disable-debug --disable-assertions --disable-params-check --disable-doxygen-doc --without-cuda --without-gdrcopy --without-knem --without-xpmem && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/ucx-1.4.0.tar.gz /var/tmp/ucx-1.4.0
ENV LD_LIBRARY_PATH=/usr/local/ucx/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/ucx/bin:$PATH''')

    @ubuntu
    @docker
    def test_runtime(self):
        """Runtime"""
        u = ucx()
        r = u.runtime()
        self.assertEqual(r,
r'''# UCX
COPY --from=0 /usr/local/ucx /usr/local/ucx
ENV LD_LIBRARY_PATH=/usr/local/ucx/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/ucx/bin:$PATH''')
