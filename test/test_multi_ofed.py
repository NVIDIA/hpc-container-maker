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

"""Test cases for the multi_ofed module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import centos, centos8, docker, ubuntu, ubuntu18, x86_64

from hpccm.building_blocks.multi_ofed import multi_ofed

class Test_multi_ofed(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @x86_64
    @ubuntu18
    @docker
    def test_versions_ubuntu18(self):
        """mlnx_version parameter"""
        # Reduced set of versions to limit gold output
        ofed = multi_ofed(mlnx_versions=['4.5-1.0.1.0', '4.6-1.0.1.1'])
        self.assertEqual(str(ofed),
r'''# Mellanox OFED version 4.5-1.0.1.0
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
    mkdir -p /etc/apt/sources.list.d && wget -q -nc --no-check-certificate -P /etc/apt/sources.list.d https://linux.mellanox.com/public/repo/mlnx_ofed/4.5-1.0.1.0/ubuntu18.04/mellanox_mlnx_ofed.list && \
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
    mkdir -p /usr/local/ofed/4.5-1.0.1.0 && \
    find /var/tmp/packages_download -regextype posix-extended -type f -regex "/var/tmp/packages_download/(ibverbs-utils|libibmad|libibmad-devel|libibumad|libibumad-devel|libibverbs-dev|libibverbs1|libmlx4-1|libmlx4-dev|libmlx5-1|libmlx5-dev|librdmacm-dev|librdmacm1).*deb" -exec dpkg --extract {} /usr/local/ofed/4.5-1.0.1.0 \; && \
    rm -rf /var/tmp/packages_download && \
    rm -f /etc/apt/sources.list.d/mellanox_mlnx_ofed.list && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /etc/libibverbs.d
# Mellanox OFED version 4.6-1.0.1.1
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
    mkdir -p /etc/apt/sources.list.d && wget -q -nc --no-check-certificate -P /etc/apt/sources.list.d https://linux.mellanox.com/public/repo/mlnx_ofed/4.6-1.0.1.1/ubuntu18.04/mellanox_mlnx_ofed.list && \
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
    mkdir -p /usr/local/ofed/4.6-1.0.1.1 && \
    find /var/tmp/packages_download -regextype posix-extended -type f -regex "/var/tmp/packages_download/(ibverbs-utils|libibmad|libibmad-devel|libibumad|libibumad-devel|libibverbs-dev|libibverbs1|libmlx4-1|libmlx4-dev|libmlx5-1|libmlx5-dev|librdmacm-dev|librdmacm1).*deb" -exec dpkg --extract {} /usr/local/ofed/4.6-1.0.1.1 \; && \
    rm -rf /var/tmp/packages_download && \
    rm -f /etc/apt/sources.list.d/mellanox_mlnx_ofed.list && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /etc/libibverbs.d
# OFED
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libnl-3-200 \
        libnl-route-3-200 \
        libnuma1 && \
    rm -rf /var/lib/apt/lists/*
RUN apt-get update -y && \
    mkdir -m 777 -p /var/tmp/packages_download && cd /var/tmp/packages_download && \
    DEBIAN_FRONTEND=noninteractive apt-get download -y --no-install-recommends -t bionic \
        dapl2-utils \
        ibutils \
        ibverbs-providers \
        ibverbs-utils \
        infiniband-diags \
        libdapl-dev \
        libdapl2 \
        libibmad-dev \
        libibmad5 \
        libibverbs-dev \
        libibverbs1 \
        librdmacm-dev \
        librdmacm1 \
        rdmacm-utils && \
    mkdir -p /usr/local/ofed/inbox && \
    find /var/tmp/packages_download -regextype posix-extended -type f -regex "/var/tmp/packages_download/(dapl2-utils|ibutils|ibverbs-providers|ibverbs-utils|infiniband-diags|libdapl-dev|libdapl2|libibmad-dev|libibmad5|libibverbs-dev|libibverbs1|librdmacm-dev|librdmacm1|rdmacm-utils).*deb" -exec dpkg --extract {} /usr/local/ofed/inbox \; && \
    rm -rf /var/tmp/packages_download && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /etc/libibverbs.d
RUN ln -s /usr/local/ofed/inbox /usr/local/ofed/5.0-0''')

    @x86_64
    @centos8
    @docker
    def test_versions_centos8(self):
        """mlnx_version parameter"""
        # Reduced set of versions to limit gold output
        ofed = multi_ofed(mlnx_versions=['4.5-1.0.1.0', '4.6-1.0.1.1'])
        self.assertEqual(str(ofed),
r'''# Mellanox OFED version 4.5-1.0.1.0
RUN yum install -y \
        ca-certificates \
        gnupg \
        libnl3 \
        numactl-libs \
        wget && \
    rm -rf /var/cache/yum/*
RUN rpm --import https://www.mellanox.com/downloads/ofed/RPM-GPG-KEY-Mellanox && \
    yum install -y dnf-utils && \
    yum-config-manager --add-repo https://linux.mellanox.com/public/repo/mlnx_ofed/4.5-1.0.1.0/rhel8.0/mellanox_mlnx_ofed.repo && \
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
    mkdir -p /usr/local/ofed/4.5-1.0.1.0 && cd /usr/local/ofed/4.5-1.0.1.0 && \
    find /var/tmp/packages_download -regextype posix-extended -type f -regex "/var/tmp/packages_download/(libibmad|libibmad-devel|libibumad|libibumad-devel|libibverbs|libibverbs-devel|libibverbs-utils|libmlx4|libmlx4-devel|libmlx5|libmlx5-devel|librdmacm|librdmacm-devel).*rpm" -exec sh -c "rpm2cpio {} | cpio -idm" \; && \
    rm -rf /var/tmp/packages_download && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /etc/libibverbs.d
# Mellanox OFED version 4.6-1.0.1.1
RUN yum install -y \
        ca-certificates \
        gnupg \
        libnl3 \
        numactl-libs \
        wget && \
    rm -rf /var/cache/yum/*
RUN rpm --import https://www.mellanox.com/downloads/ofed/RPM-GPG-KEY-Mellanox && \
    yum install -y dnf-utils && \
    yum-config-manager --add-repo https://linux.mellanox.com/public/repo/mlnx_ofed/4.6-1.0.1.1/rhel8.0/mellanox_mlnx_ofed.repo && \
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
    mkdir -p /usr/local/ofed/4.6-1.0.1.1 && cd /usr/local/ofed/4.6-1.0.1.1 && \
    find /var/tmp/packages_download -regextype posix-extended -type f -regex "/var/tmp/packages_download/(libibmad|libibmad-devel|libibumad|libibumad-devel|libibverbs|libibverbs-devel|libibverbs-utils|libmlx4|libmlx4-devel|libmlx5|libmlx5-devel|librdmacm|librdmacm-devel).*rpm" -exec sh -c "rpm2cpio {} | cpio -idm" \; && \
    rm -rf /var/tmp/packages_download && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /etc/libibverbs.d
# OFED
RUN yum install -y \
        libnl3 \
        numactl-libs && \
    rm -rf /var/cache/yum/*
RUN yum install -y dnf-utils && \
    yum-config-manager --set-enabled PowerTools && \
    yum install -y yum-utils && \
    mkdir -p /var/tmp/packages_download && \
    yumdownloader --destdir=/var/tmp/packages_download -x \*i?86 --archlist=x86_64 --disablerepo=mlnx\* \
        libibmad \
        libibmad-devel \
        libibumad \
        libibverbs \
        libibverbs-utils \
        libmlx5 \
        librdmacm \
        rdma-core \
        rdma-core-devel && \
    mkdir -p /usr/local/ofed/inbox && cd /usr/local/ofed/inbox && \
    find /var/tmp/packages_download -regextype posix-extended -type f -regex "/var/tmp/packages_download/(libibmad|libibmad-devel|libibumad|libibverbs|libibverbs-utils|libmlx5|librdmacm|rdma-core|rdma-core-devel).*rpm" -exec sh -c "rpm2cpio {} | cpio -idm" \; && \
    rm -rf /var/tmp/packages_download && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /etc/libibverbs.d
RUN ln -s /usr/local/ofed/inbox /usr/local/ofed/5.0-0''')

    @x86_64
    @centos
    @docker
    def test_runtime_centos(self):
        """Runtime"""
        ofed = multi_ofed()
        r = ofed.runtime()
        self.assertEqual(r,
r'''# OFED
RUN yum install -y \
        libnl \
        libnl3 \
        numactl-libs && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /etc/libibverbs.d
COPY --from=0 /usr/local/ofed /usr/local/ofed''')

    @x86_64
    @ubuntu18
    @docker
    def test_runtime_ubuntu18(self):
        """Runtime"""
        ofed = multi_ofed()
        r = ofed.runtime()
        self.assertEqual(r,
r'''# OFED
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libnl-3-200 \
        libnl-route-3-200 \
        libnuma1 && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /etc/libibverbs.d
COPY --from=0 /usr/local/ofed /usr/local/ofed''')
