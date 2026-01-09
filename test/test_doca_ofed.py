# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
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

"""Test cases for the mlnx_ofed module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import aarch64, centos8, docker, rockylinux9, rockylinux10, ubuntu20, ubuntu22, ubuntu24, x86_64

from hpccm.building_blocks.doca_ofed import doca_ofed

class Test_doca_ofed(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @x86_64
    @ubuntu20
    @docker
    def test_defaults_ubuntu20(self):
        """Default doca_ofed building block"""
        doca = doca_ofed()
        self.assertMultiLineEqual(str(doca),
r'''# DOCA OFED version 3.2.0
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ca-certificates \
        gnupg \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /usr/share/keyrings && \
    rm -f /usr/share/keyrings/GPG-KEY-Mellanox.gpg && \
    wget -qO - https://linux.mellanox.com/public/repo/doca/GPG-KEY-Mellanox.pub | gpg --dearmor -o /usr/share/keyrings/GPG-KEY-Mellanox.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/GPG-KEY-Mellanox.gpg] https://linux.mellanox.com/public/repo/doca/3.2.0/ubuntu20.04/x86_64/ ./" >> /etc/apt/sources.list.d/hpccm.list && \
    apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ibverbs-providers \
        ibverbs-utils \
        libibmad-dev \
        libibmad5 \
        libibumad-dev \
        libibumad3 \
        libibverbs-dev \
        libibverbs1 \
        librdmacm-dev \
        librdmacm1 && \
    rm -rf /var/lib/apt/lists/*''')

    @aarch64
    @ubuntu22
    @docker
    def test_defaults_ubuntu22(self):
        """Default doca_ofed building block"""
        doca = doca_ofed()
        self.assertMultiLineEqual(str(doca),
r'''# DOCA OFED version 3.2.0
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ca-certificates \
        gnupg \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /usr/share/keyrings && \
    rm -f /usr/share/keyrings/GPG-KEY-Mellanox.gpg && \
    wget -qO - https://linux.mellanox.com/public/repo/doca/GPG-KEY-Mellanox.pub | gpg --dearmor -o /usr/share/keyrings/GPG-KEY-Mellanox.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/GPG-KEY-Mellanox.gpg] https://linux.mellanox.com/public/repo/doca/3.2.0/ubuntu22.04/arm64-sbsa/ ./" >> /etc/apt/sources.list.d/hpccm.list && \
    apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ibverbs-providers \
        ibverbs-utils \
        libibmad-dev \
        libibmad5 \
        libibumad-dev \
        libibumad3 \
        libibverbs-dev \
        libibverbs1 \
        librdmacm-dev \
        librdmacm1 && \
    rm -rf /var/lib/apt/lists/*''')

    @x86_64
    @ubuntu24
    @docker
    def test_defaults_ubuntu24(self):
        """Default doca_ofed building block"""
        doca = doca_ofed()
        self.assertMultiLineEqual(str(doca),
r'''# DOCA OFED version 3.2.0
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ca-certificates \
        gnupg \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /usr/share/keyrings && \
    rm -f /usr/share/keyrings/GPG-KEY-Mellanox.gpg && \
    wget -qO - https://linux.mellanox.com/public/repo/doca/GPG-KEY-Mellanox.pub | gpg --dearmor -o /usr/share/keyrings/GPG-KEY-Mellanox.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/GPG-KEY-Mellanox.gpg] https://linux.mellanox.com/public/repo/doca/3.2.0/ubuntu24.04/x86_64/ ./" >> /etc/apt/sources.list.d/hpccm.list && \
    apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ibverbs-providers \
        ibverbs-utils \
        libibmad-dev \
        libibmad5 \
        libibumad-dev \
        libibumad3 \
        libibverbs-dev \
        libibverbs1 \
        librdmacm-dev \
        librdmacm1 && \
    rm -rf /var/lib/apt/lists/*''')

    @x86_64
    @rockylinux9
    @docker
    def test_defaults_rockylinux9(self):
        """Default doca_ofed building block"""
        doca = doca_ofed()
        self.assertMultiLineEqual(str(doca),
r'''# DOCA OFED version 3.2.0
RUN yum install -y \
        ca-certificates \
        gnupg \
        wget && \
    rm -rf /var/cache/yum/*
RUN rpm --import https://linux.mellanox.com/public/repo/doca/GPG-KEY-Mellanox.pub && \
    yum install -y dnf-utils && \
    yum-config-manager --add-repo https://linux.mellanox.com/public/repo/doca/3.2.0/rhel9/x86_64 && \
    yum install -y \
        libibumad \
        libibverbs \
        libibverbs-utils \
        librdmacm \
        rdma-core \
        rdma-core-devel && \
    rm -rf /var/cache/yum/*''')

    @x86_64
    @rockylinux10
    @docker
    def test_defaults_rockylinux10(self):
        """Default doca_ofed building block"""
        doca = doca_ofed()
        self.assertMultiLineEqual(str(doca),
r'''# DOCA OFED version 3.2.0
RUN yum install -y \
        ca-certificates \
        gnupg \
        wget && \
    rm -rf /var/cache/yum/*
RUN yum install -y dnf-utils && \
    yum-config-manager --add-repo https://linux.mellanox.com/public/repo/doca/3.2.0/rhel10/x86_64 && \
    yum install -y --nogpgcheck \
        libibumad \
        libibverbs \
        libibverbs-utils \
        librdmacm \
        rdma-core \
        rdma-core-devel && \
    rm -rf /var/cache/yum/*''')

    @x86_64
    @centos8
    @docker
    def test_defaults_rockylinux8(self):
        """Default doca_ofed building block"""
        doca = doca_ofed()
        self.assertMultiLineEqual(str(doca),
r'''# DOCA OFED version 3.2.0
RUN yum install -y \
        ca-certificates \
        gnupg \
        wget && \
    rm -rf /var/cache/yum/*
RUN rpm --import https://linux.mellanox.com/public/repo/doca/GPG-KEY-Mellanox.pub && \
    yum install -y dnf-utils && \
    yum-config-manager --add-repo https://linux.mellanox.com/public/repo/doca/3.2.0/rhel8/x86_64 && \
    yum install -y \
        libibumad \
        libibverbs \
        libibverbs-utils \
        librdmacm \
        rdma-core \
        rdma-core-devel && \
    rm -rf /var/cache/yum/*''')

    @x86_64
    @ubuntu24
    @docker
    def test_runtime(self):
        """Runtime"""
        doca = doca_ofed(version='2.10.0')
        r = doca.runtime()
        self.assertMultiLineEqual(r,
r'''# DOCA OFED version 2.10.0
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ca-certificates \
        gnupg \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /usr/share/keyrings && \
    rm -f /usr/share/keyrings/GPG-KEY-Mellanox.gpg && \
    wget -qO - https://linux.mellanox.com/public/repo/doca/GPG-KEY-Mellanox.pub | gpg --dearmor -o /usr/share/keyrings/GPG-KEY-Mellanox.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/GPG-KEY-Mellanox.gpg] https://linux.mellanox.com/public/repo/doca/2.10.0/ubuntu24.04/x86_64/ ./" >> /etc/apt/sources.list.d/hpccm.list && \
    apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ibverbs-providers \
        ibverbs-utils \
        libibmad-dev \
        libibmad5 \
        libibumad-dev \
        libibumad3 \
        libibverbs-dev \
        libibverbs1 \
        librdmacm-dev \
        librdmacm1 && \
    rm -rf /var/lib/apt/lists/*''')
