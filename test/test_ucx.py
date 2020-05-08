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

from helpers import centos, docker, ppc64le, ubuntu, x86_64

from hpccm.building_blocks.ucx import ucx

class Test_ucx(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @x86_64
    @ubuntu
    @docker
    def test_defaults_ubuntu(self):
        """Default ucx building block"""
        u = ucx()
        self.assertEqual(str(u),
r'''# UCX version 1.8.0
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        binutils-dev \
        file \
        libnuma-dev \
        make \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/openucx/ucx/releases/download/v1.8.0/ucx-1.8.0.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/ucx-1.8.0.tar.gz -C /var/tmp -z && \
    cd /var/tmp/ucx-1.8.0 &&   ./configure --prefix=/usr/local/ucx --disable-assertions --disable-debug --disable-doxygen-doc --disable-logging --disable-params-check --enable-optimizations --with-cuda=/usr/local/cuda && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/ucx-1.8.0 /var/tmp/ucx-1.8.0.tar.gz
ENV LD_LIBRARY_PATH=/usr/local/ucx/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/ucx/bin:$PATH''')

    @x86_64
    @centos
    @docker
    def test_defaults_centos(self):
        """Default ucx building block"""
        u = ucx()
        self.assertEqual(str(u),
r'''# UCX version 1.8.0
RUN yum install -y \
        binutils-devel \
        file \
        make \
        numactl-devel \
        wget && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/openucx/ucx/releases/download/v1.8.0/ucx-1.8.0.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/ucx-1.8.0.tar.gz -C /var/tmp -z && \
    cd /var/tmp/ucx-1.8.0 &&   ./configure --prefix=/usr/local/ucx --disable-assertions --disable-debug --disable-doxygen-doc --disable-logging --disable-params-check --enable-optimizations --with-cuda=/usr/local/cuda && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/ucx-1.8.0 /var/tmp/ucx-1.8.0.tar.gz
ENV LD_LIBRARY_PATH=/usr/local/ucx/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/ucx/bin:$PATH''')

    @x86_64
    @ubuntu
    @docker
    def test_with_paths_ubuntu(self):
        """ucx building block with paths"""
        u = ucx(cuda='/cuda', gdrcopy='/gdrcopy', knem='/knem', ofed='/ofed',
                xpmem='/xpmem')
        self.assertEqual(str(u),
r'''# UCX version 1.8.0
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        binutils-dev \
        file \
        libnuma-dev \
        make \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/openucx/ucx/releases/download/v1.8.0/ucx-1.8.0.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/ucx-1.8.0.tar.gz -C /var/tmp -z && \
    cd /var/tmp/ucx-1.8.0 &&   ./configure --prefix=/usr/local/ucx --disable-assertions --disable-debug --disable-doxygen-doc --disable-logging --disable-params-check --enable-optimizations --with-cuda=/cuda --with-gdrcopy=/gdrcopy --with-knem=/knem --with-rdmacm=/ofed --with-verbs=/ofed --with-xpmem=/xpmem && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/ucx-1.8.0 /var/tmp/ucx-1.8.0.tar.gz
ENV LD_LIBRARY_PATH=/usr/local/ucx/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/ucx/bin:$PATH''')

    @x86_64
    @ubuntu
    @docker
    def test_with_true_ubuntu(self):
        """ucx building block with True values"""
        u = ucx(cuda=True, gdrcopy=True, knem=True, ofed=True, xpmem=True)
        self.assertEqual(str(u),
r'''# UCX version 1.8.0
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        binutils-dev \
        file \
        libnuma-dev \
        make \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/openucx/ucx/releases/download/v1.8.0/ucx-1.8.0.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/ucx-1.8.0.tar.gz -C /var/tmp -z && \
    cd /var/tmp/ucx-1.8.0 &&   ./configure --prefix=/usr/local/ucx --disable-assertions --disable-debug --disable-doxygen-doc --disable-logging --disable-params-check --enable-optimizations --with-cuda=/usr/local/cuda --with-gdrcopy --with-knem --with-rdmacm --with-verbs --with-xpmem && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/ucx-1.8.0 /var/tmp/ucx-1.8.0.tar.gz
ENV LD_LIBRARY_PATH=/usr/local/ucx/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/ucx/bin:$PATH''')

    @x86_64
    @ubuntu
    @docker
    def test_with_false_ubuntu(self):
        """ucx building block with False values"""
        u = ucx(cuda=False, gdrcopy=False, knem=False, ofed=False, xpmem=False)
        self.assertEqual(str(u),
r'''# UCX version 1.8.0
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        binutils-dev \
        file \
        libnuma-dev \
        make \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/openucx/ucx/releases/download/v1.8.0/ucx-1.8.0.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/ucx-1.8.0.tar.gz -C /var/tmp -z && \
    cd /var/tmp/ucx-1.8.0 &&   ./configure --prefix=/usr/local/ucx --disable-assertions --disable-debug --disable-doxygen-doc --disable-logging --disable-params-check --enable-optimizations --without-cuda --without-gdrcopy --without-knem --without-rdmacm --without-verbs --without-xpmem && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/ucx-1.8.0 /var/tmp/ucx-1.8.0.tar.gz
ENV LD_LIBRARY_PATH=/usr/local/ucx/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/ucx/bin:$PATH''')

    @x86_64
    @ubuntu
    @docker
    def test_ldconfig(self):
        """ldconfig option"""
        u = ucx(ldconfig=True, version='1.4.0')
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
    cd /var/tmp/ucx-1.4.0 &&   ./configure --prefix=/usr/local/ucx --disable-assertions --disable-debug --disable-doxygen-doc --disable-logging --disable-params-check --enable-optimizations --with-cuda=/usr/local/cuda && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    echo "/usr/local/ucx/lib" >> /etc/ld.so.conf.d/hpccm.conf && ldconfig && \
    rm -rf /var/tmp/ucx-1.4.0 /var/tmp/ucx-1.4.0.tar.gz
ENV PATH=/usr/local/ucx/bin:$PATH''')

    @x86_64
    @ubuntu
    @docker
    def test_environment(self):
        """environment option"""
        u = ucx(environment=False, version='1.4.0')
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
    cd /var/tmp/ucx-1.4.0 &&   ./configure --prefix=/usr/local/ucx --disable-assertions --disable-debug --disable-doxygen-doc --disable-logging --disable-params-check --enable-optimizations --with-cuda=/usr/local/cuda && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/ucx-1.4.0 /var/tmp/ucx-1.4.0.tar.gz''')

    @ppc64le
    @centos
    @docker
    def test_ppc64le(self):
        """ppc64le"""
        u = ucx(cuda=False, knem='/usr/local/knem', version='1.5.2')
        self.assertEqual(str(u),
r'''# UCX version 1.5.2
RUN yum install -y \
        binutils-devel \
        file \
        make \
        numactl-devel \
        wget && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/openucx/ucx/releases/download/v1.5.2/ucx-1.5.2.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/ucx-1.5.2.tar.gz -C /var/tmp -z && \
    cd /var/tmp/ucx-1.5.2 &&  CFLAGS=-Wno-error=format ./configure --prefix=/usr/local/ucx --disable-assertions --disable-debug --disable-doxygen-doc --disable-logging --disable-params-check --enable-optimizations --with-knem=/usr/local/knem --without-cuda && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/ucx-1.5.2 /var/tmp/ucx-1.5.2.tar.gz
ENV LD_LIBRARY_PATH=/usr/local/ucx/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/ucx/bin:$PATH''')

    @x86_64
    @ubuntu
    @docker
    def test_git_repository_true(self):
        u = ucx(repository=True)
        self.assertEqual(str(u),
r'''# UCX https://github.com/openucx/ucx.git
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        autoconf \
        automake \
        binutils-dev \
        ca-certificates \
        file \
        git \
        libnuma-dev \
        libtool \
        make \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && cd /var/tmp && git clone --depth=1 https://github.com/openucx/ucx.git ucx && cd - && \
    cd /var/tmp/ucx && \
    ./autogen.sh && \
    cd /var/tmp/ucx &&   ./configure --prefix=/usr/local/ucx --disable-assertions --disable-debug --disable-doxygen-doc --disable-logging --disable-params-check --enable-optimizations --with-cuda=/usr/local/cuda && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/ucx
ENV LD_LIBRARY_PATH=/usr/local/ucx/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/ucx/bin:$PATH''')

    @x86_64
    @ubuntu
    @docker
    def test_git_repository_value(self):
        u = ucx(branch='v1.8.x',
                repository='https://github.com/openucx-fork/ucx.git')
        self.assertEqual(str(u),
r'''# UCX https://github.com/openucx-fork/ucx.git v1.8.x
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        autoconf \
        automake \
        binutils-dev \
        ca-certificates \
        file \
        git \
        libnuma-dev \
        libtool \
        make \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && cd /var/tmp && git clone --depth=1 --branch v1.8.x https://github.com/openucx-fork/ucx.git ucx && cd - && \
    cd /var/tmp/ucx && \
    ./autogen.sh && \
    cd /var/tmp/ucx &&   ./configure --prefix=/usr/local/ucx --disable-assertions --disable-debug --disable-doxygen-doc --disable-logging --disable-params-check --enable-optimizations --with-cuda=/usr/local/cuda && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/ucx
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
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        binutils && \
    rm -rf /var/lib/apt/lists/*
COPY --from=0 /usr/local/ucx /usr/local/ucx
ENV LD_LIBRARY_PATH=/usr/local/ucx/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/ucx/bin:$PATH''')
