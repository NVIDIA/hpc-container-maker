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

"""Test cases for the hdf5 module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import centos, docker, ubuntu

from hpccm.hdf5 import hdf5

class Test_hdf5(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @ubuntu
    @docker
    def test_defaults_ubuntu(self):
        """Default hdf5 building block"""
        h = hdf5()
        self.assertEqual(str(h),
r'''# HDF5 version 1.10.1
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        file \
        make \
        wget \
        zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /tmp && wget -q --no-check-certificate -P /tmp http://www.hdfgroup.org/ftp/HDF5/releases/hdf5-1.10/hdf5-1.10.1/src/hdf5-1.10.1.tar.bz2 && \
    tar -x -f /tmp/hdf5-1.10.1.tar.bz2 -C /tmp -j && \
    cd /tmp/hdf5-1.10.1 &&   ./configure --prefix=/usr/local/hdf5 --enable-cxx --enable-fortran && \
    make -j4 && \
    make -j4 install && \
    rm -rf /tmp/hdf5-1.10.1.tar.bz2 /tmp/hdf5-1.10.1
ENV HDF5_DIR=/usr/local/hdf5 \
    LD_LIBRARY_PATH=/usr/local/hdf5/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/hdf5/bin:$PATH''')

    @centos
    @docker
    def test_defaults_centos(self):
        """Default hdf5 building block"""
        h = hdf5()
        self.assertEqual(str(h),
r'''# HDF5 version 1.10.1
RUN yum install -y \
        bzip2 \
        file \
        make \
        wget \
        zlib-devel && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /tmp && wget -q --no-check-certificate -P /tmp http://www.hdfgroup.org/ftp/HDF5/releases/hdf5-1.10/hdf5-1.10.1/src/hdf5-1.10.1.tar.bz2 && \
    tar -x -f /tmp/hdf5-1.10.1.tar.bz2 -C /tmp -j && \
    cd /tmp/hdf5-1.10.1 &&   ./configure --prefix=/usr/local/hdf5 --enable-cxx --enable-fortran && \
    make -j4 && \
    make -j4 install && \
    rm -rf /tmp/hdf5-1.10.1.tar.bz2 /tmp/hdf5-1.10.1
ENV HDF5_DIR=/usr/local/hdf5 \
    LD_LIBRARY_PATH=/usr/local/hdf5/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/hdf5/bin:$PATH''')

    @ubuntu
    @docker
    def test_runtime(self):
        """Runtime"""
        h = hdf5()
        r = h.runtime()
        s = '\n'.join(str(x) for x in r)
        self.assertEqual(s,
r'''# HDF5
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        zlib1g && \
    rm -rf /var/lib/apt/lists/*
COPY --from=0 /usr/local/hdf5 /usr/local/hdf5
ENV HDF5_DIR=/usr/local/hdf5 \
    LD_LIBRARY_PATH=/usr/local/hdf5/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/hdf5/bin:$PATH''')

    @ubuntu
    @docker
    def test_directory(self):
        """Directory in local build context"""
        h = hdf5(directory='hdf5-1.10.1')
        self.assertEqual(str(h),
r'''# HDF5
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        file \
        make \
        wget \
        zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*
COPY hdf5-1.10.1 /tmp/hdf5-1.10.1
RUN cd /tmp/hdf5-1.10.1 &&   ./configure --prefix=/usr/local/hdf5 --enable-cxx --enable-fortran && \
    make -j4 && \
    make -j4 install && \
    rm -rf /tmp/hdf5-1.10.1
ENV HDF5_DIR=/usr/local/hdf5 \
    LD_LIBRARY_PATH=/usr/local/hdf5/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/hdf5/bin:$PATH''')
