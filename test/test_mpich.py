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

"""Test cases for the mpich module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import centos, docker, ubuntu

from hpccm.building_blocks.mpich import mpich
from hpccm.toolchain import toolchain

class Test_mpich(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @ubuntu
    @docker
    def test_defaults_ubuntu(self):
        """Default mpich building block"""
        m = mpich()
        self.assertEqual(str(m),
r'''# MPICH version 3.3.2
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        file \
        gzip \
        make \
        openssh-client \
        perl \
        tar \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://www.mpich.org/static/downloads/3.3.2/mpich-3.3.2.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/mpich-3.3.2.tar.gz -C /var/tmp -z && \
    cd /var/tmp/mpich-3.3.2 &&   ./configure --prefix=/usr/local/mpich && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/mpich-3.3.2 /var/tmp/mpich-3.3.2.tar.gz
ENV LD_LIBRARY_PATH=/usr/local/mpich/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/mpich/bin:$PATH''')

    @centos
    @docker
    def test_defaults_centos(self):
        """Default mpich building block"""
        m = mpich()
        self.assertEqual(str(m),
r'''# MPICH version 3.3.2
RUN yum install -y \
        file \
        gzip \
        make \
        openssh-clients \
        perl \
        tar \
        wget && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://www.mpich.org/static/downloads/3.3.2/mpich-3.3.2.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/mpich-3.3.2.tar.gz -C /var/tmp -z && \
    cd /var/tmp/mpich-3.3.2 &&   ./configure --prefix=/usr/local/mpich && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/mpich-3.3.2 /var/tmp/mpich-3.3.2.tar.gz
ENV LD_LIBRARY_PATH=/usr/local/mpich/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/mpich/bin:$PATH''')

    @ubuntu
    @docker
    def test_ldconfig(self):
        """ldconfig option"""
        m = mpich(ldconfig=True, version='3.3')
        self.assertEqual(str(m),
r'''# MPICH version 3.3
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        file \
        gzip \
        make \
        openssh-client \
        perl \
        tar \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://www.mpich.org/static/downloads/3.3/mpich-3.3.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/mpich-3.3.tar.gz -C /var/tmp -z && \
    cd /var/tmp/mpich-3.3 &&   ./configure --prefix=/usr/local/mpich && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    echo "/usr/local/mpich/lib" >> /etc/ld.so.conf.d/hpccm.conf && ldconfig && \
    rm -rf /var/tmp/mpich-3.3 /var/tmp/mpich-3.3.tar.gz
ENV PATH=/usr/local/mpich/bin:$PATH''')

    @ubuntu
    @docker
    def test_runtime(self):
        """Runtime"""
        m = mpich()
        r = m.runtime()
        self.assertEqual(r,
r'''# MPICH
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        openssh-client && \
    rm -rf /var/lib/apt/lists/*
COPY --from=0 /usr/local/mpich /usr/local/mpich
ENV LD_LIBRARY_PATH=/usr/local/mpich/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/mpich/bin:$PATH''')

    def test_toolchain(self):
        """Toolchain"""
        m = mpich()
        tc = m.toolchain
        self.assertEqual(tc.CC, 'mpicc')
        self.assertEqual(tc.CXX, 'mpicxx')
        self.assertEqual(tc.FC, 'mpifort')
        self.assertEqual(tc.F77, 'mpif77')
        self.assertEqual(tc.F90, 'mpif90')
