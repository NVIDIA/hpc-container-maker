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

"""Test cases for the fftw module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import centos, docker, ubuntu

from hpccm.building_blocks.fftw import fftw

class Test_fftw(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @ubuntu
    @docker
    def test_defaults_ubuntu(self):
        """Default fftw building block"""
        f = fftw()
        self.assertEqual(str(f),
r'''# FFTW version 3.3.8
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        file \
        make \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp ftp://ftp.fftw.org/pub/fftw/fftw-3.3.8.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/fftw-3.3.8.tar.gz -C /var/tmp -z && \
    cd /var/tmp/fftw-3.3.8 &&   ./configure --prefix=/usr/local/fftw --enable-shared --enable-openmp --enable-threads --enable-sse2 && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/fftw-3.3.8.tar.gz /var/tmp/fftw-3.3.8
ENV LD_LIBRARY_PATH=/usr/local/fftw/lib:$LD_LIBRARY_PATH''')

    @centos
    @docker
    def test_defaults_centos(self):
        """Default fftw building block"""
        f = fftw()
        self.assertEqual(str(f),
r'''# FFTW version 3.3.8
RUN yum install -y \
        file \
        make \
        wget && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp ftp://ftp.fftw.org/pub/fftw/fftw-3.3.8.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/fftw-3.3.8.tar.gz -C /var/tmp -z && \
    cd /var/tmp/fftw-3.3.8 &&   ./configure --prefix=/usr/local/fftw --enable-shared --enable-openmp --enable-threads --enable-sse2 && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/fftw-3.3.8.tar.gz /var/tmp/fftw-3.3.8
ENV LD_LIBRARY_PATH=/usr/local/fftw/lib:$LD_LIBRARY_PATH''')

    @ubuntu
    @docker
    def test_mpi(self):
        """MPI enabled"""
        f = fftw(mpi=True)
        self.assertEqual(str(f),
r'''# FFTW version 3.3.8
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        file \
        make \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp ftp://ftp.fftw.org/pub/fftw/fftw-3.3.8.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/fftw-3.3.8.tar.gz -C /var/tmp -z && \
    cd /var/tmp/fftw-3.3.8 &&   ./configure --prefix=/usr/local/fftw --enable-shared --enable-openmp --enable-threads --enable-sse2 --enable-mpi && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/fftw-3.3.8.tar.gz /var/tmp/fftw-3.3.8
ENV LD_LIBRARY_PATH=/usr/local/fftw/lib:$LD_LIBRARY_PATH''')

    @ubuntu
    @docker
    def test_runtime(self):
        """Runtime"""
        f = fftw()
        r = f.runtime()
        self.assertEqual(r,
r'''# FFTW
COPY --from=0 /usr/local/fftw /usr/local/fftw
ENV LD_LIBRARY_PATH=/usr/local/fftw/lib:$LD_LIBRARY_PATH''')

    @ubuntu
    @docker
    def test_directory(self):
        """Directory in local build context"""
        f = fftw(directory='fftw-3.3.7')
        self.assertEqual(str(f),
r'''# FFTW
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        file \
        make \
        wget && \
    rm -rf /var/lib/apt/lists/*
COPY fftw-3.3.7 /var/tmp/fftw-3.3.7
RUN cd /var/tmp/fftw-3.3.7 &&   ./configure --prefix=/usr/local/fftw --enable-shared --enable-openmp --enable-threads --enable-sse2 && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/fftw-3.3.7
ENV LD_LIBRARY_PATH=/usr/local/fftw/lib:$LD_LIBRARY_PATH''')
