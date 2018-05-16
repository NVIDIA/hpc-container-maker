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

from helpers import centos, docker, ubuntu

from hpccm.cmake import cmake

class Test_cmake(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @ubuntu
    @docker
    def test_defaults_ubuntu(self):
        """Default cmake building block"""
        c = cmake()
        self.assertEqual(str(c),
r'''# CMake version 3.11.1
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /tmp && wget -q --no-check-certificate -P /tmp https://cmake.org/files/v3.11/cmake-3.11.1-Linux-x86_64.sh && \
    /bin/sh /tmp/cmake-3.11.1-Linux-x86_64.sh --prefix=/usr/local && \
    rm -rf /tmp/cmake-3.11.1-Linux-x86_64.sh''')

    @centos
    @docker
    def test_defaults_centos(self):
        """Default cmake building block"""
        c = cmake()
        self.assertEqual(str(c),
r'''# CMake version 3.11.1
RUN yum install -y \
        wget && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /tmp && wget -q --no-check-certificate -P /tmp https://cmake.org/files/v3.11/cmake-3.11.1-Linux-x86_64.sh && \
    /bin/sh /tmp/cmake-3.11.1-Linux-x86_64.sh --prefix=/usr/local && \
    rm -rf /tmp/cmake-3.11.1-Linux-x86_64.sh''')

    @ubuntu
    @docker
    def test_eula(self):
        """Accept EULA"""
        c = cmake(eula=True)
        self.assertEqual(str(c),
r'''# CMake version 3.11.1
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /tmp && wget -q --no-check-certificate -P /tmp https://cmake.org/files/v3.11/cmake-3.11.1-Linux-x86_64.sh && \
    /bin/sh /tmp/cmake-3.11.1-Linux-x86_64.sh --prefix=/usr/local --skip-license && \
    rm -rf /tmp/cmake-3.11.1-Linux-x86_64.sh''')

    @ubuntu
    @docker
    def test_version(self):
        """Version option"""
        c = cmake(eula=True, version='3.10.3')
        self.assertEqual(str(c),
r'''# CMake version 3.10.3
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /tmp && wget -q --no-check-certificate -P /tmp https://cmake.org/files/v3.10/cmake-3.10.3-Linux-x86_64.sh && \
    /bin/sh /tmp/cmake-3.10.3-Linux-x86_64.sh --prefix=/usr/local --skip-license && \
    rm -rf /tmp/cmake-3.10.3-Linux-x86_64.sh''')

    @ubuntu
    @docker
    def test_runtime(self):
        """Runtime"""
        c = cmake(eula=True)
        r = c.runtime()
        self.assertEqual(str(r),
r'''# CMake version 3.11.1
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /tmp && wget -q --no-check-certificate -P /tmp https://cmake.org/files/v3.11/cmake-3.11.1-Linux-x86_64.sh && \
    /bin/sh /tmp/cmake-3.11.1-Linux-x86_64.sh --prefix=/usr/local --skip-license && \
    rm -rf /tmp/cmake-3.11.1-Linux-x86_64.sh''')
