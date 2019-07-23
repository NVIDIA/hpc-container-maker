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

from helpers import centos, docker, ubuntu, ubuntu18

from hpccm.building_blocks.multi_ofed import multi_ofed

class Test_multi_ofed(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @ubuntu
    @docker
    def test_versions_ubuntu(self):
        """mlnx_version parameter"""
        # Reduced set of versions to limit gold output
        ofed = multi_ofed(mlnx_versions=['4.5-1.0.1.0', '4.6-1.0.1.1'])
        self.assertEqual(str(ofed),
r'''# Mellanox OFED version 4.5-1.0.1.0
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libnl-3-200 \
        libnl-route-3-200 \
        libnuma1 \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp http://content.mellanox.com/ofed/MLNX_OFED-4.5-1.0.1.0/MLNX_OFED_LINUX-4.5-1.0.1.0-ubuntu16.04-x86_64.tgz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/MLNX_OFED_LINUX-4.5-1.0.1.0-ubuntu16.04-x86_64.tgz -C /var/tmp -z && \
    mkdir -p /etc/libibverbs.d && \
    mkdir -p /usr/local/ofed/4.5-1.0.1.0 && cd /usr/local/ofed/4.5-1.0.1.0 && \
    dpkg --extract /var/tmp/MLNX_OFED_LINUX-4.5-1.0.1.0-ubuntu16.04-x86_64/DEBS/libibverbs1_*_amd64.deb /usr/local/ofed/4.5-1.0.1.0 && \
    dpkg --extract /var/tmp/MLNX_OFED_LINUX-4.5-1.0.1.0-ubuntu16.04-x86_64/DEBS/libibverbs-dev_*_amd64.deb /usr/local/ofed/4.5-1.0.1.0 && \
    dpkg --extract /var/tmp/MLNX_OFED_LINUX-4.5-1.0.1.0-ubuntu16.04-x86_64/DEBS/ibverbs-utils_*_amd64.deb /usr/local/ofed/4.5-1.0.1.0 && \
    dpkg --extract /var/tmp/MLNX_OFED_LINUX-4.5-1.0.1.0-ubuntu16.04-x86_64/DEBS/libibmad_*_amd64.deb /usr/local/ofed/4.5-1.0.1.0 && \
    dpkg --extract /var/tmp/MLNX_OFED_LINUX-4.5-1.0.1.0-ubuntu16.04-x86_64/DEBS/libibmad-devel_*_amd64.deb /usr/local/ofed/4.5-1.0.1.0 && \
    dpkg --extract /var/tmp/MLNX_OFED_LINUX-4.5-1.0.1.0-ubuntu16.04-x86_64/DEBS/libibumad_*_amd64.deb /usr/local/ofed/4.5-1.0.1.0 && \
    dpkg --extract /var/tmp/MLNX_OFED_LINUX-4.5-1.0.1.0-ubuntu16.04-x86_64/DEBS/libibumad-devel_*_amd64.deb /usr/local/ofed/4.5-1.0.1.0 && \
    dpkg --extract /var/tmp/MLNX_OFED_LINUX-4.5-1.0.1.0-ubuntu16.04-x86_64/DEBS/libmlx4-1_*_amd64.deb /usr/local/ofed/4.5-1.0.1.0 && \
    dpkg --extract /var/tmp/MLNX_OFED_LINUX-4.5-1.0.1.0-ubuntu16.04-x86_64/DEBS/libmlx4-dev_*_amd64.deb /usr/local/ofed/4.5-1.0.1.0 && \
    dpkg --extract /var/tmp/MLNX_OFED_LINUX-4.5-1.0.1.0-ubuntu16.04-x86_64/DEBS/libmlx5-1_*_amd64.deb /usr/local/ofed/4.5-1.0.1.0 && \
    dpkg --extract /var/tmp/MLNX_OFED_LINUX-4.5-1.0.1.0-ubuntu16.04-x86_64/DEBS/libmlx5-dev_*_amd64.deb /usr/local/ofed/4.5-1.0.1.0 && \
    dpkg --extract /var/tmp/MLNX_OFED_LINUX-4.5-1.0.1.0-ubuntu16.04-x86_64/DEBS/librdmacm-dev_*_amd64.deb /usr/local/ofed/4.5-1.0.1.0 && \
    dpkg --extract /var/tmp/MLNX_OFED_LINUX-4.5-1.0.1.0-ubuntu16.04-x86_64/DEBS/librdmacm1_*_amd64.deb /usr/local/ofed/4.5-1.0.1.0 && \
    rm -rf /var/tmp/MLNX_OFED_LINUX-4.5-1.0.1.0-ubuntu16.04-x86_64.tgz /var/tmp/MLNX_OFED_LINUX-4.5-1.0.1.0-ubuntu16.04-x86_64
# Mellanox OFED version 4.6-1.0.1.1
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libnl-3-200 \
        libnl-route-3-200 \
        libnuma1 \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp http://content.mellanox.com/ofed/MLNX_OFED-4.6-1.0.1.1/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64.tgz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64.tgz -C /var/tmp -z && \
    mkdir -p /etc/libibverbs.d && \
    mkdir -p /usr/local/ofed/4.6-1.0.1.1 && cd /usr/local/ofed/4.6-1.0.1.1 && \
    dpkg --extract /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64/DEBS/libibverbs1_*_amd64.deb /usr/local/ofed/4.6-1.0.1.1 && \
    dpkg --extract /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64/DEBS/libibverbs-dev_*_amd64.deb /usr/local/ofed/4.6-1.0.1.1 && \
    dpkg --extract /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64/DEBS/ibverbs-utils_*_amd64.deb /usr/local/ofed/4.6-1.0.1.1 && \
    dpkg --extract /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64/DEBS/libibmad_*_amd64.deb /usr/local/ofed/4.6-1.0.1.1 && \
    dpkg --extract /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64/DEBS/libibmad-devel_*_amd64.deb /usr/local/ofed/4.6-1.0.1.1 && \
    dpkg --extract /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64/DEBS/libibumad_*_amd64.deb /usr/local/ofed/4.6-1.0.1.1 && \
    dpkg --extract /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64/DEBS/libibumad-devel_*_amd64.deb /usr/local/ofed/4.6-1.0.1.1 && \
    dpkg --extract /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64/DEBS/libmlx4-1_*_amd64.deb /usr/local/ofed/4.6-1.0.1.1 && \
    dpkg --extract /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64/DEBS/libmlx4-dev_*_amd64.deb /usr/local/ofed/4.6-1.0.1.1 && \
    dpkg --extract /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64/DEBS/libmlx5-1_*_amd64.deb /usr/local/ofed/4.6-1.0.1.1 && \
    dpkg --extract /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64/DEBS/libmlx5-dev_*_amd64.deb /usr/local/ofed/4.6-1.0.1.1 && \
    dpkg --extract /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64/DEBS/librdmacm-dev_*_amd64.deb /usr/local/ofed/4.6-1.0.1.1 && \
    dpkg --extract /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64/DEBS/librdmacm1_*_amd64.deb /usr/local/ofed/4.6-1.0.1.1 && \
    rm -rf /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64.tgz /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64
# OFED
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libnl-3-200 \
        libnl-route-3-200 \
        libnuma1 && \
    rm -rf /var/lib/apt/lists/*
RUN apt-get update -y && \
    mkdir -m 777 -p /var/tmp/packages_download && cd /var/tmp/packages_download && \
    DEBIAN_FRONTEND=noninteractive apt-get download -y \
        dapl2-utils \
        ibutils \
        ibverbs-utils \
        infiniband-diags \
        libdapl-dev \
        libdapl2 \
        libibcm-dev \
        libibcm1 \
        libibmad-dev \
        libibmad5 \
        libibverbs-dev \
        libibverbs1 \
        libmlx4-1 \
        libmlx4-dev \
        libmlx5-1 \
        libmlx5-dev \
        librdmacm-dev \
        librdmacm1 \
        rdmacm-utils && \
    mkdir -p /usr/local/ofed/inbox && \
    find /var/tmp/packages_download -regextype posix-extended -type f -regex "/var/tmp/packages_download/(dapl2-utils|ibutils|ibverbs-utils|infiniband-diags|libdapl-dev|libdapl2|libibcm-dev|libibcm1|libibmad-dev|libibmad5|libibverbs-dev|libibverbs1|libmlx4-1|libmlx4-dev|libmlx5-1|libmlx5-dev|librdmacm-dev|librdmacm1|rdmacm-utils).*deb" -exec dpkg --extract {} /usr/local/ofed/inbox \; && \
    rm -rf /var/tmp/packages_download && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /etc/libibverbs.d
RUN ln -s /usr/local/ofed/inbox /usr/local/ofed/5.0-0''')

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

    @ubuntu
    @docker
    def test_runtime_ubuntu(self):
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
