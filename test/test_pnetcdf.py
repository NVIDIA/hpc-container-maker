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

"""Test cases for the pnetcdf module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import centos, docker, ubuntu

from hpccm.building_blocks.pnetcdf import pnetcdf

class Test_pnetcdf(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @ubuntu
    @docker
    def test_defaults(self):
        """Default pnetcdf building block"""
        p = pnetcdf()
        self.assertEqual(str(p),
r'''# PnetCDF version 1.12.1
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        m4 \
        make \
        tar \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://parallel-netcdf.github.io/Release/pnetcdf-1.12.1.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/pnetcdf-1.12.1.tar.gz -C /var/tmp -z && \
    cd /var/tmp/pnetcdf-1.12.1 &&  CC=mpicc CXX=mpicxx F77=mpif77 F90=mpif90 FC=mpifort ./configure --prefix=/usr/local/pnetcdf --enable-shared && \
    cd /var/tmp/pnetcdf-1.12.1 && \
    sed -i -e 's#pic_flag=""#pic_flag=" -fpic -DPIC"#' -e 's#wl=""#wl="-Wl,"#' libtool && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/pnetcdf-1.12.1 /var/tmp/pnetcdf-1.12.1.tar.gz
ENV LD_LIBRARY_PATH=/usr/local/pnetcdf/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/pnetcdf/bin:$PATH''')

    @ubuntu
    @docker
    def test_ldconfig(self):
        """ldconfig option"""
        p = pnetcdf(ldconfig=True, version='1.10.0')
        self.assertEqual(str(p),
r'''# PnetCDF version 1.10.0
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        m4 \
        make \
        tar \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://parallel-netcdf.github.io/Release/parallel-netcdf-1.10.0.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/parallel-netcdf-1.10.0.tar.gz -C /var/tmp -z && \
    cd /var/tmp/parallel-netcdf-1.10.0 &&  CC=mpicc CXX=mpicxx F77=mpif77 F90=mpif90 FC=mpifort ./configure --prefix=/usr/local/pnetcdf --enable-shared && \
    cd /var/tmp/parallel-netcdf-1.10.0 && \
    sed -i -e 's#pic_flag=""#pic_flag=" -fpic -DPIC"#' -e 's#wl=""#wl="-Wl,"#' libtool && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    echo "/usr/local/pnetcdf/lib" >> /etc/ld.so.conf.d/hpccm.conf && ldconfig && \
    rm -rf /var/tmp/parallel-netcdf-1.10.0 /var/tmp/parallel-netcdf-1.10.0.tar.gz
ENV PATH=/usr/local/pnetcdf/bin:$PATH''')

    @ubuntu
    @docker
    def test_runtime(self):
        """Runtime"""
        p = pnetcdf()
        r = p.runtime()
        self.assertEqual(r,
r'''# PnetCDF
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libatomic1 && \
    rm -rf /var/lib/apt/lists/*
COPY --from=0 /usr/local/pnetcdf /usr/local/pnetcdf
ENV LD_LIBRARY_PATH=/usr/local/pnetcdf/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/pnetcdf/bin:$PATH''')
