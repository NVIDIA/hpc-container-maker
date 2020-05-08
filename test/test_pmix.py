# Copyright (c) 2019, NVIDIA CORPORATION.  All rights reserved.
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

"""Test cases for the pmix module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import centos, docker, ubuntu, x86_64

from hpccm.building_blocks.pmix import pmix

class Test_pmix(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @x86_64
    @ubuntu
    @docker
    def test_defaults_ubuntu(self):
        """Default pmix building block"""
        p = pmix()
        self.assertEqual(str(p),
r'''# PMIX version 3.1.4
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        file \
        hwloc \
        libevent-dev \
        make \
        tar \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/openpmix/openpmix/releases/download/v3.1.4/pmix-3.1.4.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/pmix-3.1.4.tar.gz -C /var/tmp -z && \
    cd /var/tmp/pmix-3.1.4 &&   ./configure --prefix=/usr/local/pmix && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/pmix-3.1.4 /var/tmp/pmix-3.1.4.tar.gz
ENV CPATH=/usr/local/pmix/include:$CPATH \
    LD_LIBRARY_PATH=/usr/local/pmix/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/pmix/bin:$PATH''')

    @x86_64
    @centos
    @docker
    def test_ldconfig(self):
        """ldconfig option"""
        p = pmix(ldconfig=True, version='3.1.4')
        self.assertEqual(str(p),
r'''# PMIX version 3.1.4
RUN yum install -y \
        file \
        hwloc \
        libevent-devel \
        make \
        tar \
        wget && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/openpmix/openpmix/releases/download/v3.1.4/pmix-3.1.4.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/pmix-3.1.4.tar.gz -C /var/tmp -z && \
    cd /var/tmp/pmix-3.1.4 &&   ./configure --prefix=/usr/local/pmix && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    echo "/usr/local/pmix/lib" >> /etc/ld.so.conf.d/hpccm.conf && ldconfig && \
    rm -rf /var/tmp/pmix-3.1.4 /var/tmp/pmix-3.1.4.tar.gz
ENV CPATH=/usr/local/pmix/include:$CPATH \
    PATH=/usr/local/pmix/bin:$PATH''')

    @x86_64
    @ubuntu
    @docker
    def test_runtime(self):
        """Runtime"""
        p = pmix()
        r = p.runtime()
        self.assertEqual(r,
r'''# PMIX
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libevent-2.* \
        libevent-pthreads-2.* && \
    rm -rf /var/lib/apt/lists/*
COPY --from=0 /usr/local/pmix /usr/local/pmix
ENV CPATH=/usr/local/pmix/include:$CPATH \
    LD_LIBRARY_PATH=/usr/local/pmix/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/pmix/bin:$PATH''')
