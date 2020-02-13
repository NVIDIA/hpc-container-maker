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

"""Test cases for the gnu module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import centos, centos8, docker, ubuntu

from hpccm.building_blocks.gnu import gnu

class Test_gnu(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @ubuntu
    @docker
    def test_defaults_ubuntu(self):
        """Default gnu building block"""
        g = gnu()
        self.assertEqual(str(g),
r'''# GNU compiler
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        g++ \
        gcc \
        gfortran && \
    rm -rf /var/lib/apt/lists/*''')

    @centos
    @docker
    def test_defaults_centos(self):
        """Default gnu building block"""
        g = gnu()
        self.assertEqual(str(g),
r'''# GNU compiler
RUN yum install -y \
        gcc \
        gcc-c++ \
        gcc-gfortran && \
    rm -rf /var/cache/yum/*''')

    @ubuntu
    @docker
    def test_version_ubuntu(self):
        """GNU compiler version"""
        g = gnu(extra_repository=True, version='7')
        self.assertEqual(str(g),
r'''# GNU compiler
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends software-properties-common && \
    apt-add-repository ppa:ubuntu-toolchain-r/test -y && \
    apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        g++-7 \
        gcc-7 \
        gfortran-7 && \
    rm -rf /var/lib/apt/lists/*
RUN update-alternatives --install /usr/bin/g++ g++ $(which g++-7) 30 && \
    update-alternatives --install /usr/bin/gcc gcc $(which gcc-7) 30 && \
    update-alternatives --install /usr/bin/gcov gcov $(which gcov-7) 30 && \
    update-alternatives --install /usr/bin/gfortran gfortran $(which gfortran-7) 30''')

    @centos
    @docker
    def test_version_centos7(self):
        """GNU compiler version"""
        g = gnu(extra_repository=True, version='7')
        self.assertEqual(str(g),
r'''# GNU compiler
RUN yum install -y centos-release-scl && \
    yum install -y \
        devtoolset-7-gcc \
        devtoolset-7-gcc-c++ \
        devtoolset-7-gcc-gfortran && \
    rm -rf /var/cache/yum/*
RUN update-alternatives --install /usr/bin/g++ g++ /opt/rh/devtoolset-7/root/usr/bin/g++ 30 && \
    update-alternatives --install /usr/bin/gcc gcc /opt/rh/devtoolset-7/root/usr/bin/gcc 30 && \
    update-alternatives --install /usr/bin/gcov gcov /opt/rh/devtoolset-7/root/usr/bin/gcov 30 && \
    update-alternatives --install /usr/bin/gfortran gfortran /opt/rh/devtoolset-7/root/usr/bin/gfortran 30''')

    @centos8
    @docker
    def test_version_centos8(self):
        """GNU compiler version"""
        g = gnu(version='9')
        self.assertEqual(str(g),
r'''# GNU compiler
RUN yum install -y centos-release-stream && \
    yum install -y \
        gcc-toolset-9-gcc \
        gcc-toolset-9-gcc-c++ \
        gcc-toolset-9-gcc-gfortran && \
    rm -rf /var/cache/yum/*
RUN update-alternatives --install /usr/bin/g++ g++ /opt/rh/gcc-toolset-9/root/usr/bin/g++ 30 && \
    update-alternatives --install /usr/bin/gcc gcc /opt/rh/gcc-toolset-9/root/usr/bin/gcc 30 && \
    update-alternatives --install /usr/bin/gcov gcov /opt/rh/gcc-toolset-9/root/usr/bin/gcov 30 && \
    update-alternatives --install /usr/bin/gfortran gfortran /opt/rh/gcc-toolset-9/root/usr/bin/gfortran 30''')

    @ubuntu
    @docker
    def test_source_no_version(self):
        """GNU compiler from source with no version"""
        with self.assertRaises(RuntimeError):
            g = gnu(source=True)

    @ubuntu
    @docker
    def test_source_ubuntu(self):
        """GNU compiler from source"""
        g = gnu(source=True, version='9.1.0')
        self.assertEqual(str(g),
r'''# GNU compiler
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        bzip2 \
        file \
        g++ \
        gcc \
        git \
        make \
        perl \
        tar \
        wget \
        xz-utils && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp http://ftpmirror.gnu.org/gcc/gcc-9.1.0/gcc-9.1.0.tar.xz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/gcc-9.1.0.tar.xz -C /var/tmp -J && \
    cd /var/tmp/gcc-9.1.0 && ./contrib/download_prerequisites && \
    mkdir -p /var/tmp/objdir && cd /var/tmp/objdir &&   /var/tmp/gcc-9.1.0/configure --prefix=/usr/local/gnu --disable-multilib --enable-languages=c,c++,fortran && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/gcc-9.1.0.tar.xz /var/tmp/gcc-9.1.0 /var/tmp/objdir
ENV LD_LIBRARY_PATH=/usr/local/gnu/lib64:$LD_LIBRARY_PATH \
    PATH=/usr/local/gnu/bin:$PATH''')

    @centos
    @docker
    def test_source_ldconfig_centos(self):
        """GNU compiler from source"""
        g = gnu(ldconfig=True, source=True, version='9.1.0')
        self.assertEqual(str(g),
r'''# GNU compiler
RUN yum install -y \
        bzip2 \
        file \
        gcc \
        gcc-c++ \
        git \
        make \
        perl \
        tar \
        wget \
        xz && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp http://ftpmirror.gnu.org/gcc/gcc-9.1.0/gcc-9.1.0.tar.xz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/gcc-9.1.0.tar.xz -C /var/tmp -J && \
    cd /var/tmp/gcc-9.1.0 && ./contrib/download_prerequisites && \
    mkdir -p /var/tmp/objdir && cd /var/tmp/objdir &&   /var/tmp/gcc-9.1.0/configure --prefix=/usr/local/gnu --disable-multilib --enable-languages=c,c++,fortran && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    echo "/usr/local/gnu/lib64" >> /etc/ld.so.conf.d/hpccm.conf && ldconfig && \
    rm -rf /var/tmp/gcc-9.1.0.tar.xz /var/tmp/gcc-9.1.0 /var/tmp/objdir
ENV PATH=/usr/local/gnu/bin:$PATH''')

    @centos
    @docker
    def test_source_openacc_centos(self):
        """GNU compiler from source"""
        g = gnu(openacc=True, source=True, version='9.1.0')
        self.assertEqual(str(g),
r'''# GNU compiler
RUN yum install -y \
        bzip2 \
        file \
        gcc \
        gcc-c++ \
        git \
        make \
        perl \
        tar \
        wget \
        xz && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp http://ftpmirror.gnu.org/gcc/gcc-9.1.0/gcc-9.1.0.tar.xz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/gcc-9.1.0.tar.xz -C /var/tmp -J && \
    cd /var/tmp/gcc-9.1.0 && ./contrib/download_prerequisites && \
    mkdir -p /var/tmp && cd /var/tmp && git clone --depth=1 --branch master https://github.com/MentorEmbedded/nvptx-tools.git nvptx-tools && cd - && \
    cd /var/tmp/nvptx-tools &&   ./configure --prefix=/usr/local/gnu && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/nvptx-tools && \
    cd /var/tmp && \
    mkdir -p /var/tmp && cd /var/tmp && git clone --depth=1 --branch master https://github.com/MentorEmbedded/nvptx-newlib nvptx-newlib && cd - && \
    ln -s /var/tmp/nvptx-newlib/newlib /var/tmp/gcc-9.1.0/newlib && \
    mkdir -p /var/tmp/accel_objdir && cd /var/tmp/accel_objdir &&   /var/tmp/gcc-9.1.0/configure --prefix=/usr/local/gnu --disable-multilib --disable-sjlj-exceptions --enable-as-accelerator-for=x86_64-pc-linux-gnu --enable-languages=c,c++,fortran,lto --enable-newlib-io-long-long --target=nvptx-none && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    mkdir -p /var/tmp/objdir && cd /var/tmp/objdir &&   /var/tmp/gcc-9.1.0/configure --prefix=/usr/local/gnu --disable-multilib --enable-languages=c,c++,fortran,lto --enable-offload-targets=nvptx-none=/usr/local/gnu/nvptx-none --with-cuda-driver=/usr/local/cuda && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/gcc-9.1.0.tar.xz /var/tmp/gcc-9.1.0 /var/tmp/objdir && \
    rm -rf /var/tmp/accel_objdir /var/tmp/nvptx-newlib
ENV LD_LIBRARY_PATH=/usr/local/gnu/lib64:$LD_LIBRARY_PATH \
    PATH=/usr/local/gnu/bin:$PATH''')

    @ubuntu
    @docker
    def test_runtime(self):
        """Runtime"""
        g = gnu()
        r = g.runtime()
        self.assertEqual(r,
r'''# GNU compiler runtime
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libgfortran3 \
        libgomp1 && \
    rm -rf /var/lib/apt/lists/*''')

    @centos
    @docker
    def test_runtime_source(self):
        """Runtime"""
        g = gnu(source=True, version='9.1.0')
        r = g.runtime()
        self.assertEqual(r,
r'''# GNU compiler runtime
COPY --from=0 /usr/local/gnu/lib64 /usr/local/gnu/lib64
ENV LD_LIBRARY_PATH=/usr/local/gnu/lib64:$LD_LIBRARY_PATH''')

    @centos
    @docker
    def test_runtime_source_ldconfig(self):
        """Runtime"""
        g = gnu(ldconfig=True, source=True, version='9.1.0')
        r = g.runtime()
        self.assertEqual(r,
r'''# GNU compiler runtime
COPY --from=0 /usr/local/gnu/lib64 /usr/local/gnu/lib64
RUN echo "/usr/local/gnu/lib64" >> /etc/ld.so.conf.d/hpccm.conf && ldconfig''')

    def test_toolchain(self):
        """Toolchain"""
        g = gnu()
        tc = g.toolchain
        self.assertEqual(tc.CC, 'gcc')
        self.assertEqual(tc.CXX, 'g++')
        self.assertEqual(tc.FC, 'gfortran')
        self.assertEqual(tc.F77, 'gfortran')
        self.assertEqual(tc.F90, 'gfortran')
