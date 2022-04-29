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

"""Test cases for the nccl module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import centos, centos8, docker, ppc64le, ubuntu, ubuntu18, x86_64

from hpccm.building_blocks.nccl import nccl

class Test_nccl(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @x86_64
    @ubuntu
    @docker
    def test_defaults_ubuntu(self):
        """nccl defaults"""
        n = nccl()
        self.assertEqual(str(n),
r'''# NCCL 2.12.10-1
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        apt-transport-https \
        ca-certificates \
        gnupg \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN wget -qO - https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64/3bf863cc.pub | apt-key add - && \
    echo "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64 /" >> /etc/apt/sources.list.d/hpccm.list && \
    apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libnccl-dev=2.12.10-1+cuda11.6 \
        libnccl2=2.12.10-1+cuda11.6 && \
    rm -rf /var/lib/apt/lists/*''')

    @x86_64
    @ubuntu18
    @docker
    def test_defaults_ubuntu18(self):
        """nccl defaults"""
        n = nccl()
        self.assertEqual(str(n),
r'''# NCCL 2.12.10-1
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        apt-transport-https \
        ca-certificates \
        gnupg \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN wget -qO - https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/3bf863cc.pub | apt-key add - && \
    echo "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64 /" >> /etc/apt/sources.list.d/hpccm.list && \
    apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libnccl-dev=2.12.10-1+cuda11.6 \
        libnccl2=2.12.10-1+cuda11.6 && \
    rm -rf /var/lib/apt/lists/*''')

    @ppc64le
    @ubuntu
    @docker
    def test_ubuntu_ppc64le(self):
        """nccl ppc64le"""
        n = nccl(cuda=9.2, version='2.4.8-1')
        self.assertEqual(str(n),
r'''# NCCL 2.4.8-1
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        apt-transport-https \
        ca-certificates \
        gnupg \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN wget -qO - https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/ppc64el/3bf863cc.pub | apt-key add - && \
    echo "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/ppc64el /" >> /etc/apt/sources.list.d/hpccm.list && \
    apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libnccl-dev=2.4.8-1+cuda9.2 \
        libnccl2=2.4.8-1+cuda9.2 && \
    rm -rf /var/lib/apt/lists/*''')

    @x86_64
    @ubuntu
    @docker
    def test_build_ubuntu(self):
        """nccl build"""
        n = nccl(build=True)
        self.assertEqual(str(n),
r'''# NCCL
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        make \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/NVIDIA/nccl/archive/v2.12.10-1.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/v2.12.10-1.tar.gz -C /var/tmp -z && \
    cd /var/tmp/nccl-2.12.10-1 && \
    PREFIX=/usr/local/nccl make -j$(nproc) install && \
    rm -rf /var/tmp/nccl-2.12.10-1 /var/tmp/v2.12.10-1.tar.gz
ENV CPATH=/usr/local/nccl/include:$CPATH \
    LD_LIBRARY_PATH=/usr/local/nccl/lib:$LD_LIBRARY_PATH \
    LIBRARY_PATH=/usr/local/nccl/lib:$LIBRARY_PATH \
    PATH=/usr/local/nccl/bin:$PATH''')

    @x86_64
    @centos
    @docker
    def test_defaults_centos(self):
        """nccl defaults"""
        n = nccl()
        self.assertEqual(str(n),
r'''# NCCL 2.12.10-1
RUN rpm --import https://developer.download.nvidia.com/compute/cuda/repos/rhel7/x86_64/3bf863cc.pub && \
    yum install -y yum-utils && \
    yum-config-manager --add-repo https://developer.download.nvidia.com/compute/cuda/repos/rhel7/x86_64 && \
    yum install -y \
        libnccl-2.12.10-1+cuda11.6 \
        libnccl-devel-2.12.10-1+cuda11.6 && \
    rm -rf /var/cache/yum/*''')

    @x86_64
    @centos8
    @docker
    def test_defaults_centos8(self):
        """nccl defaults"""
        n = nccl()
        self.assertEqual(str(n),
r'''# NCCL 2.12.10-1
RUN rpm --import https://developer.download.nvidia.com/compute/cuda/repos/rhel8/x86_64/3bf863cc.pub && \
    yum install -y dnf-utils && \
    yum-config-manager --add-repo https://developer.download.nvidia.com/compute/cuda/repos/rhel8/x86_64 && \
    yum install -y \
        libnccl-2.12.10-1+cuda11.6 \
        libnccl-devel-2.12.10-1+cuda11.6 && \
    rm -rf /var/cache/yum/*''')

    @x86_64
    @ubuntu
    @docker
    def test_build_repo_ubuntu(self):
        """nccl build from git"""
        n = nccl(build=True, make_variables={'CUDA_HOME': '/usr/local/cuda'},
                 repository=True)
        self.assertEqual(str(n),
r'''# NCCL
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        git \
        make \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && cd /var/tmp && git clone --depth=1 https://github.com/NVIDIA/nccl.git nccl && cd - && \
    cd /var/tmp/nccl && \
    CUDA_HOME=/usr/local/cuda PREFIX=/usr/local/nccl make -j$(nproc) install && \
    rm -rf /var/tmp/nccl
ENV CPATH=/usr/local/nccl/include:$CPATH \
    LD_LIBRARY_PATH=/usr/local/nccl/lib:$LD_LIBRARY_PATH \
    LIBRARY_PATH=/usr/local/nccl/lib:$LIBRARY_PATH \
    PATH=/usr/local/nccl/bin:$PATH''')

    @centos
    @docker
    def test_build_centos(self):
        """nccl build"""
        n = nccl(build=True, version='2.7.6-1')
        self.assertEqual(str(n),
r'''# NCCL
RUN yum install -y \
        make \
        wget \
        which && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/NVIDIA/nccl/archive/v2.7.6-1.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/v2.7.6-1.tar.gz -C /var/tmp -z && \
    cd /var/tmp/nccl-2.7.6-1 && \
    PREFIX=/usr/local/nccl make -j$(nproc) install && \
    rm -rf /var/tmp/nccl-2.7.6-1 /var/tmp/v2.7.6-1.tar.gz
ENV CPATH=/usr/local/nccl/include:$CPATH \
    LD_LIBRARY_PATH=/usr/local/nccl/lib:$LD_LIBRARY_PATH \
    LIBRARY_PATH=/usr/local/nccl/lib:$LIBRARY_PATH \
    PATH=/usr/local/nccl/bin:$PATH''')

    @x86_64
    @ubuntu
    @docker
    def test_runtime(self):
        """Runtime"""
        n = nccl()
        r = n.runtime()
        self.assertEqual(r,
r'''# NCCL
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        apt-transport-https \
        ca-certificates \
        gnupg \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN wget -qO - https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64/3bf863cc.pub | apt-key add - && \
    echo "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64 /" >> /etc/apt/sources.list.d/hpccm.list && \
    apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libnccl2=2.12.10-1+cuda11.6 && \
    rm -rf /var/lib/apt/lists/*''')

    @x86_64
    @ubuntu
    @docker
    def test_build_runtime(self):
        """Runtime"""
        n = nccl(build=True)
        r = n.runtime()
        self.assertEqual(r,
r'''# NCCL
COPY --from=0 /usr/local/nccl /usr/local/nccl
ENV CPATH=/usr/local/nccl/include:$CPATH \
    LD_LIBRARY_PATH=/usr/local/nccl/lib:$LD_LIBRARY_PATH \
    LIBRARY_PATH=/usr/local/nccl/lib:$LIBRARY_PATH \
    PATH=/usr/local/nccl/bin:$PATH''')
