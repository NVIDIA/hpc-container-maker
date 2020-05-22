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

"""Test cases for the AMGX module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import centos, docker, ubuntu

from hpccm.building_blocks.amgx import amgx
from hpccm.toolchain import toolchain

class Test_sensei(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @ubuntu
    @docker
    def test_branch_ubuntu(self):
        """Default amgx building block"""
        m = amgx(branch='v2.1.0')
        self.assertEqual(str(m),
r'''# AMGX branch v2.1.0
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        git \
        make && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && cd /var/tmp && git clone --depth=1 --branch v2.1.0 https://github.com/NVIDIA/amgx amgx && cd - && \
    mkdir -p /var/tmp/amgx/build && cd /var/tmp/amgx/build && cmake -DCMAKE_INSTALL_PREFIX=/usr/local/amgx /var/tmp/amgx && \
    cmake --build /var/tmp/amgx/build --target all -- -j$(nproc) && \
    cmake --build /var/tmp/amgx/build --target install -- -j$(nproc) && \
    rm -rf /var/tmp/amgx
ENV CPATH=/usr/local/amgx/include:$CPATH \
    LD_LIBRARY_PATH=/usr/local/amgx/lib:$LD_LIBRARY_PATH \
    LIBRARY_PATH=/usr/local/amgx/lib:$LIBRARY_PATH''')

    @centos
    @docker
    def test_branch_centos(self):
        """Default amgx building block"""
        m = amgx(branch='v2.1.0')
        self.assertEqual(str(m),
r'''# AMGX branch v2.1.0
RUN yum install -y \
        git \
        make && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp && cd /var/tmp && git clone --depth=1 --branch v2.1.0 https://github.com/NVIDIA/amgx amgx && cd - && \
    mkdir -p /var/tmp/amgx/build && cd /var/tmp/amgx/build && cmake -DCMAKE_INSTALL_PREFIX=/usr/local/amgx /var/tmp/amgx && \
    cmake --build /var/tmp/amgx/build --target all -- -j$(nproc) && \
    cmake --build /var/tmp/amgx/build --target install -- -j$(nproc) && \
    rm -rf /var/tmp/amgx
ENV CPATH=/usr/local/amgx/include:$CPATH \
    LD_LIBRARY_PATH=/usr/local/amgx/lib:$LD_LIBRARY_PATH \
    LIBRARY_PATH=/usr/local/amgx/lib:$LIBRARY_PATH''')

    @ubuntu
    @docker
    def test_defaults_ubuntu(self):
        """Default amgx building block"""
        m = amgx()
        self.assertEqual(str(m),
r'''# AMGX branch master
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        git \
        make && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && cd /var/tmp && git clone --depth=1 --branch master https://github.com/NVIDIA/amgx amgx && cd - && \
    mkdir -p /var/tmp/amgx/build && cd /var/tmp/amgx/build && cmake -DCMAKE_INSTALL_PREFIX=/usr/local/amgx /var/tmp/amgx && \
    cmake --build /var/tmp/amgx/build --target all -- -j$(nproc) && \
    cmake --build /var/tmp/amgx/build --target install -- -j$(nproc) && \
    rm -rf /var/tmp/amgx
ENV CPATH=/usr/local/amgx/include:$CPATH \
    LD_LIBRARY_PATH=/usr/local/amgx/lib:$LD_LIBRARY_PATH \
    LIBRARY_PATH=/usr/local/amgx/lib:$LIBRARY_PATH''')

    @centos
    @docker
    def test_defaults_centos(self):
        """Default amgx building block"""
        m = amgx()
        self.assertEqual(str(m),
r'''# AMGX branch master
RUN yum install -y \
        git \
        make && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp && cd /var/tmp && git clone --depth=1 --branch master https://github.com/NVIDIA/amgx amgx && cd - && \
    mkdir -p /var/tmp/amgx/build && cd /var/tmp/amgx/build && cmake -DCMAKE_INSTALL_PREFIX=/usr/local/amgx /var/tmp/amgx && \
    cmake --build /var/tmp/amgx/build --target all -- -j$(nproc) && \
    cmake --build /var/tmp/amgx/build --target install -- -j$(nproc) && \
    rm -rf /var/tmp/amgx
ENV CPATH=/usr/local/amgx/include:$CPATH \
    LD_LIBRARY_PATH=/usr/local/amgx/lib:$LD_LIBRARY_PATH \
    LIBRARY_PATH=/usr/local/amgx/lib:$LIBRARY_PATH''')
