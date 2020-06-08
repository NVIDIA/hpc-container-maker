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

"""Test cases for the mlnx_ofed module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import aarch64, centos, centos8, docker, ppc64le, ubuntu, ubuntu18, x86_64

from hpccm.building_blocks.mlnx_ofed import mlnx_ofed

class Test_mlnx_ofed(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @x86_64
    @ubuntu
    @docker
    def test_defaults_ubuntu(self):
        """Default mlnx_ofed building block"""
        mofed = mlnx_ofed()
        self.assertEqual(str(mofed),
r'''# Mellanox OFED version 5.0-2.1.8.0
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ca-certificates \
        gnupg \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN wget -qO - https://www.mellanox.com/downloads/ofed/RPM-GPG-KEY-Mellanox | apt-key add - && \
    mkdir -p /etc/apt/sources.list.d && wget -q -nc --no-check-certificate -P /etc/apt/sources.list.d https://linux.mellanox.com/public/repo/mlnx_ofed/5.0-2.1.8.0/ubuntu16.04/mellanox_mlnx_ofed.list && \
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
    @ubuntu18
    @docker
    def test_defaults_ubuntu18(self):
        """Default mlnx_ofed building block"""
        mofed = mlnx_ofed()
        self.assertEqual(str(mofed),
r'''# Mellanox OFED version 5.0-2.1.8.0
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ca-certificates \
        gnupg \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN wget -qO - https://www.mellanox.com/downloads/ofed/RPM-GPG-KEY-Mellanox | apt-key add - && \
    mkdir -p /etc/apt/sources.list.d && wget -q -nc --no-check-certificate -P /etc/apt/sources.list.d https://linux.mellanox.com/public/repo/mlnx_ofed/5.0-2.1.8.0/ubuntu18.04/mellanox_mlnx_ofed.list && \
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
    @centos
    @docker
    def test_defaults_centos(self):
        """Default mlnx_ofed building block"""
        mofed = mlnx_ofed()
        self.assertEqual(str(mofed),
r'''# Mellanox OFED version 5.0-2.1.8.0
RUN yum install -y \
        ca-certificates \
        gnupg \
        wget && \
    rm -rf /var/cache/yum/*
RUN rpm --import https://www.mellanox.com/downloads/ofed/RPM-GPG-KEY-Mellanox && \
    yum install -y yum-utils && \
    yum-config-manager --add-repo https://linux.mellanox.com/public/repo/mlnx_ofed/5.0-2.1.8.0/rhel7.2/mellanox_mlnx_ofed.repo && \
    yum install -y \
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
    def test_defaults_centos8(self):
        """Default mlnx_ofed building block"""
        mofed = mlnx_ofed()
        self.assertEqual(str(mofed),
r'''# Mellanox OFED version 5.0-2.1.8.0
RUN yum install -y \
        ca-certificates \
        gnupg \
        wget && \
    rm -rf /var/cache/yum/*
RUN rpm --import https://www.mellanox.com/downloads/ofed/RPM-GPG-KEY-Mellanox && \
    yum install -y dnf-utils && \
    yum-config-manager --add-repo https://linux.mellanox.com/public/repo/mlnx_ofed/5.0-2.1.8.0/rhel8.0/mellanox_mlnx_ofed.repo && \
    yum install -y \
        libibumad \
        libibverbs \
        libibverbs-utils \
        librdmacm \
        rdma-core \
        rdma-core-devel && \
    rm -rf /var/cache/yum/*''')

    @x86_64
    @ubuntu
    @docker
    def test_prefix_ubuntu(self):
        """Prefix option"""
        mofed = mlnx_ofed(prefix='/opt/ofed', version='4.6-1.0.1.1')
        self.assertEqual(str(mofed),
r'''# Mellanox OFED version 4.6-1.0.1.1
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ca-certificates \
        gnupg \
        libnl-3-200 \
        libnl-route-3-200 \
        libnuma1 \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN wget -qO - https://www.mellanox.com/downloads/ofed/RPM-GPG-KEY-Mellanox | apt-key add - && \
    mkdir -p /etc/apt/sources.list.d && wget -q -nc --no-check-certificate -P /etc/apt/sources.list.d https://linux.mellanox.com/public/repo/mlnx_ofed/4.6-1.0.1.1/ubuntu16.04/mellanox_mlnx_ofed.list && \
    apt-get update -y && \
    mkdir -m 777 -p /var/tmp/packages_download && cd /var/tmp/packages_download && \
    DEBIAN_FRONTEND=noninteractive apt-get download -y --no-install-recommends \
        ibverbs-utils \
        libibmad \
        libibmad-devel \
        libibumad \
        libibumad-devel \
        libibverbs-dev \
        libibverbs1 \
        libmlx4-1 \
        libmlx4-dev \
        libmlx5-1 \
        libmlx5-dev \
        librdmacm-dev \
        librdmacm1 && \
    mkdir -p /opt/ofed && \
    find /var/tmp/packages_download -regextype posix-extended -type f -regex "/var/tmp/packages_download/(ibverbs-utils|libibmad|libibmad-devel|libibumad|libibumad-devel|libibverbs-dev|libibverbs1|libmlx4-1|libmlx4-dev|libmlx5-1|libmlx5-dev|librdmacm-dev|librdmacm1).*deb" -exec dpkg --extract {} /opt/ofed \; && \
    rm -rf /var/tmp/packages_download && \
    rm -f /etc/apt/sources.list.d/mellanox_mlnx_ofed.list && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /etc/libibverbs.d''')

    @x86_64
    @centos
    @docker
    def test_prefix_centos(self):
        """Prefix option"""
        mofed = mlnx_ofed(prefix='/opt/ofed', version='4.6-1.0.1.1')
        self.assertEqual(str(mofed),
r'''# Mellanox OFED version 4.6-1.0.1.1
RUN yum install -y \
        ca-certificates \
        gnupg \
        libnl \
        libnl3 \
        numactl-libs \
        wget && \
    rm -rf /var/cache/yum/*
RUN rpm --import https://www.mellanox.com/downloads/ofed/RPM-GPG-KEY-Mellanox && \
    yum install -y yum-utils && \
    yum-config-manager --add-repo https://linux.mellanox.com/public/repo/mlnx_ofed/4.6-1.0.1.1/rhel7.2/mellanox_mlnx_ofed.repo && \
    yum install -y yum-utils && \
    mkdir -p /var/tmp/packages_download && \
    yumdownloader --destdir=/var/tmp/packages_download -x \*i?86 --archlist=x86_64 \
        libibmad \
        libibmad-devel \
        libibumad \
        libibumad-devel \
        libibverbs \
        libibverbs-devel \
        libibverbs-utils \
        libmlx4 \
        libmlx4-devel \
        libmlx5 \
        libmlx5-devel \
        librdmacm \
        librdmacm-devel && \
    mkdir -p /opt/ofed && cd /opt/ofed && \
    find /var/tmp/packages_download -regextype posix-extended -type f -regex "/var/tmp/packages_download/(libibmad|libibmad-devel|libibumad|libibumad-devel|libibverbs|libibverbs-devel|libibverbs-utils|libmlx4|libmlx4-devel|libmlx5|libmlx5-devel|librdmacm|librdmacm-devel).*rpm" -exec sh -c "rpm2cpio {} | cpio -idm" \; && \
    rm -rf /var/tmp/packages_download && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /etc/libibverbs.d''')

    @aarch64
    @centos
    @docker
    def test_aarch64_centos(self):
        """aarch64"""
        mofed = mlnx_ofed(version='4.6-1.0.1.1')
        self.assertEqual(str(mofed),
r'''# Mellanox OFED version 4.6-1.0.1.1
RUN yum install -y \
        ca-certificates \
        gnupg \
        wget && \
    rm -rf /var/cache/yum/*
RUN rpm --import https://www.mellanox.com/downloads/ofed/RPM-GPG-KEY-Mellanox && \
    yum install -y yum-utils && \
    yum-config-manager --add-repo https://linux.mellanox.com/public/repo/mlnx_ofed/4.6-1.0.1.1/rhel7.6alternate/mellanox_mlnx_ofed.repo && \
    yum install -y \
        libibmad \
        libibmad-devel \
        libibumad \
        libibumad-devel \
        libibverbs \
        libibverbs-devel \
        libibverbs-utils \
        libmlx4 \
        libmlx4-devel \
        libmlx5 \
        libmlx5-devel \
        librdmacm \
        librdmacm-devel && \
    rm -rf /var/cache/yum/*''')

    @x86_64
    @ubuntu
    @docker
    def test_runtime(self):
        """Runtime"""
        mofed = mlnx_ofed()
        r = mofed.runtime()
        self.assertEqual(r,
r'''# Mellanox OFED version 5.0-2.1.8.0
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ca-certificates \
        gnupg \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN wget -qO - https://www.mellanox.com/downloads/ofed/RPM-GPG-KEY-Mellanox | apt-key add - && \
    mkdir -p /etc/apt/sources.list.d && wget -q -nc --no-check-certificate -P /etc/apt/sources.list.d https://linux.mellanox.com/public/repo/mlnx_ofed/5.0-2.1.8.0/ubuntu16.04/mellanox_mlnx_ofed.list && \
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
    @ubuntu
    @docker
    def test_prefix_runtime(self):
        """Prefix runtime"""
        mofed = mlnx_ofed(prefix='/opt/ofed')
        r = mofed.runtime()
        self.assertEqual(r,
r'''# Mellanox OFED version 5.0-2.1.8.0
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libnl-3-200 \
        libnl-route-3-200 \
        libnuma1 && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /etc/libibverbs.d
COPY --from=0 /opt/ofed /opt/ofed''')
