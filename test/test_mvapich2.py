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

"""Test cases for the mvapich2 module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import centos, docker, ubuntu

from hpccm.building_blocks.mvapich2 import mvapich2
from hpccm.toolchain import toolchain

class Test_mvapich2(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @ubuntu
    @docker
    def test_defaults_ubuntu(self):
        """Default mvapich2 building block"""
        mv2 = mvapich2()
        self.assertEqual(str(mv2),
r'''# MVAPICH2 version 2.3.3
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        byacc \
        file \
        make \
        openssh-client \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp http://mvapich.cse.ohio-state.edu/download/mvapich/mv2/mvapich2-2.3.3.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/mvapich2-2.3.3.tar.gz -C /var/tmp -z && \
    cd /var/tmp/mvapich2-2.3.3 && \
    ln -s /usr/local/cuda/lib64/stubs/libnvidia-ml.so /usr/local/cuda/lib64/stubs/libnvidia-ml.so.1 && \
    ln -s /usr/local/cuda/lib64/stubs/libcuda.so /usr/local/cuda/lib64/stubs/libcuda.so.1 && \
    cd /var/tmp/mvapich2-2.3.3 &&  LD_LIBRARY_PATH='/usr/local/cuda/lib64/stubs:$LD_LIBRARY_PATH' ./configure --prefix=/usr/local/mvapich2 --disable-mcast --enable-cuda --with-cuda=/usr/local/cuda && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/mvapich2-2.3.3 /var/tmp/mvapich2-2.3.3.tar.gz
ENV LD_LIBRARY_PATH=/usr/local/mvapich2/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/mvapich2/bin:$PATH \
    PROFILE_POSTLIB="-L/usr/local/cuda/lib64/stubs -lnvidia-ml -lcuda"''')

    @ubuntu
    @docker
    def test_pgi_cuda(self):
        """mvapich2 with pgi and cuda"""
        tc = toolchain()
        tc.CC = 'pgcc'
        tc.CXX = 'pgc++'
        tc.F77 = 'pgfortran'
        tc.FC = 'pgfortran'
        mv2 = mvapich2(toolchain=tc, cuda=True)
        self.assertEqual(str(mv2),
r'''# MVAPICH2 version 2.3.3
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        byacc \
        file \
        make \
        openssh-client \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp http://mvapich.cse.ohio-state.edu/download/mvapich/mv2/mvapich2-2.3.3.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/mvapich2-2.3.3.tar.gz -C /var/tmp -z && \
    cd /var/tmp/mvapich2-2.3.3 && \
    ln -s /usr/local/cuda/lib64/stubs/libnvidia-ml.so /usr/local/cuda/lib64/stubs/libnvidia-ml.so.1 && \
    ln -s /usr/local/cuda/lib64/stubs/libcuda.so /usr/local/cuda/lib64/stubs/libcuda.so.1 && \
    cd /var/tmp/mvapich2-2.3.3 &&  CC=pgcc CFLAGS=-ta=tesla:nordc CPPFLAGS='-D__x86_64 -D__align__\(n\)=__attribute__\(\(aligned\(n\)\)\) -D__location__\(a\)=__annotate__\(a\) -DCUDARTAPI=' CXX=pgc++ F77=pgfortran FC=pgfortran LD_LIBRARY_PATH='/usr/local/cuda/lib64/stubs:$LD_LIBRARY_PATH' ./configure --prefix=/usr/local/mvapich2 --disable-mcast --enable-cuda=basic --with-cuda=/usr/local/cuda --enable-fast=O1 && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/mvapich2-2.3.3 /var/tmp/mvapich2-2.3.3.tar.gz
ENV LD_LIBRARY_PATH=/usr/local/mvapich2/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/mvapich2/bin:$PATH \
    PROFILE_POSTLIB="-L/usr/local/cuda/lib64/stubs -lnvidia-ml -lcuda"''')

    @ubuntu
    @docker
    def test_gpu_arch(self):
        """mvapich2 GPU architecture"""
        mv2 = mvapich2(version='2.3b', gpu_arch='sm_60')
        self.assertEqual(str(mv2),
r'''# MVAPICH2 version 2.3b
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        byacc \
        file \
        make \
        openssh-client \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp http://mvapich.cse.ohio-state.edu/download/mvapich/mv2/mvapich2-2.3b.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/mvapich2-2.3b.tar.gz -C /var/tmp -z && \
    cd /var/tmp/mvapich2-2.3b && \
    ln -s /usr/local/cuda/lib64/stubs/libnvidia-ml.so /usr/local/cuda/lib64/stubs/libnvidia-ml.so.1 && \
    ln -s /usr/local/cuda/lib64/stubs/libcuda.so /usr/local/cuda/lib64/stubs/libcuda.so.1 && \
    sed -i -e 's/-arch sm_20/-arch sm_60/g' Makefile.in && \
    cd /var/tmp/mvapich2-2.3b &&  LD_LIBRARY_PATH='/usr/local/cuda/lib64/stubs:$LD_LIBRARY_PATH' ./configure --prefix=/usr/local/mvapich2 --disable-mcast --enable-cuda --with-cuda=/usr/local/cuda && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/mvapich2-2.3b /var/tmp/mvapich2-2.3b.tar.gz
ENV LD_LIBRARY_PATH=/usr/local/mvapich2/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/mvapich2/bin:$PATH \
    PROFILE_POSTLIB="-L/usr/local/cuda/lib64/stubs -lnvidia-ml -lcuda"''')

    @ubuntu
    @docker
    def test_nocuda(self):
        """Disable CUDA"""
        mv2 = mvapich2(cuda=False)
        self.assertEqual(str(mv2),
r'''# MVAPICH2 version 2.3.3
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        byacc \
        file \
        make \
        openssh-client \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp http://mvapich.cse.ohio-state.edu/download/mvapich/mv2/mvapich2-2.3.3.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/mvapich2-2.3.3.tar.gz -C /var/tmp -z && \
    cd /var/tmp/mvapich2-2.3.3 &&   ./configure --prefix=/usr/local/mvapich2 --disable-cuda --disable-mcast && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/mvapich2-2.3.3 /var/tmp/mvapich2-2.3.3.tar.gz
ENV LD_LIBRARY_PATH=/usr/local/mvapich2/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/mvapich2/bin:$PATH''')

    @centos
    @docker
    def test_defaults_centos(self):
        """Default mvapich2 building block"""
        mv2 = mvapich2()
        self.assertEqual(str(mv2),
r'''# MVAPICH2 version 2.3.3
RUN yum install -y \
        byacc \
        file \
        make \
        openssh-clients \
        wget && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp http://mvapich.cse.ohio-state.edu/download/mvapich/mv2/mvapich2-2.3.3.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/mvapich2-2.3.3.tar.gz -C /var/tmp -z && \
    cd /var/tmp/mvapich2-2.3.3 && \
    ln -s /usr/local/cuda/lib64/stubs/libnvidia-ml.so /usr/local/cuda/lib64/stubs/libnvidia-ml.so.1 && \
    ln -s /usr/local/cuda/lib64/stubs/libcuda.so /usr/local/cuda/lib64/stubs/libcuda.so.1 && \
    cd /var/tmp/mvapich2-2.3.3 &&  LD_LIBRARY_PATH='/usr/local/cuda/lib64/stubs:$LD_LIBRARY_PATH' ./configure --prefix=/usr/local/mvapich2 --disable-mcast --enable-cuda --with-cuda=/usr/local/cuda && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/mvapich2-2.3.3 /var/tmp/mvapich2-2.3.3.tar.gz
ENV LD_LIBRARY_PATH=/usr/local/mvapich2/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/mvapich2/bin:$PATH \
    PROFILE_POSTLIB="-L/usr/local/cuda/lib64/stubs -lnvidia-ml -lcuda"''')

    @ubuntu
    @docker
    def test_ldconfig(self):
        """ldconfig option"""
        mv2 = mvapich2(ldconfig=True, version='2.3')
        self.assertEqual(str(mv2),
r'''# MVAPICH2 version 2.3
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        byacc \
        file \
        make \
        openssh-client \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp http://mvapich.cse.ohio-state.edu/download/mvapich/mv2/mvapich2-2.3.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/mvapich2-2.3.tar.gz -C /var/tmp -z && \
    cd /var/tmp/mvapich2-2.3 && \
    ln -s /usr/local/cuda/lib64/stubs/libnvidia-ml.so /usr/local/cuda/lib64/stubs/libnvidia-ml.so.1 && \
    ln -s /usr/local/cuda/lib64/stubs/libcuda.so /usr/local/cuda/lib64/stubs/libcuda.so.1 && \
    cd /var/tmp/mvapich2-2.3 &&  LD_LIBRARY_PATH='/usr/local/cuda/lib64/stubs:$LD_LIBRARY_PATH' ./configure --prefix=/usr/local/mvapich2 --disable-mcast --enable-cuda --with-cuda=/usr/local/cuda && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    echo "/usr/local/mvapich2/lib" >> /etc/ld.so.conf.d/hpccm.conf && ldconfig && \
    rm -rf /var/tmp/mvapich2-2.3 /var/tmp/mvapich2-2.3.tar.gz
ENV PATH=/usr/local/mvapich2/bin:$PATH \
    PROFILE_POSTLIB="-L/usr/local/cuda/lib64/stubs -lnvidia-ml -lcuda"''')

    @ubuntu
    @docker
    def test_runtime(self):
        """Runtime"""
        mv2 = mvapich2()
        r = mv2.runtime()
        self.assertEqual(r,
r'''# MVAPICH2
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        openssh-client && \
    rm -rf /var/lib/apt/lists/*
COPY --from=0 /usr/local/mvapich2 /usr/local/mvapich2
ENV LD_LIBRARY_PATH=/usr/local/mvapich2/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/mvapich2/bin:$PATH''')

    def test_toolchain(self):
        """Toolchain"""
        mv2 = mvapich2()
        tc = mv2.toolchain
        self.assertEqual(tc.CC, 'mpicc')
        self.assertEqual(tc.CXX, 'mpicxx')
        self.assertEqual(tc.FC, 'mpifort')
        self.assertEqual(tc.F77, 'mpif77')
        self.assertEqual(tc.F90, 'mpif90')
