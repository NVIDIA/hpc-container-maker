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

"""Test cases for the cmake module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import aarch64, centos, docker, ubuntu, x86_64

from hpccm.building_blocks.cmake import cmake

class Test_cmake(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @x86_64
    @ubuntu
    @docker
    def test_defaults_ubuntu(self):
        """Default cmake building block"""
        c = cmake()
        self.assertEqual(str(c),
r'''# CMake version 3.16.3
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        make \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://cmake.org/files/v3.16/cmake-3.16.3-Linux-x86_64.sh && \
    mkdir -p /usr/local && \
    /bin/sh /var/tmp/cmake-3.16.3-Linux-x86_64.sh --prefix=/usr/local && \
    rm -rf /var/tmp/cmake-3.16.3-Linux-x86_64.sh
ENV PATH=/usr/local/bin:$PATH''')

    @x86_64
    @centos
    @docker
    def test_defaults_centos(self):
        """Default cmake building block"""
        c = cmake()
        self.assertEqual(str(c),
r'''# CMake version 3.16.3
RUN yum install -y \
        make \
        wget && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://cmake.org/files/v3.16/cmake-3.16.3-Linux-x86_64.sh && \
    mkdir -p /usr/local && \
    /bin/sh /var/tmp/cmake-3.16.3-Linux-x86_64.sh --prefix=/usr/local && \
    rm -rf /var/tmp/cmake-3.16.3-Linux-x86_64.sh
ENV PATH=/usr/local/bin:$PATH''')

    @x86_64
    @ubuntu
    @docker
    def test_eula(self):
        """Accept EULA"""
        c = cmake(eula=True)
        self.assertEqual(str(c),
r'''# CMake version 3.16.3
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        make \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://cmake.org/files/v3.16/cmake-3.16.3-Linux-x86_64.sh && \
    mkdir -p /usr/local && \
    /bin/sh /var/tmp/cmake-3.16.3-Linux-x86_64.sh --prefix=/usr/local --skip-license && \
    rm -rf /var/tmp/cmake-3.16.3-Linux-x86_64.sh
ENV PATH=/usr/local/bin:$PATH''')

    @x86_64
    @ubuntu
    @docker
    def test_version(self):
        """Version option"""
        c = cmake(eula=True, version='3.10.3')
        self.assertEqual(str(c),
r'''# CMake version 3.10.3
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        make \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://cmake.org/files/v3.10/cmake-3.10.3-Linux-x86_64.sh && \
    mkdir -p /usr/local && \
    /bin/sh /var/tmp/cmake-3.10.3-Linux-x86_64.sh --prefix=/usr/local --skip-license && \
    rm -rf /var/tmp/cmake-3.10.3-Linux-x86_64.sh
ENV PATH=/usr/local/bin:$PATH''')

    @x86_64
    @centos
    @docker
    def test_source(self):
        """Source option"""
        c = cmake(eula=True, source=True, version='3.14.5')
        self.assertEqual(str(c),
r'''# CMake version 3.14.5
RUN yum install -y \
        make \
        openssl-devel \
        wget && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://cmake.org/files/v3.14/cmake-3.14.5.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/cmake-3.14.5.tar.gz -C /var/tmp -z && \
    cd /var/tmp/cmake-3.14.5 && ./bootstrap --prefix=/usr/local --parallel=$(nproc) && \
    make -j$(nproc) && \
    make install && \
    rm -rf /var/tmp/cmake-3.14.5.tar.gz /var/tmp/cmake-3.14.5
ENV PATH=/usr/local/bin:$PATH''')

    @aarch64
    @centos
    @docker
    def test_aarch64(self):
        """Source option"""
        c = cmake(eula=True, version='3.14.5')
        self.assertEqual(str(c),
r'''# CMake version 3.14.5
RUN yum install -y \
        make \
        openssl-devel \
        wget && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://cmake.org/files/v3.14/cmake-3.14.5.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/cmake-3.14.5.tar.gz -C /var/tmp -z && \
    cd /var/tmp/cmake-3.14.5 && ./bootstrap --prefix=/usr/local --parallel=$(nproc) && \
    make -j$(nproc) && \
    make install && \
    rm -rf /var/tmp/cmake-3.14.5.tar.gz /var/tmp/cmake-3.14.5
ENV PATH=/usr/local/bin:$PATH''')
