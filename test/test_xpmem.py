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

"""Test cases for the xpmem module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import centos, docker, ubuntu

from hpccm.building_blocks.xpmem import xpmem

class Test_xpmem(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @ubuntu
    @docker
    def test_defaults_ubuntu(self):
        """Default xpmem building block"""
        x = xpmem()
        self.assertEqual(str(x),
r'''# XPMEM branch master
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        autoconf \
        automake \
        ca-certificates \
        file \
        git \
        libtool \
        make && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && cd /var/tmp && git clone --depth=1 --branch master https://gitlab.com/hjelmn/xpmem.git xpmem && cd - && \
    cd /var/tmp/xpmem && \
    autoreconf --install && \
    cd /var/tmp/xpmem &&   ./configure --prefix=/usr/local/xpmem --disable-kernel-module && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/xpmem
ENV CPATH=/usr/local/xpmem/include:$CPATH \
    LD_LIBRARY_PATH=/usr/local/xpmem/lib:$LD_LIBRARY_PATH \
    LIBRARY_PATH=/usr/local/xpmem/lib:$LIBRARY_PATH''')

    @centos
    @docker
    def test_defaults_centos(self):
        """Default xpmem building block"""
        x = xpmem()
        self.assertEqual(str(x),
r'''# XPMEM branch master
RUN yum install -y \
        autoconf \
        automake \
        ca-certificates \
        file \
        git \
        libtool \
        make && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp && cd /var/tmp && git clone --depth=1 --branch master https://gitlab.com/hjelmn/xpmem.git xpmem && cd - && \
    cd /var/tmp/xpmem && \
    autoreconf --install && \
    cd /var/tmp/xpmem &&   ./configure --prefix=/usr/local/xpmem --disable-kernel-module && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/xpmem
ENV CPATH=/usr/local/xpmem/include:$CPATH \
    LD_LIBRARY_PATH=/usr/local/xpmem/lib:$LD_LIBRARY_PATH \
    LIBRARY_PATH=/usr/local/xpmem/lib:$LIBRARY_PATH''')

    @ubuntu
    @docker
    def test_ldconfig(self):
        """ldconfig option"""
        x = xpmem(ldconfig=True, branch='master')
        self.assertEqual(str(x),
r'''# XPMEM branch master
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        autoconf \
        automake \
        ca-certificates \
        file \
        git \
        libtool \
        make && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && cd /var/tmp && git clone --depth=1 --branch master https://gitlab.com/hjelmn/xpmem.git xpmem && cd - && \
    cd /var/tmp/xpmem && \
    autoreconf --install && \
    cd /var/tmp/xpmem &&   ./configure --prefix=/usr/local/xpmem --disable-kernel-module && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    echo "/usr/local/xpmem/lib" >> /etc/ld.so.conf.d/hpccm.conf && ldconfig && \
    rm -rf /var/tmp/xpmem
ENV CPATH=/usr/local/xpmem/include:$CPATH \
    LIBRARY_PATH=/usr/local/xpmem/lib:$LIBRARY_PATH''')

    @ubuntu
    @docker
    def test_runtime(self):
        """Runtime"""
        x = xpmem()
        r = x.runtime()
        self.assertEqual(r,
r'''# XPMEM
COPY --from=0 /usr/local/xpmem /usr/local/xpmem
ENV CPATH=/usr/local/xpmem/include:$CPATH \
    LD_LIBRARY_PATH=/usr/local/xpmem/lib:$LD_LIBRARY_PATH \
    LIBRARY_PATH=/usr/local/xpmem/lib:$LIBRARY_PATH''')
