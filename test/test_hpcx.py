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

"""Test cases for the hpcx module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import aarch64, centos, centos8, docker, ppc64le, ubuntu, ubuntu18, x86_64

from hpccm.building_blocks.hpcx import hpcx

class Test_mlnx_ofed(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @x86_64
    @ubuntu
    @docker
    def test_defaults_ubuntu(self):
        """Default hpcx building block"""
        h = hpcx()
        self.assertEqual(str(h),
r'''# Mellanox HPC-X version 2.6.0
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        bzip2 \
        openssh-client \
        tar \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp http://www.mellanox.com/downloads/hpc/hpc-x/v2.6/hpcx-v2.6.0-gcc-MLNX_OFED_LINUX-4.7-1.0.0.1-ubuntu16.04-x86_64.tbz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/hpcx-v2.6.0-gcc-MLNX_OFED_LINUX-4.7-1.0.0.1-ubuntu16.04-x86_64.tbz -C /var/tmp -j && \
    cp -a /var/tmp/hpcx-v2.6.0-gcc-MLNX_OFED_LINUX-4.7-1.0.0.1-ubuntu16.04-x86_64 /usr/local/hpcx && \
    echo "source /usr/local/hpcx/hpcx-init-ompi.sh" >> /etc/bash.bashrc && \
    echo "hpcx_load" >> /etc/bash.bashrc && \
    rm -rf /var/tmp/hpcx-v2.6.0-gcc-MLNX_OFED_LINUX-4.7-1.0.0.1-ubuntu16.04-x86_64.tbz /var/tmp/hpcx-v2.6.0-gcc-MLNX_OFED_LINUX-4.7-1.0.0.1-ubuntu16.04-x86_64''')

    @x86_64
    @ubuntu18
    @docker
    def test_defaults_ubuntu18(self):
        """Default hpcx building block"""
        h = hpcx()
        self.assertEqual(str(h),
r'''# Mellanox HPC-X version 2.6.0
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        bzip2 \
        openssh-client \
        tar \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp http://www.mellanox.com/downloads/hpc/hpc-x/v2.6/hpcx-v2.6.0-gcc-MLNX_OFED_LINUX-4.7-1.0.0.1-ubuntu18.04-x86_64.tbz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/hpcx-v2.6.0-gcc-MLNX_OFED_LINUX-4.7-1.0.0.1-ubuntu18.04-x86_64.tbz -C /var/tmp -j && \
    cp -a /var/tmp/hpcx-v2.6.0-gcc-MLNX_OFED_LINUX-4.7-1.0.0.1-ubuntu18.04-x86_64 /usr/local/hpcx && \
    echo "source /usr/local/hpcx/hpcx-init-ompi.sh" >> /etc/bash.bashrc && \
    echo "hpcx_load" >> /etc/bash.bashrc && \
    rm -rf /var/tmp/hpcx-v2.6.0-gcc-MLNX_OFED_LINUX-4.7-1.0.0.1-ubuntu18.04-x86_64.tbz /var/tmp/hpcx-v2.6.0-gcc-MLNX_OFED_LINUX-4.7-1.0.0.1-ubuntu18.04-x86_64''')

    @x86_64
    @centos
    @docker
    def test_defaults_centos7(self):
        """Default mlnx_ofed building block"""
        h = hpcx()
        self.assertEqual(str(h),
r'''# Mellanox HPC-X version 2.6.0
RUN yum install -y \
        bzip2 \
        openssh-clients \
        tar \
        wget && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp http://www.mellanox.com/downloads/hpc/hpc-x/v2.6/hpcx-v2.6.0-gcc-MLNX_OFED_LINUX-4.7-1.0.0.1-redhat7.6-x86_64.tbz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/hpcx-v2.6.0-gcc-MLNX_OFED_LINUX-4.7-1.0.0.1-redhat7.6-x86_64.tbz -C /var/tmp -j && \
    cp -a /var/tmp/hpcx-v2.6.0-gcc-MLNX_OFED_LINUX-4.7-1.0.0.1-redhat7.6-x86_64 /usr/local/hpcx && \
    echo "source /usr/local/hpcx/hpcx-init-ompi.sh" >> /etc/bashrc && \
    echo "hpcx_load" >> /etc/bashrc && \
    rm -rf /var/tmp/hpcx-v2.6.0-gcc-MLNX_OFED_LINUX-4.7-1.0.0.1-redhat7.6-x86_64.tbz /var/tmp/hpcx-v2.6.0-gcc-MLNX_OFED_LINUX-4.7-1.0.0.1-redhat7.6-x86_64''')

    @x86_64
    @centos8
    @docker
    def test_defaults_centos8(self):
        """Default mlnx_ofed building block"""
        h = hpcx()
        self.assertEqual(str(h),
r'''# Mellanox HPC-X version 2.6.0
RUN yum install -y \
        bzip2 \
        openssh-clients \
        tar \
        wget && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp http://www.mellanox.com/downloads/hpc/hpc-x/v2.6/hpcx-v2.6.0-gcc-MLNX_OFED_LINUX-4.7-1.0.0.1-redhat8.0-x86_64.tbz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/hpcx-v2.6.0-gcc-MLNX_OFED_LINUX-4.7-1.0.0.1-redhat8.0-x86_64.tbz -C /var/tmp -j && \
    cp -a /var/tmp/hpcx-v2.6.0-gcc-MLNX_OFED_LINUX-4.7-1.0.0.1-redhat8.0-x86_64 /usr/local/hpcx && \
    echo "source /usr/local/hpcx/hpcx-init-ompi.sh" >> /etc/bashrc && \
    echo "hpcx_load" >> /etc/bashrc && \
    rm -rf /var/tmp/hpcx-v2.6.0-gcc-MLNX_OFED_LINUX-4.7-1.0.0.1-redhat8.0-x86_64.tbz /var/tmp/hpcx-v2.6.0-gcc-MLNX_OFED_LINUX-4.7-1.0.0.1-redhat8.0-x86_64''')

    @x86_64
    @ubuntu
    @docker
    def test_prefix_multi_thread(self):
        """Prefix and multi_thread options"""
        h = hpcx(multi_thread=True, prefix='/opt/hpcx', version='2.5.0')
        self.assertEqual(str(h),
r'''# Mellanox HPC-X version 2.5.0
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        bzip2 \
        openssh-client \
        tar \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp http://www.mellanox.com/downloads/hpc/hpc-x/v2.5/hpcx-v2.5.0-gcc-MLNX_OFED_LINUX-4.7-1.0.0.1-ubuntu16.04-x86_64.tbz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/hpcx-v2.5.0-gcc-MLNX_OFED_LINUX-4.7-1.0.0.1-ubuntu16.04-x86_64.tbz -C /var/tmp -j && \
    cp -a /var/tmp/hpcx-v2.5.0-gcc-MLNX_OFED_LINUX-4.7-1.0.0.1-ubuntu16.04-x86_64 /opt/hpcx && \
    echo "source /opt/hpcx/hpcx-mt-init-ompi.sh" >> /etc/bash.bashrc && \
    echo "hpcx_load" >> /etc/bash.bashrc && \
    rm -rf /var/tmp/hpcx-v2.5.0-gcc-MLNX_OFED_LINUX-4.7-1.0.0.1-ubuntu16.04-x86_64.tbz /var/tmp/hpcx-v2.5.0-gcc-MLNX_OFED_LINUX-4.7-1.0.0.1-ubuntu16.04-x86_64''')

    @aarch64
    @ubuntu
    @docker
    def test_aarch64_ubuntu(self):
        """aarch64"""
        h = hpcx(mlnx_ofed='4.5-1.0.1.0', version='2.5.0')
        self.assertEqual(str(h),
r'''# Mellanox HPC-X version 2.5.0
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        bzip2 \
        openssh-client \
        tar \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp http://www.mellanox.com/downloads/hpc/hpc-x/v2.5/hpcx-v2.5.0-gcc-MLNX_OFED_LINUX-4.5-1.0.1.0-ubuntu16.04-aarch64.tbz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/hpcx-v2.5.0-gcc-MLNX_OFED_LINUX-4.5-1.0.1.0-ubuntu16.04-aarch64.tbz -C /var/tmp -j && \
    cp -a /var/tmp/hpcx-v2.5.0-gcc-MLNX_OFED_LINUX-4.5-1.0.1.0-ubuntu16.04-aarch64 /usr/local/hpcx && \
    echo "source /usr/local/hpcx/hpcx-init-ompi.sh" >> /etc/bash.bashrc && \
    echo "hpcx_load" >> /etc/bash.bashrc && \
    rm -rf /var/tmp/hpcx-v2.5.0-gcc-MLNX_OFED_LINUX-4.5-1.0.1.0-ubuntu16.04-aarch64.tbz /var/tmp/hpcx-v2.5.0-gcc-MLNX_OFED_LINUX-4.5-1.0.1.0-ubuntu16.04-aarch64''')

    @ppc64le
    @centos
    @docker
    def test_ppc64le_centos(self):
        """ppc64le"""
        h = hpcx(version='2.5.0')
        self.assertEqual(str(h),
r'''# Mellanox HPC-X version 2.5.0
RUN yum install -y \
        bzip2 \
        openssh-clients \
        tar \
        wget && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp http://www.mellanox.com/downloads/hpc/hpc-x/v2.5/hpcx-v2.5.0-gcc-MLNX_OFED_LINUX-4.7-1.0.0.1-redhat7.6-ppc64le.tbz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/hpcx-v2.5.0-gcc-MLNX_OFED_LINUX-4.7-1.0.0.1-redhat7.6-ppc64le.tbz -C /var/tmp -j && \
    cp -a /var/tmp/hpcx-v2.5.0-gcc-MLNX_OFED_LINUX-4.7-1.0.0.1-redhat7.6-ppc64le /usr/local/hpcx && \
    echo "source /usr/local/hpcx/hpcx-init-ompi.sh" >> /etc/bashrc && \
    echo "hpcx_load" >> /etc/bashrc && \
    rm -rf /var/tmp/hpcx-v2.5.0-gcc-MLNX_OFED_LINUX-4.7-1.0.0.1-redhat7.6-ppc64le.tbz /var/tmp/hpcx-v2.5.0-gcc-MLNX_OFED_LINUX-4.7-1.0.0.1-redhat7.6-ppc64le''')

    @x86_64
    @ubuntu18
    @docker
    def test_inbox_hpcxinit(self):
        """inbox and hpcxinit parameters"""
        h = hpcx(hpcxinit=False, inbox=True, version='2.5.0')
        self.assertEqual(str(h),
r'''# Mellanox HPC-X version 2.5.0
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        bzip2 \
        openssh-client \
        tar \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp http://www.mellanox.com/downloads/hpc/hpc-x/v2.5/hpcx-v2.5.0-gcc-inbox-ubuntu18.04-x86_64.tbz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/hpcx-v2.5.0-gcc-inbox-ubuntu18.04-x86_64.tbz -C /var/tmp -j && \
    cp -a /var/tmp/hpcx-v2.5.0-gcc-inbox-ubuntu18.04-x86_64 /usr/local/hpcx && \
    rm -rf /var/tmp/hpcx-v2.5.0-gcc-inbox-ubuntu18.04-x86_64.tbz /var/tmp/hpcx-v2.5.0-gcc-inbox-ubuntu18.04-x86_64
ENV CPATH=/usr/local/hpcx/hcoll/include:/usr/local/hpcx/ompi/include:/usr/local/hpcx/sharp/include:/usr/local/hpcx/ucx/include:$CPATH \
    HPCX_CLUSTERKIT_DIR=/usr/local/hpcx/clusterkit \
    HPCX_DIR=/usr/local/hpcx \
    HPCX_HCOLL_DIR=/usr/local/hpcx/hcoll \
    HPCX_IPM_DIR=/usr/local/hpcx/ompi/tests/ipm-2.0.6 \
    HPCX_IPM_LIB=/usr/local/hpcx/ompi/tests/ipm-2.0.6/lib/libipm.so \
    HPCX_MPI_DIR=/usr/local/hpcx/ompi \
    HPCX_MPI_TESTS_DIR=/usr/local/hpcx/ompi/tests \
    HPCX_NCCL_RDMA_SHARP_PLUGIN_DIR=/usr/local/hpcx/nccl_rdma_sharp_plugin \
    HPCX_OSHMEM_DIR=/usr/local/hpcx/ompi \
    HPCX_OSU_CUDA_DIR=/usr/local/hpcx/ompi/tests/osu-micro-benchmarks-5.3.2-cuda \
    HPCX_OSU_DIR=/usr/local/hpcx/ompi/tests/osu-micro-benchmarks-5.3.2 \
    HPCX_SHARP_DIR=/usr/local/hpcx/sharp \
    HPCX_UCX_DIR=/usr/local/hpcx/ucx \
    LD_LIBRARY_PATH=/usr/local/hpcx/hcoll/lib:/usr/local/hpcx/ompi/lib:/usr/local/hpcx/nccl_rdma_sharp_plugin/lib:/usr/local/hpcx/sharp/lib:/usr/local/hpcx/ucx/lib:/usr/local/hpcx/ucx/lib/ucx:$LD_LIBRARY_PATH \
    LIBRARY_PATH=/usr/local/hpcx/hcoll/lib:/usr/local/hpcx/ompi/lib:/usr/local/hpcx/nccl_rdma_sharp_plugin/lib:/usr/local/hpcx/sharp/lib:/usr/local/hpcx/ucx/lib:$LIBRARY_PATH \
    MPI_HOME=/usr/local/hpcx/ompi \
    OMPI_HOME=/usr/local/hpcx/ompi \
    OPAL_PREFIX=/usr/local/hpcx/ompi \
    OSHMEM_HOME=/usr/local/hpcx/ompi \
    PATH=/usr/local/hpcx/clusterkit/bin:/usr/local/hpcx/hcoll/bin:/usr/local/hpcx/ompi/bin:/usr/local/hpcx/ucx/bin:$PATH \
    PKG_CONFIG_PATH=/usr/local/hpcx/hcoll/lib/pkgconfig:/usr/local/hpcx/ompi/lib/pkgconfig:/usr/local/hpcx/sharp/lib/pkgconfig:/usr/local/hpcx/ucx/lib/pkgconfig:$PKG_CONFIG_PATH \
    SHMEM_HOME=/usr/local/hpcx/ompi''')

    @x86_64
    @centos
    @docker
    def test_ldconfig_multi_thread(self):
        """ldconfig and multi_thread parameters"""
        h = hpcx(hpcxinit=False, ldconfig=True, mlnx_ofed='4.6-1.0.1.1',
                 multi_thread=True, version='2.5.0')
        self.assertEqual(str(h),
r'''# Mellanox HPC-X version 2.5.0
RUN yum install -y \
        bzip2 \
        openssh-clients \
        tar \
        wget && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp http://www.mellanox.com/downloads/hpc/hpc-x/v2.5/hpcx-v2.5.0-gcc-MLNX_OFED_LINUX-4.6-1.0.1.1-redhat7.6-x86_64.tbz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/hpcx-v2.5.0-gcc-MLNX_OFED_LINUX-4.6-1.0.1.1-redhat7.6-x86_64.tbz -C /var/tmp -j && \
    cp -a /var/tmp/hpcx-v2.5.0-gcc-MLNX_OFED_LINUX-4.6-1.0.1.1-redhat7.6-x86_64 /usr/local/hpcx && \
    echo "/usr/local/hpcx/hcoll/lib" >> /etc/ld.so.conf.d/hpccm.conf && ldconfig && \
    echo "/usr/local/hpcx/ompi/lib" >> /etc/ld.so.conf.d/hpccm.conf && ldconfig && \
    echo "/usr/local/hpcx/nccl_rdma_sharp_plugin/lib" >> /etc/ld.so.conf.d/hpccm.conf && ldconfig && \
    echo "/usr/local/hpcx/sharp/lib" >> /etc/ld.so.conf.d/hpccm.conf && ldconfig && \
    echo "/usr/local/hpcx/ucx/mt/lib" >> /etc/ld.so.conf.d/hpccm.conf && ldconfig && \
    echo "/usr/local/hpcx/ucx/mt/lib/ucx" >> /etc/ld.so.conf.d/hpccm.conf && ldconfig && \
    rm -rf /var/tmp/hpcx-v2.5.0-gcc-MLNX_OFED_LINUX-4.6-1.0.1.1-redhat7.6-x86_64.tbz /var/tmp/hpcx-v2.5.0-gcc-MLNX_OFED_LINUX-4.6-1.0.1.1-redhat7.6-x86_64
ENV CPATH=/usr/local/hpcx/hcoll/include:/usr/local/hpcx/ompi/include:/usr/local/hpcx/sharp/include:/usr/local/hpcx/ucx/mt/include:$CPATH \
    HPCX_CLUSTERKIT_DIR=/usr/local/hpcx/clusterkit \
    HPCX_DIR=/usr/local/hpcx \
    HPCX_HCOLL_DIR=/usr/local/hpcx/hcoll \
    HPCX_IPM_DIR=/usr/local/hpcx/ompi/tests/ipm-2.0.6 \
    HPCX_IPM_LIB=/usr/local/hpcx/ompi/tests/ipm-2.0.6/lib/libipm.so \
    HPCX_MPI_DIR=/usr/local/hpcx/ompi \
    HPCX_MPI_TESTS_DIR=/usr/local/hpcx/ompi/tests \
    HPCX_NCCL_RDMA_SHARP_PLUGIN_DIR=/usr/local/hpcx/nccl_rdma_sharp_plugin \
    HPCX_OSHMEM_DIR=/usr/local/hpcx/ompi \
    HPCX_OSU_CUDA_DIR=/usr/local/hpcx/ompi/tests/osu-micro-benchmarks-5.3.2-cuda \
    HPCX_OSU_DIR=/usr/local/hpcx/ompi/tests/osu-micro-benchmarks-5.3.2 \
    HPCX_SHARP_DIR=/usr/local/hpcx/sharp \
    HPCX_UCX_DIR=/usr/local/hpcx/ucx/mt \
    LIBRARY_PATH=/usr/local/hpcx/hcoll/lib:/usr/local/hpcx/ompi/lib:/usr/local/hpcx/nccl_rdma_sharp_plugin/lib:/usr/local/hpcx/sharp/lib:/usr/local/hpcx/ucx/mt/lib:$LIBRARY_PATH \
    MPI_HOME=/usr/local/hpcx/ompi \
    OMPI_HOME=/usr/local/hpcx/ompi \
    OPAL_PREFIX=/usr/local/hpcx/ompi \
    OSHMEM_HOME=/usr/local/hpcx/ompi \
    PATH=/usr/local/hpcx/clusterkit/bin:/usr/local/hpcx/hcoll/bin:/usr/local/hpcx/ompi/bin:/usr/local/hpcx/ucx/mt/bin:$PATH \
    PKG_CONFIG_PATH=/usr/local/hpcx/hcoll/lib/pkgconfig:/usr/local/hpcx/ompi/lib/pkgconfig:/usr/local/hpcx/sharp/lib/pkgconfig:/usr/local/hpcx/ucx/mt/lib/pkgconfig:$PKG_CONFIG_PATH \
    SHMEM_HOME=/usr/local/hpcx/ompi''')

    @x86_64
    @ubuntu
    @docker
    def test_runtime(self):
        """Runtime"""
        h = hpcx()
        r = h.runtime()
        self.assertEqual(r,
r'''# Mellanox HPC-X version 2.6.0
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        bzip2 \
        openssh-client \
        tar \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp http://www.mellanox.com/downloads/hpc/hpc-x/v2.6/hpcx-v2.6.0-gcc-MLNX_OFED_LINUX-4.7-1.0.0.1-ubuntu16.04-x86_64.tbz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/hpcx-v2.6.0-gcc-MLNX_OFED_LINUX-4.7-1.0.0.1-ubuntu16.04-x86_64.tbz -C /var/tmp -j && \
    cp -a /var/tmp/hpcx-v2.6.0-gcc-MLNX_OFED_LINUX-4.7-1.0.0.1-ubuntu16.04-x86_64 /usr/local/hpcx && \
    echo "source /usr/local/hpcx/hpcx-init-ompi.sh" >> /etc/bash.bashrc && \
    echo "hpcx_load" >> /etc/bash.bashrc && \
    rm -rf /var/tmp/hpcx-v2.6.0-gcc-MLNX_OFED_LINUX-4.7-1.0.0.1-ubuntu16.04-x86_64.tbz /var/tmp/hpcx-v2.6.0-gcc-MLNX_OFED_LINUX-4.7-1.0.0.1-ubuntu16.04-x86_64''')
