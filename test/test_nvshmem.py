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
    def test_binary_tarball_ubuntu(self):
        """nvshmem binary tarball"""
        n = nvshmem(binary_tarball='nvshmem_0.4.1-0+cuda10_x86_64.txz')
        self.assertEqual(str(n),
r'''# NVSHMEM
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        make \
        wget && \
    rm -rf /var/lib/apt/lists/*
COPY nvshmem_0.4.1-0+cuda10_x86_64.txz /var/tmp/nvshmem_0.4.1-0+cuda10_x86_64.txz
RUN mkdir -p /usr/local/nvshmem && tar -x -f /var/tmp/nvshmem_0.4.1-0+cuda10_x86_64.txz -C /usr/local/nvshmem -J --strip-components=1 && \
    rm -rf /var/tmp/nvshmem_0.4.1-0+cuda10_x86_64.txz
ENV CPATH=/usr/local/nvshmem/include:$CPATH \
    LIBRARY_PATH=/usr/local/nvshmem/lib:$LIBRARY_PATH \
    PATH=/usr/local/nvshmem/bin:$PATH''')

    @centos
    @docker
    def test_binary_tarball_centos(self):
        """nvshmem binary tarball"""
        n = nvshmem(binary_tarball='nvshmem_0.4.1-0+cuda10_x86_64.txz')
        self.assertEqual(str(n),
r'''# NVSHMEM
RUN yum install -y \
        make \
        wget && \
    rm -rf /var/cache/yum/*
COPY nvshmem_0.4.1-0+cuda10_x86_64.txz /var/tmp/nvshmem_0.4.1-0+cuda10_x86_64.txz
RUN mkdir -p /usr/local/nvshmem && tar -x -f /var/tmp/nvshmem_0.4.1-0+cuda10_x86_64.txz -C /usr/local/nvshmem -J --strip-components=1 && \
    rm -rf /var/tmp/nvshmem_0.4.1-0+cuda10_x86_64.txz
ENV CPATH=/usr/local/nvshmem/include:$CPATH \
    LIBRARY_PATH=/usr/local/nvshmem/lib:$LIBRARY_PATH \
    PATH=/usr/local/nvshmem/bin:$PATH''')

    @ubuntu
    @docker
    def test_package_ubuntu(self):
        """nvshmem source package"""
        n = nvshmem(package='nvshmem-0.3.2EA.tar.gz')
        self.assertEqual(str(n),
r'''# NVSHMEM
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        make \
        wget && \
    rm -rf /var/lib/apt/lists/*
COPY nvshmem-0.3.2EA.tar.gz /var/tmp/nvshmem-0.3.2EA.tar.gz
RUN mkdir -p /var/tmp && tar -x -f /var/tmp/nvshmem-0.3.2EA.tar.gz -C /var/tmp -z && \
    cd /var/tmp/nvshmem-0.3.2EA && \
    NVSHMEM_PREFIX=/usr/local/nvshmem make -j$(nproc) install && \
    rm -rf /var/tmp/nvshmem-0.3.2EA /var/tmp/nvshmem-0.3.2EA.tar.gz
ENV CPATH=/usr/local/nvshmem/include:$CPATH \
    LIBRARY_PATH=/usr/local/nvshmem/lib:$LIBRARY_PATH \
    PATH=/usr/local/nvshmem/bin:$PATH''')

    @centos
    @docker
    def test_package_options_centos(self):
        """nvshmem source package with all options"""
        n = nvshmem(gdrcopy='/usr/local/gdrcopy', hydra=True,
                    make_variables={
                        'NVCC_GENCODE': '-gencode=arch=compute_70,code=sm_70',
                        'NVSHMEM_VERBOSE': 1},
                    mpi='/usr/local/openmpi',
                    package='nvshmem-0.3.2EA.tar.gz',
                    shmem='/usr/local/openmpi')
        self.assertEqual(str(n),
r'''# NVSHMEM
RUN yum install -y \
        automake \
        make \
        wget && \
    rm -rf /var/cache/yum/*
COPY nvshmem-0.3.2EA.tar.gz /var/tmp/nvshmem-0.3.2EA.tar.gz
RUN mkdir -p /var/tmp && tar -x -f /var/tmp/nvshmem-0.3.2EA.tar.gz -C /var/tmp -z && \
    cd /var/tmp/nvshmem-0.3.2EA && \
    GDRCOPY_HOME=/usr/local/gdrcopy MPI_HOME=/usr/local/openmpi NVCC_GENCODE=-gencode=arch=compute_70,code=sm_70 NVSHMEM_MPI_SUPPORT=1 NVSHMEM_PREFIX=/usr/local/nvshmem NVSHMEM_SHMEM_SUPPORT=1 NVSHMEM_VERBOSE=1 SHMEM_HOME=/usr/local/openmpi make -j$(nproc) install && \
    ./scripts/install_hydra.sh /var/tmp /usr/local/nvshmem && \
    rm -rf /var/tmp/nvshmem-0.3.2EA /var/tmp/nvshmem-0.3.2EA.tar.gz
ENV CPATH=/usr/local/nvshmem/include:$CPATH \
    LIBRARY_PATH=/usr/local/nvshmem/lib:$LIBRARY_PATH \
    PATH=/usr/local/nvshmem/bin:$PATH''')

    @ubuntu
    @docker
    def test_binary_runtime(self):
        """Runtime"""
        n = nvshmem(binary_tarball='nvshmem_0.4.1-0+cuda10_x86_64.txz')
        r = n.runtime()
        self.assertEqual(r,
r'''# NVSHMEM
COPY --from=0 /usr/local/nvshmem /usr/local/nvshmem
ENV CPATH=/usr/local/nvshmem/include:$CPATH \
    LIBRARY_PATH=/usr/local/nvshmem/lib:$LIBRARY_PATH \
    PATH=/usr/local/nvshmem/bin:$PATH''')

    @ubuntu
    @docker
    def test_source_runtime(self):
        """Runtime"""
        n = nvshmem(package='nvshmem-0.3.2EA.tar.gz')
        r = n.runtime()
        self.assertEqual(r,
r'''# NVSHMEM
COPY --from=0 /usr/local/nvshmem /usr/local/nvshmem
ENV CPATH=/usr/local/nvshmem/include:$CPATH \
    LIBRARY_PATH=/usr/local/nvshmem/lib:$LIBRARY_PATH \
    PATH=/usr/local/nvshmem/bin:$PATH''')
