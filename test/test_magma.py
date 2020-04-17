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

"""Test cases for the magma module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import centos, docker, ubuntu

from hpccm.building_blocks.magma import magma
from hpccm.toolchain import toolchain

class Test_sensei(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @ubuntu
    @docker
    def test_defaults_ubuntu(self):
        """Default magma building block"""
        m = magma()
        self.assertEqual(str(m),
r'''# MAGMA version 2.5.3
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        tar \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp http://icl.utk.edu/projectsfiles/magma/downloads/magma-2.5.3.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/magma-2.5.3.tar.gz -C /var/tmp -z && \
    mkdir -p /var/tmp/magma-2.5.3/build && cd /var/tmp/magma-2.5.3/build && cmake -DCMAKE_INSTALL_PREFIX=/usr/local/magma -DGPU_TARGET="Pascal Volta Turing" /var/tmp/magma-2.5.3 && \
    cmake --build /var/tmp/magma-2.5.3/build --target all -- -j$(nproc) && \
    cmake --build /var/tmp/magma-2.5.3/build --target install -- -j$(nproc) && \
    rm -rf /var/tmp/magma-2.5.3 /var/tmp/magma-2.5.3.tar.gz
ENV CPATH=/usr/local/magma/include:$CPATH \
    LD_LIBRARY_PATH=/usr/local/magma/lib:$LD_LIBRARY_PATH \
    LIBRARY_PATH=/usr/local/magma/lib:$LIBRARY_PATH''')

    @centos
    @docker
    def test_defaults_centos(self):
        """Default magma building block"""
        m = magma()
        self.assertEqual(str(m),
r'''# MAGMA version 2.5.3
RUN yum install -y \
        tar \
        wget && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp http://icl.utk.edu/projectsfiles/magma/downloads/magma-2.5.3.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/magma-2.5.3.tar.gz -C /var/tmp -z && \
    mkdir -p /var/tmp/magma-2.5.3/build && cd /var/tmp/magma-2.5.3/build && cmake -DCMAKE_INSTALL_PREFIX=/usr/local/magma -DGPU_TARGET="Pascal Volta Turing" /var/tmp/magma-2.5.3 && \
    cmake --build /var/tmp/magma-2.5.3/build --target all -- -j$(nproc) && \
    cmake --build /var/tmp/magma-2.5.3/build --target install -- -j$(nproc) && \
    rm -rf /var/tmp/magma-2.5.3 /var/tmp/magma-2.5.3.tar.gz
ENV CPATH=/usr/local/magma/include:$CPATH \
    LD_LIBRARY_PATH=/usr/local/magma/lib:$LD_LIBRARY_PATH \
    LIBRARY_PATH=/usr/local/magma/lib:$LIBRARY_PATH''')

    @ubuntu
    @docker
    def test_runtime(self):
        """Runtime"""
        m = magma()
        r = m.runtime()
        self.assertEqual(r,
r'''# MAGMA
COPY --from=0 /usr/local/magma /usr/local/magma
ENV CPATH=/usr/local/magma/include:$CPATH \
    LD_LIBRARY_PATH=/usr/local/magma/lib:$LD_LIBRARY_PATH \
    LIBRARY_PATH=/usr/local/magma/lib:$LIBRARY_PATH''')
