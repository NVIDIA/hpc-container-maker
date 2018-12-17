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

"""Test cases for the netcdf module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import centos, docker, ubuntu

from hpccm.building_blocks.netcdf import netcdf

class Test_netcdf(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @ubuntu
    @docker
    def test_defaults_ubuntu(self):
        """Default netcdf building block"""
        n = netcdf()
        self.assertEqual(str(n),
r'''# NetCDF version 4.6.1, NetCDF C++ version 4.3.0, NetCDF Fortran
# version 4.4.4
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ca-certificates \
        file \
        libcurl4-openssl-dev \
        m4 \
        make \
        wget \
        zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://www.unidata.ucar.edu/downloads/netcdf/ftp/netcdf-4.6.1.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/netcdf-4.6.1.tar.gz -C /var/tmp -z && \
    cd /var/tmp/netcdf-4.6.1 &&  CPPFLAGS=-I/usr/local/hdf5/include LDFLAGS=-L/usr/local/hdf5/lib ./configure --prefix=/usr/local/netcdf && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/netcdf-4.6.1.tar.gz /var/tmp/netcdf-4.6.1 && \
    mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://www.unidata.ucar.edu/downloads/netcdf/ftp/netcdf-cxx4-4.3.0.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/netcdf-cxx4-4.3.0.tar.gz -C /var/tmp -z && \
    cd /var/tmp/netcdf-cxx4-4.3.0 &&  CPPFLAGS=-I/usr/local/netcdf/include LD_LIBRARY_PATH='/usr/local/netcdf/lib:$LD_LIBRARY_PATH' LDFLAGS=-L/usr/local/netcdf/lib ./configure --prefix=/usr/local/netcdf && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/netcdf-cxx4-4.3.0.tar.gz /var/tmp/netcdf-cxx4-4.3.0 && \
    mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://www.unidata.ucar.edu/downloads/netcdf/ftp/netcdf-fortran-4.4.4.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/netcdf-fortran-4.4.4.tar.gz -C /var/tmp -z && \
    cd /var/tmp/netcdf-fortran-4.4.4 &&  CPPFLAGS=-I/usr/local/netcdf/include LD_LIBRARY_PATH='/usr/local/netcdf/lib:$LD_LIBRARY_PATH' LDFLAGS=-L/usr/local/netcdf/lib ./configure --prefix=/usr/local/netcdf && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/netcdf-fortran-4.4.4.tar.gz /var/tmp/netcdf-fortran-4.4.4
ENV LD_LIBRARY_PATH=/usr/local/netcdf/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/netcdf/bin:$PATH''')

    @centos
    @docker
    def test_defaults_centos(self):
        """Default netcdf building block"""
        n = netcdf()
        self.assertEqual(str(n),
r'''# NetCDF version 4.6.1, NetCDF C++ version 4.3.0, NetCDF Fortran
# version 4.4.4
RUN yum install -y \
        ca-certificates \
        file \
        libcurl-devel \
        m4 \
        make \
        wget \
        zlib-devel && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://www.unidata.ucar.edu/downloads/netcdf/ftp/netcdf-4.6.1.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/netcdf-4.6.1.tar.gz -C /var/tmp -z && \
    cd /var/tmp/netcdf-4.6.1 &&  CPPFLAGS=-I/usr/local/hdf5/include LDFLAGS=-L/usr/local/hdf5/lib ./configure --prefix=/usr/local/netcdf && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/netcdf-4.6.1.tar.gz /var/tmp/netcdf-4.6.1 && \
    mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://www.unidata.ucar.edu/downloads/netcdf/ftp/netcdf-cxx4-4.3.0.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/netcdf-cxx4-4.3.0.tar.gz -C /var/tmp -z && \
    cd /var/tmp/netcdf-cxx4-4.3.0 &&  CPPFLAGS=-I/usr/local/netcdf/include LD_LIBRARY_PATH='/usr/local/netcdf/lib:$LD_LIBRARY_PATH' LDFLAGS=-L/usr/local/netcdf/lib ./configure --prefix=/usr/local/netcdf && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/netcdf-cxx4-4.3.0.tar.gz /var/tmp/netcdf-cxx4-4.3.0 && \
    mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://www.unidata.ucar.edu/downloads/netcdf/ftp/netcdf-fortran-4.4.4.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/netcdf-fortran-4.4.4.tar.gz -C /var/tmp -z && \
    cd /var/tmp/netcdf-fortran-4.4.4 &&  CPPFLAGS=-I/usr/local/netcdf/include LD_LIBRARY_PATH='/usr/local/netcdf/lib:$LD_LIBRARY_PATH' LDFLAGS=-L/usr/local/netcdf/lib ./configure --prefix=/usr/local/netcdf && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/netcdf-fortran-4.4.4.tar.gz /var/tmp/netcdf-fortran-4.4.4
ENV LD_LIBRARY_PATH=/usr/local/netcdf/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/netcdf/bin:$PATH''')

    @ubuntu
    @docker
    def test_runtime(self):
        """Runtime"""
        n = netcdf()
        r = n.runtime()
        self.assertEqual(r,
r'''# NetCDF
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        zlib1g && \
    rm -rf /var/lib/apt/lists/*
COPY --from=0 /usr/local/netcdf /usr/local/netcdf
ENV LD_LIBRARY_PATH=/usr/local/netcdf/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/netcdf/bin:$PATH''')
