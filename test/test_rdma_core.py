# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
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

"""Test cases for the rdma_core module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import centos, docker, ubuntu, x86_64

from hpccm.building_blocks.rdma_core import rdma_core

class Test_rdma_core(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @x86_64
    @ubuntu
    @docker
    def test_defaults_ubuntu(self):
        """Default rdma_core building block"""
        r = rdma_core()
        self.assertEqual(str(r),
r'''# RDMA Core version 31.2
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libnl-3-dev \
        libnl-route-3-dev \
        libudev-dev \
        make \
        pandoc \
        pkg-config \
        python3-docutils \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/linux-rdma/rdma-core/archive/v31.2.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/v31.2.tar.gz -C /var/tmp -z && \
    mkdir -p /var/tmp/rdma-core-31.2/build && cd /var/tmp/rdma-core-31.2/build && cmake -DCMAKE_INSTALL_PREFIX=/usr/local/rdma-core /var/tmp/rdma-core-31.2 && \
    cmake --build /var/tmp/rdma-core-31.2/build --target all -- -j$(nproc) && \
    cmake --build /var/tmp/rdma-core-31.2/build --target install -- -j$(nproc) && \
    rm -rf /var/tmp/rdma-core-31.2 /var/tmp/v31.2.tar.gz
ENV CPATH=/usr/local/rdma-core/include:$CPATH \
    LD_LIBRARY_PATH=/usr/local/rdma-core/lib:/usr/local/rdma-core/lib64:$LD_LIBRARY_PATH \
    LIBRARY_PATH=/usr/local/rdma-core/lib:/usr/local/rdma-core/lib64:$LIBRARY_PATH \
    PATH=/usr/local/rdma-core/bin:$PATH''')

    @x86_64
    @centos
    @docker
    def test_defaults_centos(self):
        """Default rdma_core building block"""
        r = rdma_core()
        self.assertEqual(str(r),
r'''# RDMA Core version 31.2
RUN yum install -y epel-release && \
    yum install -y \
        libnl3-devel \
        libudev-devel \
        make \
        pandoc \
        pkgconfig \
        python-docutils \
        wget && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/linux-rdma/rdma-core/archive/v31.2.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/v31.2.tar.gz -C /var/tmp -z && \
    mkdir -p /var/tmp/rdma-core-31.2/build && cd /var/tmp/rdma-core-31.2/build && cmake -DCMAKE_INSTALL_PREFIX=/usr/local/rdma-core /var/tmp/rdma-core-31.2 && \
    cmake --build /var/tmp/rdma-core-31.2/build --target all -- -j$(nproc) && \
    cmake --build /var/tmp/rdma-core-31.2/build --target install -- -j$(nproc) && \
    rm -rf /var/tmp/rdma-core-31.2 /var/tmp/v31.2.tar.gz
ENV CPATH=/usr/local/rdma-core/include:$CPATH \
    LD_LIBRARY_PATH=/usr/local/rdma-core/lib:/usr/local/rdma-core/lib64:$LD_LIBRARY_PATH \
    LIBRARY_PATH=/usr/local/rdma-core/lib:/usr/local/rdma-core/lib64:$LIBRARY_PATH \
    PATH=/usr/local/rdma-core/bin:$PATH''')

    @x86_64
    @ubuntu
    @docker
    def test_ldconfig(self):
        """ldconfig option"""
        r = rdma_core(ldconfig=True, version='31.2')
        self.assertEqual(str(r),
r'''# RDMA Core version 31.2
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libnl-3-dev \
        libnl-route-3-dev \
        libudev-dev \
        make \
        pandoc \
        pkg-config \
        python3-docutils \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/linux-rdma/rdma-core/archive/v31.2.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/v31.2.tar.gz -C /var/tmp -z && \
    mkdir -p /var/tmp/rdma-core-31.2/build && cd /var/tmp/rdma-core-31.2/build && cmake -DCMAKE_INSTALL_PREFIX=/usr/local/rdma-core /var/tmp/rdma-core-31.2 && \
    cmake --build /var/tmp/rdma-core-31.2/build --target all -- -j$(nproc) && \
    cmake --build /var/tmp/rdma-core-31.2/build --target install -- -j$(nproc) && \
    echo "/usr/local/rdma-core/lib" >> /etc/ld.so.conf.d/hpccm.conf && ldconfig && \
    rm -rf /var/tmp/rdma-core-31.2 /var/tmp/v31.2.tar.gz
ENV CPATH=/usr/local/rdma-core/include:$CPATH \
    LIBRARY_PATH=/usr/local/rdma-core/lib:/usr/local/rdma-core/lib64:$LIBRARY_PATH \
    PATH=/usr/local/rdma-core/bin:$PATH''')

    @x86_64
    @ubuntu
    @docker
    def test_git_repository_true(self):
        r = rdma_core(repository=True)
        self.assertEqual(str(r),
r'''# RDMA Core https://github.com/linux-rdma/rdma-core.git
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ca-certificates \
        git \
        libnl-3-dev \
        libnl-route-3-dev \
        libudev-dev \
        make \
        pandoc \
        pkg-config \
        python3-docutils \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && cd /var/tmp && git clone --depth=1 https://github.com/linux-rdma/rdma-core.git rdma-core && cd - && \
    mkdir -p /var/tmp/rdma-core/build && cd /var/tmp/rdma-core/build && cmake -DCMAKE_INSTALL_PREFIX=/usr/local/rdma-core /var/tmp/rdma-core && \
    cmake --build /var/tmp/rdma-core/build --target all -- -j$(nproc) && \
    cmake --build /var/tmp/rdma-core/build --target install -- -j$(nproc) && \
    rm -rf /var/tmp/rdma-core
ENV CPATH=/usr/local/rdma-core/include:$CPATH \
    LD_LIBRARY_PATH=/usr/local/rdma-core/lib:/usr/local/rdma-core/lib64:$LD_LIBRARY_PATH \
    LIBRARY_PATH=/usr/local/rdma-core/lib:/usr/local/rdma-core/lib64:$LIBRARY_PATH \
    PATH=/usr/local/rdma-core/bin:$PATH''')

    @ubuntu
    @docker
    def test_runtime(self):
        """Runtime"""
        r = rdma_core()
        r2 = r.runtime()
        self.assertEqual(r2,
r'''# RDMA Core
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libnl-3-200 \
        libnl-route-3-200 \
        libnuma1 && \
    rm -rf /var/lib/apt/lists/*
COPY --from=0 /usr/local/rdma-core /usr/local/rdma-core
ENV CPATH=/usr/local/rdma-core/include:$CPATH \
    LD_LIBRARY_PATH=/usr/local/rdma-core/lib:/usr/local/rdma-core/lib64:$LD_LIBRARY_PATH \
    LIBRARY_PATH=/usr/local/rdma-core/lib:/usr/local/rdma-core/lib64:$LIBRARY_PATH \
    PATH=/usr/local/rdma-core/bin:$PATH''')
