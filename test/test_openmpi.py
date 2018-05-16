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

"""Test cases for the openmpi module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import centos, docker, ubuntu

from hpccm.openmpi import openmpi

class Test_openmpi(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @ubuntu
    @docker
    def test_defaults_ubuntu(self):
        """Default openmpi building block"""
        ompi = openmpi()
        self.assertEqual(str(ompi),
r'''# OpenMPI version 3.0.0
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        file \
        hwloc \
        openssh-client \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /tmp && wget -q --no-check-certificate -P /tmp https://www.open-mpi.org/software/ompi/v3.0/downloads/openmpi-3.0.0.tar.bz2 && \
    tar -x -f /tmp/openmpi-3.0.0.tar.bz2 -C /tmp -j && \
    cd /tmp/openmpi-3.0.0 &&   ./configure --prefix=/usr/local/openmpi --disable-getpwuid --enable-orterun-prefix-by-default --with-cuda --with-verbs && \
    make -j4 && \
    make -j4 install && \
    rm -rf /tmp/openmpi-3.0.0.tar.bz2 /tmp/openmpi-3.0.0
ENV LD_LIBRARY_PATH=/usr/local/openmpi/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/openmpi/bin:$PATH''')

    @centos
    @docker
    def test_defaults_centos(self):
        """Default openmpi building block"""
        ompi = openmpi()
        self.assertEqual(str(ompi),
r'''# OpenMPI version 3.0.0
RUN yum install -y \
        bzip2 \
        file \
        hwloc \
        make \
        openssh-clients \
        perl \
        wget && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /tmp && wget -q --no-check-certificate -P /tmp https://www.open-mpi.org/software/ompi/v3.0/downloads/openmpi-3.0.0.tar.bz2 && \
    tar -x -f /tmp/openmpi-3.0.0.tar.bz2 -C /tmp -j && \
    cd /tmp/openmpi-3.0.0 &&   ./configure --prefix=/usr/local/openmpi --disable-getpwuid --enable-orterun-prefix-by-default --with-cuda --with-verbs && \
    make -j4 && \
    make -j4 install && \
    rm -rf /tmp/openmpi-3.0.0.tar.bz2 /tmp/openmpi-3.0.0
ENV LD_LIBRARY_PATH=/usr/local/openmpi/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/openmpi/bin:$PATH''')

    @ubuntu
    @docker
    def test_directory(self):
        """Directory in local build context"""
        ompi = openmpi(directory='openmpi-3.0.0')
        self.assertEqual(str(ompi),
r'''# OpenMPI
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        file \
        hwloc \
        openssh-client \
        wget && \
    rm -rf /var/lib/apt/lists/*
COPY openmpi-3.0.0 /tmp/openmpi-3.0.0
RUN cd /tmp/openmpi-3.0.0 &&   ./configure --prefix=/usr/local/openmpi --disable-getpwuid --enable-orterun-prefix-by-default --with-cuda --with-verbs && \
    make -j4 && \
    make -j4 install && \
    rm -rf /tmp/openmpi-3.0.0
ENV LD_LIBRARY_PATH=/usr/local/openmpi/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/openmpi/bin:$PATH''')

    @ubuntu
    @docker
    def test_runtime(self):
        """Runtime"""
        ompi = openmpi()
        r = ompi.runtime()
        s = '\n'.join(str(x) for x in r)
        self.assertEqual(s,
r'''# OpenMPI
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        hwloc \
        openssh-client && \
    rm -rf /var/lib/apt/lists/*
COPY --from=0 /usr/local/openmpi /usr/local/openmpi
ENV LD_LIBRARY_PATH=/usr/local/openmpi/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/openmpi/bin:$PATH''')

    def test_toolchain(self):
        """Toolchain"""
        ompi = openmpi()
        tc = ompi.toolchain
        self.assertEqual(tc.CC, 'mpicc')
        self.assertEqual(tc.CXX, 'mpicxx')
        self.assertEqual(tc.FC, 'mpifort')
        self.assertEqual(tc.F77, 'mpif77')
        self.assertEqual(tc.F90, 'mpif90')
