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

"""Test cases for the mvapich2_gdr module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import centos, docker, ubuntu

from hpccm.building_blocks.mvapich2_gdr import mvapich2_gdr

class Test_mvapich2_gdr(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @ubuntu
    @docker
    def test_defaults_ubuntu(self):
        """Default mvapich2_gdr building block"""
        mv2 = mvapich2_gdr()
        self.assertEqual(str(mv2),
r'''# MVAPICH2-GDR version 2.3.3
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        cpio \
        libgfortran3 \
        libnuma1 \
        libpciaccess0 \
        openssh-client \
        rpm2cpio \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp http://mvapich.cse.ohio-state.edu/download/mvapich/gdr/2.3.3/mofed4.5/mvapich2-gdr-mcast.cuda9.2.mofed4.5.gnu4.8.5-2.3.3-2.el7.x86_64.rpm && \
    cd / && rpm2cpio /var/tmp/mvapich2-gdr-mcast.cuda9.2.mofed4.5.gnu4.8.5-2.3.3-2.el7.x86_64.rpm | cpio -id && \
    (test -f /usr/bin/bash || ln -s /bin/bash /usr/bin/bash) && \
    ln -s /usr/local/cuda/lib64/stubs/nvidia-ml.so /usr/local/cuda/lib64/stubs/nvidia-ml.so.1 && \
    rm -rf /var/tmp/mvapich2-gdr-mcast.cuda9.2.mofed4.5.gnu4.8.5-2.3.3-2.el7.x86_64.rpm
ENV LD_LIBRARY_PATH=/opt/mvapich2/gdr/2.3.3/mcast/no-openacc/cuda9.2/mofed4.5/mpirun/gnu4.8.5/lib64:$LD_LIBRARY_PATH \
    PATH=/opt/mvapich2/gdr/2.3.3/mcast/no-openacc/cuda9.2/mofed4.5/mpirun/gnu4.8.5/bin:$PATH \
    PROFILE_POSTLIB="-L/usr/local/cuda/lib64/stubs -lnvidia-ml"''')

    @centos
    @docker
    def test_default_centos(self):
        """Default mvapich2_gdr building block"""
        mv2 = mvapich2_gdr()
        self.assertEqual(str(mv2),
r'''# MVAPICH2-GDR version 2.3.3
RUN yum install -y \
        libgfortran \
        libpciaccess \
        numactl-libs \
        openssh-clients \
        wget && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp http://mvapich.cse.ohio-state.edu/download/mvapich/gdr/2.3.3/mofed4.5/mvapich2-gdr-mcast.cuda9.2.mofed4.5.gnu4.8.5-2.3.3-2.el7.x86_64.rpm && \
    rpm --install --nodeps /var/tmp/mvapich2-gdr-mcast.cuda9.2.mofed4.5.gnu4.8.5-2.3.3-2.el7.x86_64.rpm && \
    (test -f /usr/bin/bash || ln -s /bin/bash /usr/bin/bash) && \
    ln -s /usr/local/cuda/lib64/stubs/nvidia-ml.so /usr/local/cuda/lib64/stubs/nvidia-ml.so.1 && \
    rm -rf /var/tmp/mvapich2-gdr-mcast.cuda9.2.mofed4.5.gnu4.8.5-2.3.3-2.el7.x86_64.rpm
ENV LD_LIBRARY_PATH=/opt/mvapich2/gdr/2.3.3/mcast/no-openacc/cuda9.2/mofed4.5/mpirun/gnu4.8.5/lib64:$LD_LIBRARY_PATH \
    PATH=/opt/mvapich2/gdr/2.3.3/mcast/no-openacc/cuda9.2/mofed4.5/mpirun/gnu4.8.5/bin:$PATH \
    PROFILE_POSTLIB="-L/usr/local/cuda/lib64/stubs -lnvidia-ml"''')

    @ubuntu
    @docker
    def test_ldconfig(self):
        """ldconfig option"""
        mv2 = mvapich2_gdr(ldconfig=True)
        self.assertEqual(str(mv2),
r'''# MVAPICH2-GDR version 2.3.3
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        cpio \
        libgfortran3 \
        libnuma1 \
        libpciaccess0 \
        openssh-client \
        rpm2cpio \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp http://mvapich.cse.ohio-state.edu/download/mvapich/gdr/2.3.3/mofed4.5/mvapich2-gdr-mcast.cuda9.2.mofed4.5.gnu4.8.5-2.3.3-2.el7.x86_64.rpm && \
    cd / && rpm2cpio /var/tmp/mvapich2-gdr-mcast.cuda9.2.mofed4.5.gnu4.8.5-2.3.3-2.el7.x86_64.rpm | cpio -id && \
    (test -f /usr/bin/bash || ln -s /bin/bash /usr/bin/bash) && \
    ln -s /usr/local/cuda/lib64/stubs/nvidia-ml.so /usr/local/cuda/lib64/stubs/nvidia-ml.so.1 && \
    rm -rf /var/tmp/mvapich2-gdr-mcast.cuda9.2.mofed4.5.gnu4.8.5-2.3.3-2.el7.x86_64.rpm && \
    echo "/opt/mvapich2/gdr/2.3.3/mcast/no-openacc/cuda9.2/mofed4.5/mpirun/gnu4.8.5/lib64" >> /etc/ld.so.conf.d/hpccm.conf && ldconfig
ENV PATH=/opt/mvapich2/gdr/2.3.3/mcast/no-openacc/cuda9.2/mofed4.5/mpirun/gnu4.8.5/bin:$PATH \
    PROFILE_POSTLIB="-L/usr/local/cuda/lib64/stubs -lnvidia-ml"''')

    @ubuntu
    @docker
    def test_options(self):
        """PGI compiler and different Mellanox OFED version"""
        mv2 = mvapich2_gdr(pgi=True, gnu=False, cuda_version='9.2',
                           mlnx_ofed_version='3.4', pgi_version='17.10',
                           release='1', version='2.3')
        self.assertEqual(str(mv2),
r'''# MVAPICH2-GDR version 2.3
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        cpio \
        libnuma1 \
        libpciaccess0 \
        openssh-client \
        rpm2cpio \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp http://mvapich.cse.ohio-state.edu/download/mvapich/gdr/2.3/mofed3.4/mvapich2-gdr-mcast.cuda9.2.mofed3.4.pgi17.10-2.3-1.el7.x86_64.rpm && \
    cd / && rpm2cpio /var/tmp/mvapich2-gdr-mcast.cuda9.2.mofed3.4.pgi17.10-2.3-1.el7.x86_64.rpm | cpio -id && \
    (test -f /usr/bin/bash || ln -s /bin/bash /usr/bin/bash) && \
    ln -s /usr/local/cuda/lib64/stubs/nvidia-ml.so /usr/local/cuda/lib64/stubs/nvidia-ml.so.1 && \
    rm -rf /var/tmp/mvapich2-gdr-mcast.cuda9.2.mofed3.4.pgi17.10-2.3-1.el7.x86_64.rpm
ENV LD_LIBRARY_PATH=/opt/mvapich2/gdr/2.3/mcast/no-openacc/cuda9.2/mofed3.4/mpirun/pgi17.10/lib64:$LD_LIBRARY_PATH \
    PATH=/opt/mvapich2/gdr/2.3/mcast/no-openacc/cuda9.2/mofed3.4/mpirun/pgi17.10/bin:$PATH \
    PROFILE_POSTLIB="-L/usr/local/cuda/lib64/stubs -lnvidia-ml"''')

    @ubuntu
    @docker
    def test_package(self):
        """Manually specified download package"""
        mv2 = mvapich2_gdr(package='mvapich2-gdr-mcast.cuda10.0.mofed4.3.gnu4.8.5-2.3-1.el7.x86_64.rpm')
        self.assertEqual(str(mv2),
r'''# MVAPICH2-GDR version 2.3
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        cpio \
        libgfortran3 \
        libnuma1 \
        libpciaccess0 \
        openssh-client \
        rpm2cpio \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp http://mvapich.cse.ohio-state.edu/download/mvapich/gdr/2.3/mofed4.3/mvapich2-gdr-mcast.cuda10.0.mofed4.3.gnu4.8.5-2.3-1.el7.x86_64.rpm && \
    cd / && rpm2cpio /var/tmp/mvapich2-gdr-mcast.cuda10.0.mofed4.3.gnu4.8.5-2.3-1.el7.x86_64.rpm | cpio -id && \
    (test -f /usr/bin/bash || ln -s /bin/bash /usr/bin/bash) && \
    ln -s /usr/local/cuda/lib64/stubs/nvidia-ml.so /usr/local/cuda/lib64/stubs/nvidia-ml.so.1 && \
    rm -rf /var/tmp/mvapich2-gdr-mcast.cuda10.0.mofed4.3.gnu4.8.5-2.3-1.el7.x86_64.rpm
ENV LD_LIBRARY_PATH=/opt/mvapich2/gdr/2.3/mcast/no-openacc/cuda10.0/mofed4.3/mpirun/gnu4.8.5/lib64:$LD_LIBRARY_PATH \
    PATH=/opt/mvapich2/gdr/2.3/mcast/no-openacc/cuda10.0/mofed4.3/mpirun/gnu4.8.5/bin:$PATH \
    PROFILE_POSTLIB="-L/usr/local/cuda/lib64/stubs -lnvidia-ml"''')

    @ubuntu
    @docker
    def test_runtime(self):
        """Runtime"""
        mv2 = mvapich2_gdr()
        r = mv2.runtime()
        self.assertEqual(r,
r'''# MVAPICH2-GDR
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libgfortran3 \
        libnuma1 \
        libpciaccess0 \
        openssh-client && \
    rm -rf /var/lib/apt/lists/*
COPY --from=0 /opt/mvapich2/gdr/2.3.3/mcast/no-openacc/cuda9.2/mofed4.5/mpirun/gnu4.8.5 /opt/mvapich2/gdr/2.3.3/mcast/no-openacc/cuda9.2/mofed4.5/mpirun/gnu4.8.5
ENV LD_LIBRARY_PATH=/opt/mvapich2/gdr/2.3.3/mcast/no-openacc/cuda9.2/mofed4.5/mpirun/gnu4.8.5/lib64:$LD_LIBRARY_PATH \
    PATH=/opt/mvapich2/gdr/2.3.3/mcast/no-openacc/cuda9.2/mofed4.5/mpirun/gnu4.8.5/bin:$PATH''')

    def test_toolchain(self):
        """Toolchain"""
        mv2 = mvapich2_gdr()
        tc = mv2.toolchain
        self.assertEqual(tc.CC, 'mpicc')
        self.assertEqual(tc.CXX, 'mpicxx')
        self.assertEqual(tc.FC, 'mpifort')
        self.assertEqual(tc.F77, 'mpif77')
        self.assertEqual(tc.F90, 'mpif90')
