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

"""Test cases for the nvshmem module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import centos, docker, ubuntu

from hpccm.building_blocks.nvshmem import nvshmem

class Test_nvshmem(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @ubuntu
    @docker
    def test_defaults_ubuntu(self):
        """nvshmem defaults"""
        n = nvshmem()
        self.assertEqual(str(n),
r'''# NVSHMEM 2.9.0-2
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        make \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://developer.download.nvidia.com/compute/redist/nvshmem/2.9.0/source/nvshmem_src_2.9.0-2.txz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/nvshmem_src_2.9.0-2.txz -C /var/tmp -J && \
    mkdir -p /var/tmp/nvshmem_src_2.9.0-2/build && cd /var/tmp/nvshmem_src_2.9.0-2/build && cmake -DCMAKE_INSTALL_PREFIX=/usr/local/nvshmem -DNVSHMEM_BUILD_EXAMPLES=OFF -DNVSHMEM_BUILD_PACKAGES=OFF -DNVSHMEM_BUILD_DEB_PACKAGES=OFF -DNVSHMEM_BUILD_RPM_PACKAGES=OFF -DCUDA_HOME=/usr/local/cuda /var/tmp/nvshmem_src_2.9.0-2 && \
    cmake --build /var/tmp/nvshmem_src_2.9.0-2/build --target all -- -j$(nproc) && \
    cmake --build /var/tmp/nvshmem_src_2.9.0-2/build --target install -- -j$(nproc) && \
    rm -rf /var/tmp/nvshmem_src_2.9.0-2 /var/tmp/nvshmem_src_2.9.0-2.txz
ENV CPATH=/usr/local/nvshmem/include:$CPATH \
    LD_LIBRARY_PATH=/usr/local/nvshmem/lib:$LD_LIBRARY_PATH \
    LIBRARY_PATH=/usr/local/nvshmem/lib:$LIBRARY_PATH \
    PATH=/usr/local/nvshmem/bin:$PATH''')

    @ubuntu
    @docker
    def test_package_ubuntu(self):
        """nvshmem source package"""
        n = nvshmem(package='nvshmem_src_2.9.0-2.tar.xz')
        self.assertEqual(str(n),
r'''# NVSHMEM
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        make \
        wget && \
    rm -rf /var/lib/apt/lists/*
COPY nvshmem_src_2.9.0-2.tar.xz /var/tmp/nvshmem_src_2.9.0-2.tar.xz
RUN mkdir -p /var/tmp && tar -x -f /var/tmp/nvshmem_src_2.9.0-2.tar.xz -C /var/tmp -J && \
    mkdir -p /var/tmp/nvshmem_src_2.9.0-2/build && cd /var/tmp/nvshmem_src_2.9.0-2/build && cmake -DCMAKE_INSTALL_PREFIX=/usr/local/nvshmem -DNVSHMEM_BUILD_EXAMPLES=OFF -DNVSHMEM_BUILD_PACKAGES=OFF -DNVSHMEM_BUILD_DEB_PACKAGES=OFF -DNVSHMEM_BUILD_RPM_PACKAGES=OFF -DCUDA_HOME=/usr/local/cuda /var/tmp/nvshmem_src_2.9.0-2 && \
    cmake --build /var/tmp/nvshmem_src_2.9.0-2/build --target all -- -j$(nproc) && \
    cmake --build /var/tmp/nvshmem_src_2.9.0-2/build --target install -- -j$(nproc) && \
    rm -rf /var/tmp/nvshmem_src_2.9.0-2 /var/tmp/nvshmem_src_2.9.0-2.tar.xz
ENV CPATH=/usr/local/nvshmem/include:$CPATH \
    LD_LIBRARY_PATH=/usr/local/nvshmem/lib:$LD_LIBRARY_PATH \
    LIBRARY_PATH=/usr/local/nvshmem/lib:$LIBRARY_PATH \
    PATH=/usr/local/nvshmem/bin:$PATH''')

    @centos
    @docker
    def test_cmake_options_centos(self):
        """nvshmem with cmake options"""
        n = nvshmem(cmake_opts=['-DNVSHMEM_USE_NCCL=1',
                                '-DNVSHMEM_UCX_SUPPORT=1'],
                    gdrcopy='/usr/local/gdrcopy',
                    mpi='/usr/local/openmpi',
                    shmem='/usr/local/openmpi',
                    version='2.9.0-2')
        self.assertEqual(str(n),
r'''# NVSHMEM 2.9.0-2
RUN yum install -y \
        make \
        wget && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://developer.download.nvidia.com/compute/redist/nvshmem/2.9.0/source/nvshmem_src_2.9.0-2.txz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/nvshmem_src_2.9.0-2.txz -C /var/tmp -J && \
    mkdir -p /var/tmp/nvshmem_src_2.9.0-2/build && cd /var/tmp/nvshmem_src_2.9.0-2/build && cmake -DCMAKE_INSTALL_PREFIX=/usr/local/nvshmem -DNVSHMEM_USE_NCCL=1 -DNVSHMEM_UCX_SUPPORT=1 -DNVSHMEM_BUILD_EXAMPLES=OFF -DNVSHMEM_BUILD_PACKAGES=OFF -DNVSHMEM_BUILD_DEB_PACKAGES=OFF -DNVSHMEM_BUILD_RPM_PACKAGES=OFF -DCUDA_HOME=/usr/local/cuda -DGDRCOPY_HOME=/usr/local/gdrcopy -DNVSHMEM_MPI_SUPPORT=1 -DMPI_HOME=/usr/local/openmpi -DNVSHMEM_SHMEM_SUPPORT=1 -DSHMEM_HOME=/usr/local/openmpi /var/tmp/nvshmem_src_2.9.0-2 && \
    cmake --build /var/tmp/nvshmem_src_2.9.0-2/build --target all -- -j$(nproc) && \
    cmake --build /var/tmp/nvshmem_src_2.9.0-2/build --target install -- -j$(nproc) && \
    rm -rf /var/tmp/nvshmem_src_2.9.0-2 /var/tmp/nvshmem_src_2.9.0-2.txz
ENV CPATH=/usr/local/nvshmem/include:$CPATH \
    LD_LIBRARY_PATH=/usr/local/nvshmem/lib:$LD_LIBRARY_PATH \
    LIBRARY_PATH=/usr/local/nvshmem/lib:$LIBRARY_PATH \
    PATH=/usr/local/nvshmem/bin:$PATH''')

    @ubuntu
    @docker
    def test_runtime(self):
        """Runtime"""
        n = nvshmem()
        r = n.runtime()
        self.assertEqual(r,
r'''# NVSHMEM
COPY --from=0 /usr/local/nvshmem /usr/local/nvshmem
ENV CPATH=/usr/local/nvshmem/include:$CPATH \
    LD_LIBRARY_PATH=/usr/local/nvshmem/lib:$LD_LIBRARY_PATH \
    LIBRARY_PATH=/usr/local/nvshmem/lib:$LIBRARY_PATH \
    PATH=/usr/local/nvshmem/bin:$PATH''')
