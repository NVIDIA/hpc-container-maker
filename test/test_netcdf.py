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
r'''# NetCDF version 4.7.3, NetCDF C++ version 4.3.1, NetCDF Fortran
# version 4.5.2
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
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/Unidata/netcdf-c/archive/v4.7.3.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/v4.7.3.tar.gz -C /var/tmp -z && \
    cd /var/tmp/netcdf-c-4.7.3 &&   ./configure --prefix=/usr/local/netcdf && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/netcdf-c-4.7.3 /var/tmp/v4.7.3.tar.gz
ENV CPATH=/usr/local/netcdf/include:$CPATH \
    LD_LIBRARY_PATH=/usr/local/netcdf/lib:$LD_LIBRARY_PATH \
    LIBRARY_PATH=/usr/local/netcdf/lib:$LIBRARY_PATH \
    PATH=/usr/local/netcdf/bin:$PATH
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/Unidata/netcdf-cxx4/archive/v4.3.1.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/v4.3.1.tar.gz -C /var/tmp -z && \
    cd /var/tmp/netcdf-cxx4-4.3.1 &&   ./configure --prefix=/usr/local/netcdf && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/netcdf-cxx4-4.3.1 /var/tmp/v4.3.1.tar.gz
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/Unidata/netcdf-fortran/archive/v4.5.2.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/v4.5.2.tar.gz -C /var/tmp -z && \
    cd /var/tmp/netcdf-fortran-4.5.2 &&   ./configure --prefix=/usr/local/netcdf && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/netcdf-fortran-4.5.2 /var/tmp/v4.5.2.tar.gz''')

    @centos
    @docker
    def test_defaults_centos(self):
        """Default netcdf building block"""
        n = netcdf()
        self.assertEqual(str(n),
r'''# NetCDF version 4.7.3, NetCDF C++ version 4.3.1, NetCDF Fortran
# version 4.5.2
RUN yum install -y \
        ca-certificates \
        file \
        libcurl-devel \
        m4 \
        make \
        wget \
        zlib-devel && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/Unidata/netcdf-c/archive/v4.7.3.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/v4.7.3.tar.gz -C /var/tmp -z && \
    cd /var/tmp/netcdf-c-4.7.3 &&   ./configure --prefix=/usr/local/netcdf && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/netcdf-c-4.7.3 /var/tmp/v4.7.3.tar.gz
ENV CPATH=/usr/local/netcdf/include:$CPATH \
    LD_LIBRARY_PATH=/usr/local/netcdf/lib:$LD_LIBRARY_PATH \
    LIBRARY_PATH=/usr/local/netcdf/lib:$LIBRARY_PATH \
    PATH=/usr/local/netcdf/bin:$PATH
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/Unidata/netcdf-cxx4/archive/v4.3.1.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/v4.3.1.tar.gz -C /var/tmp -z && \
    cd /var/tmp/netcdf-cxx4-4.3.1 &&   ./configure --prefix=/usr/local/netcdf && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/netcdf-cxx4-4.3.1 /var/tmp/v4.3.1.tar.gz
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/Unidata/netcdf-fortran/archive/v4.5.2.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/v4.5.2.tar.gz -C /var/tmp -z && \
    cd /var/tmp/netcdf-fortran-4.5.2 &&   ./configure --prefix=/usr/local/netcdf && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/netcdf-fortran-4.5.2 /var/tmp/v4.5.2.tar.gz''')

    @ubuntu
    @docker
    def test_ldconfig(self):
        """ldconfig option"""
        n = netcdf(ldconfig=True, version='4.6.1', version_cxx='4.3.0',
                   version_fortran='4.4.4')
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
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/Unidata/netcdf-c/archive/v4.6.1.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/v4.6.1.tar.gz -C /var/tmp -z && \
    cd /var/tmp/netcdf-c-4.6.1 &&   ./configure --prefix=/usr/local/netcdf && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    echo "/usr/local/netcdf/lib" >> /etc/ld.so.conf.d/hpccm.conf && ldconfig && \
    rm -rf /var/tmp/netcdf-c-4.6.1 /var/tmp/v4.6.1.tar.gz
ENV CPATH=/usr/local/netcdf/include:$CPATH \
    LIBRARY_PATH=/usr/local/netcdf/lib:$LIBRARY_PATH \
    PATH=/usr/local/netcdf/bin:$PATH
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/Unidata/netcdf-cxx4/archive/v4.3.0.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/v4.3.0.tar.gz -C /var/tmp -z && \
    cd /var/tmp/netcdf-cxx4-4.3.0 &&   ./configure --prefix=/usr/local/netcdf && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    echo "/usr/local/netcdf/lib" >> /etc/ld.so.conf.d/hpccm.conf && ldconfig && \
    rm -rf /var/tmp/netcdf-cxx4-4.3.0 /var/tmp/v4.3.0.tar.gz
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/Unidata/netcdf-fortran/archive/v4.4.4.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/v4.4.4.tar.gz -C /var/tmp -z && \
    cd /var/tmp/netcdf-fortran-4.4.4 &&   ./configure --prefix=/usr/local/netcdf && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    echo "/usr/local/netcdf/lib" >> /etc/ld.so.conf.d/hpccm.conf && ldconfig && \
    rm -rf /var/tmp/netcdf-fortran-4.4.4 /var/tmp/v4.4.4.tar.gz''')

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
ENV CPATH=/usr/local/netcdf/include:$CPATH \
    LD_LIBRARY_PATH=/usr/local/netcdf/lib:$LD_LIBRARY_PATH \
    LIBRARY_PATH=/usr/local/netcdf/lib:$LIBRARY_PATH \
    PATH=/usr/local/netcdf/bin:$PATH''')
