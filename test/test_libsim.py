# Copyright (c) 2019, NVIDIA CORPORATION.  All rights reserved.
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

"""Test cases for the libsim module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import centos, docker, ubuntu

from hpccm.building_blocks.libsim import libsim

class Test_libsim(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @ubuntu
    @docker
    def test_defaults_ubuntu(self):
        """Default libsim building block"""
        l = libsim()
        self.assertEqual(str(l),
r'''# VisIt libsim version 2.13.3
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        gzip \
        libgl1-mesa-dev \
        libglu1-mesa-dev \
        libxt-dev \
        make \
        patch \
        tar \
        wget \
        zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp/visit && wget -q -nc --no-check-certificate -P /var/tmp/visit http://portal.nersc.gov/project/visit/releases/2.13.3/build_visit2_13_3 && \
    mkdir -p /usr/local/visit/third-party && \
    cd /var/tmp/visit && PAR_COMPILER=mpicc bash build_visit2_13_3 --xdb --server-components-only --parallel --no-icet --makeflags -j$(nproc) --prefix /usr/local/visit --system-cmake --system-python --thirdparty-path /usr/local/visit/third-party && \
    rm -rf /var/tmp/visit
ENV LD_LIBRARY_PATH=/usr/local/visit/2.13.3/linux-x86_64/lib:/usr/local/visit/2.13.3/linux-x86_64/libsim/V2/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/visit/bin:$PATH''')

    @centos
    @docker
    def test_defaults_centos(self):
        """Default libsim building block"""
        l = libsim()
        self.assertEqual(str(l),
r'''# VisIt libsim version 2.13.3
RUN yum install -y \
        gzip \
        libXt-devel \
        libglvnd-devel \
        make \
        mesa-libGL-devel \
        mesa-libGLU-devel \
        patch \
        tar \
        wget \
        which \
        zlib-devel && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp/visit && wget -q -nc --no-check-certificate -P /var/tmp/visit http://portal.nersc.gov/project/visit/releases/2.13.3/build_visit2_13_3 && \
    mkdir -p /usr/local/visit/third-party && \
    cd /var/tmp/visit && PAR_COMPILER=mpicc bash build_visit2_13_3 --xdb --server-components-only --parallel --no-icet --makeflags -j$(nproc) --prefix /usr/local/visit --system-cmake --system-python --thirdparty-path /usr/local/visit/third-party && \
    rm -rf /var/tmp/visit
ENV LD_LIBRARY_PATH=/usr/local/visit/2.13.3/linux-x86_64/lib:/usr/local/visit/2.13.3/linux-x86_64/libsim/V2/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/visit/bin:$PATH''')

    @ubuntu
    @docker
    def test_ldconfig(self):
        """ldconfig option"""
        l = libsim(ldconfig=True, version='2.13.3')
        self.assertEqual(str(l),
r'''# VisIt libsim version 2.13.3
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        gzip \
        libgl1-mesa-dev \
        libglu1-mesa-dev \
        libxt-dev \
        make \
        patch \
        tar \
        wget \
        zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp/visit && wget -q -nc --no-check-certificate -P /var/tmp/visit http://portal.nersc.gov/project/visit/releases/2.13.3/build_visit2_13_3 && \
    mkdir -p /usr/local/visit/third-party && \
    cd /var/tmp/visit && PAR_COMPILER=mpicc bash build_visit2_13_3 --xdb --server-components-only --parallel --no-icet --makeflags -j$(nproc) --prefix /usr/local/visit --system-cmake --system-python --thirdparty-path /usr/local/visit/third-party && \
    echo "/usr/local/visit/2.13.3/linux-x86_64/lib" >> /etc/ld.so.conf.d/hpccm.conf && ldconfig && \
    echo "/usr/local/visit/2.13.3/linux-x86_64/libsim/V2/lib" >> /etc/ld.so.conf.d/hpccm.conf && ldconfig && \
    rm -rf /var/tmp/visit
ENV PATH=/usr/local/visit/bin:$PATH''')

    def test_non_default_opts(self):
        """non-default options"""
        l = libsim(mpi=False, system_cmake=False, system_python=False,
                   thirdparty=False, version='2.13.3')
        self.assertEqual(str(l),
r'''# VisIt libsim version 2.13.3
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        gzip \
        libgl1-mesa-dev \
        libglu1-mesa-dev \
        libxt-dev \
        make \
        patch \
        tar \
        wget \
        zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp/visit && wget -q -nc --no-check-certificate -P /var/tmp/visit http://portal.nersc.gov/project/visit/releases/2.13.3/build_visit2_13_3 && \
    cd /var/tmp/visit &&  bash build_visit2_13_3 --xdb --server-components-only --makeflags -j$(nproc) --prefix /usr/local/visit && \
    rm -rf /var/tmp/visit
ENV LD_LIBRARY_PATH=/usr/local/visit/2.13.3/linux-x86_64/lib:/usr/local/visit/2.13.3/linux-x86_64/libsim/V2/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/visit/bin:$PATH''')

    @ubuntu
    @docker
    def test_runtime(self):
        """Runtime"""
        l = libsim()
        r = l.runtime()
        self.assertEqual(r,
r'''# VisIt libsim
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libgl1-mesa-glx \
        libglu1-mesa \
        libxt6 \
        zlib1g && \
    rm -rf /var/lib/apt/lists/*
COPY --from=0 /usr/local/visit /usr/local/visit
ENV LD_LIBRARY_PATH=/usr/local/visit/2.13.3/linux-x86_64/lib:/usr/local/visit/2.13.3/linux-x86_64/libsim/V2/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/visit/bin:$PATH''')
