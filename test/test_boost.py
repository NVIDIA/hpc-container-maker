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

"""Test cases for the boost module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import centos, docker, ubuntu

from hpccm.building_blocks.boost import boost

class Test_boost(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @ubuntu
    @docker
    def test_defaults_ubuntu(self):
        """Default boost building block"""
        b = boost()
        self.assertEqual(str(b),
r'''# Boost version 1.72.0
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        bzip2 \
        libbz2-dev \
        tar \
        wget \
        zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://dl.bintray.com/boostorg/release/1.72.0/source/boost_1_72_0.tar.bz2 && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/boost_1_72_0.tar.bz2 -C /var/tmp -j && \
    cd /var/tmp/boost_1_72_0 && ./bootstrap.sh --prefix=/usr/local/boost --without-libraries=python && \
    ./b2 -j$(nproc) -q install && \
    rm -rf /var/tmp/boost_1_72_0.tar.bz2 /var/tmp/boost_1_72_0
ENV LD_LIBRARY_PATH=/usr/local/boost/lib:$LD_LIBRARY_PATH''')

    @centos
    @docker
    def test_defaults_centos(self):
        """Default boost building block"""
        b = boost()
        self.assertEqual(str(b),
r'''# Boost version 1.72.0
RUN yum install -y \
        bzip2 \
        bzip2-devel \
        tar \
        wget \
        which \
        zlib-devel && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://dl.bintray.com/boostorg/release/1.72.0/source/boost_1_72_0.tar.bz2 && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/boost_1_72_0.tar.bz2 -C /var/tmp -j && \
    cd /var/tmp/boost_1_72_0 && ./bootstrap.sh --prefix=/usr/local/boost --without-libraries=python && \
    ./b2 -j$(nproc) -q install && \
    rm -rf /var/tmp/boost_1_72_0.tar.bz2 /var/tmp/boost_1_72_0
ENV LD_LIBRARY_PATH=/usr/local/boost/lib:$LD_LIBRARY_PATH''')

    @ubuntu
    @docker
    def test_python(self):
        """python option"""
        b = boost(python=True)
        self.assertEqual(str(b),
r'''# Boost version 1.72.0
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        bzip2 \
        libbz2-dev \
        tar \
        wget \
        zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://dl.bintray.com/boostorg/release/1.72.0/source/boost_1_72_0.tar.bz2 && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/boost_1_72_0.tar.bz2 -C /var/tmp -j && \
    cd /var/tmp/boost_1_72_0 && ./bootstrap.sh --prefix=/usr/local/boost  && \
    ./b2 -j$(nproc) -q install && \
    rm -rf /var/tmp/boost_1_72_0.tar.bz2 /var/tmp/boost_1_72_0
ENV LD_LIBRARY_PATH=/usr/local/boost/lib:$LD_LIBRARY_PATH''')

    @ubuntu
    @docker
    def test_sourceforge(self):
        """sourceforge option"""
        b = boost(sourceforge=True, version='1.57.0')
        self.assertEqual(str(b),
r'''# Boost version 1.57.0
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        bzip2 \
        libbz2-dev \
        tar \
        wget \
        zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://sourceforge.net/projects/boost/files/boost/1.57.0/boost_1_57_0.tar.bz2 && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/boost_1_57_0.tar.bz2 -C /var/tmp -j && \
    cd /var/tmp/boost_1_57_0 && ./bootstrap.sh --prefix=/usr/local/boost --without-libraries=python && \
    ./b2 -j$(nproc) -q install && \
    rm -rf /var/tmp/boost_1_57_0.tar.bz2 /var/tmp/boost_1_57_0
ENV LD_LIBRARY_PATH=/usr/local/boost/lib:$LD_LIBRARY_PATH''')

    @ubuntu
    @docker
    def test_ldconfig(self):
        """ldconfig option"""
        b = boost(ldconfig=True, version='1.68.0')
        self.assertEqual(str(b),
r'''# Boost version 1.68.0
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        bzip2 \
        libbz2-dev \
        tar \
        wget \
        zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://dl.bintray.com/boostorg/release/1.68.0/source/boost_1_68_0.tar.bz2 && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/boost_1_68_0.tar.bz2 -C /var/tmp -j && \
    cd /var/tmp/boost_1_68_0 && ./bootstrap.sh --prefix=/usr/local/boost --without-libraries=python && \
    ./b2 -j$(nproc) -q install && \
    echo "/usr/local/boost/lib" >> /etc/ld.so.conf.d/hpccm.conf && ldconfig && \
    rm -rf /var/tmp/boost_1_68_0.tar.bz2 /var/tmp/boost_1_68_0''')

    @ubuntu
    @docker
    def test_runtime(self):
        """Runtime"""
        b = boost()
        r = b.runtime()
        self.assertEqual(r,
r'''# Boost
COPY --from=0 /usr/local/boost /usr/local/boost
ENV LD_LIBRARY_PATH=/usr/local/boost/lib:$LD_LIBRARY_PATH''')
