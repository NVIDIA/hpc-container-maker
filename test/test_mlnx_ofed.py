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

from helpers import aarch64, centos, docker, ppc64le, ubuntu, ubuntu18, x86_64

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
r'''# Mellanox OFED version 4.6-1.0.1.1
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libnl-3-200 \
        libnl-route-3-200 \
        libnuma1 \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp http://content.mellanox.com/ofed/MLNX_OFED-4.6-1.0.1.1/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64.tgz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64.tgz -C /var/tmp -z && \
    dpkg --install /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64/DEBS/libibverbs1_*_amd64.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64/DEBS/libibverbs-dev_*_amd64.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64/DEBS/ibverbs-utils_*_amd64.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64/DEBS/libibmad_*_amd64.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64/DEBS/libibmad-devel_*_amd64.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64/DEBS/libibumad_*_amd64.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64/DEBS/libibumad-devel_*_amd64.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64/DEBS/libmlx4-1_*_amd64.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64/DEBS/libmlx4-dev_*_amd64.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64/DEBS/libmlx5-1_*_amd64.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64/DEBS/libmlx5-dev_*_amd64.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64/DEBS/librdmacm-dev_*_amd64.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64/DEBS/librdmacm1_*_amd64.deb && \
    rm -rf /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64.tgz /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64''')

    @x86_64
    @ubuntu18
    @docker
    def test_defaults_ubuntu(self):
        """Default mlnx_ofed building block"""
        mofed = mlnx_ofed()
        self.assertEqual(str(mofed),
r'''# Mellanox OFED version 4.6-1.0.1.1
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libnl-3-200 \
        libnl-route-3-200 \
        libnuma1 \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp http://content.mellanox.com/ofed/MLNX_OFED-4.6-1.0.1.1/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu18.04-x86_64.tgz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu18.04-x86_64.tgz -C /var/tmp -z && \
    dpkg --install /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu18.04-x86_64/DEBS/libibverbs1_*_amd64.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu18.04-x86_64/DEBS/libibverbs-dev_*_amd64.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu18.04-x86_64/DEBS/ibverbs-utils_*_amd64.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu18.04-x86_64/DEBS/libibmad_*_amd64.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu18.04-x86_64/DEBS/libibmad-devel_*_amd64.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu18.04-x86_64/DEBS/libibumad_*_amd64.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu18.04-x86_64/DEBS/libibumad-devel_*_amd64.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu18.04-x86_64/DEBS/libmlx4-1_*_amd64.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu18.04-x86_64/DEBS/libmlx4-dev_*_amd64.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu18.04-x86_64/DEBS/libmlx5-1_*_amd64.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu18.04-x86_64/DEBS/libmlx5-dev_*_amd64.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu18.04-x86_64/DEBS/librdmacm-dev_*_amd64.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu18.04-x86_64/DEBS/librdmacm1_*_amd64.deb && \
    rm -rf /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu18.04-x86_64.tgz /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu18.04-x86_64''')

    @x86_64
    @centos
    @docker
    def test_defaults_centos(self):
        """Default mlnx_ofed building block"""
        mofed = mlnx_ofed()
        self.assertEqual(str(mofed),
r'''# Mellanox OFED version 4.6-1.0.1.1
RUN yum install -y \
        libnl \
        libnl3 \
        numactl-libs \
        wget && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp http://content.mellanox.com/ofed/MLNX_OFED-4.6-1.0.1.1/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.2-x86_64.tgz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.2-x86_64.tgz -C /var/tmp -z && \
    rpm --install /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.2-x86_64/RPMS/libibverbs-*.x86_64.rpm /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.2-x86_64/RPMS/libibverbs-devel-*.x86_64.rpm /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.2-x86_64/RPMS/libibverbs-utils-*.x86_64.rpm /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.2-x86_64/RPMS/libibmad-*.x86_64.rpm /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.2-x86_64/RPMS/libibmad-devel-*.x86_64.rpm /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.2-x86_64/RPMS/libibumad-*.x86_64.rpm /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.2-x86_64/RPMS/libibumad-devel-*.x86_64.rpm /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.2-x86_64/RPMS/libmlx4-*.x86_64.rpm /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.2-x86_64/RPMS/libmlx4-devel-*.x86_64.rpm /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.2-x86_64/RPMS/libmlx5-*.x86_64.rpm /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.2-x86_64/RPMS/libmlx5-devel-*.x86_64.rpm /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.2-x86_64/RPMS/librdmacm-devel-*.x86_64.rpm /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.2-x86_64/RPMS/librdmacm-*.x86_64.rpm && \
    rm -rf /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.2-x86_64.tgz /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.2-x86_64''')

    @x86_64
    @ubuntu
    @docker
    def test_prefix_ubuntu(self):
        """Prefix option"""
        mofed = mlnx_ofed(prefix='/opt/ofed')
        self.assertEqual(str(mofed),
r'''# Mellanox OFED version 4.6-1.0.1.1
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
    mkdir -p /opt/ofed && cd /opt/ofed && \
    dpkg --extract /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64/DEBS/libibverbs1_*_amd64.deb /opt/ofed && \
    dpkg --extract /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64/DEBS/libibverbs-dev_*_amd64.deb /opt/ofed && \
    dpkg --extract /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64/DEBS/ibverbs-utils_*_amd64.deb /opt/ofed && \
    dpkg --extract /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64/DEBS/libibmad_*_amd64.deb /opt/ofed && \
    dpkg --extract /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64/DEBS/libibmad-devel_*_amd64.deb /opt/ofed && \
    dpkg --extract /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64/DEBS/libibumad_*_amd64.deb /opt/ofed && \
    dpkg --extract /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64/DEBS/libibumad-devel_*_amd64.deb /opt/ofed && \
    dpkg --extract /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64/DEBS/libmlx4-1_*_amd64.deb /opt/ofed && \
    dpkg --extract /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64/DEBS/libmlx4-dev_*_amd64.deb /opt/ofed && \
    dpkg --extract /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64/DEBS/libmlx5-1_*_amd64.deb /opt/ofed && \
    dpkg --extract /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64/DEBS/libmlx5-dev_*_amd64.deb /opt/ofed && \
    dpkg --extract /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64/DEBS/librdmacm-dev_*_amd64.deb /opt/ofed && \
    dpkg --extract /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64/DEBS/librdmacm1_*_amd64.deb /opt/ofed && \
    rm -rf /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64.tgz /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64''')

    @x86_64
    @centos
    @docker
    def test_prefix_centos(self):
        """Prefix option"""
        mofed = mlnx_ofed(prefix='/opt/ofed')
        self.assertEqual(str(mofed),
r'''# Mellanox OFED version 4.6-1.0.1.1
RUN yum install -y \
        libnl \
        libnl3 \
        numactl-libs \
        wget && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp http://content.mellanox.com/ofed/MLNX_OFED-4.6-1.0.1.1/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.2-x86_64.tgz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.2-x86_64.tgz -C /var/tmp -z && \
    mkdir -p /etc/libibverbs.d && \
    mkdir -p /opt/ofed && cd /opt/ofed && \
    rpm2cpio /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.2-x86_64/RPMS/libibverbs-*.x86_64.rpm | cpio -idm && \
    rpm2cpio /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.2-x86_64/RPMS/libibverbs-devel-*.x86_64.rpm | cpio -idm && \
    rpm2cpio /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.2-x86_64/RPMS/libibverbs-utils-*.x86_64.rpm | cpio -idm && \
    rpm2cpio /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.2-x86_64/RPMS/libibmad-*.x86_64.rpm | cpio -idm && \
    rpm2cpio /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.2-x86_64/RPMS/libibmad-devel-*.x86_64.rpm | cpio -idm && \
    rpm2cpio /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.2-x86_64/RPMS/libibumad-*.x86_64.rpm | cpio -idm && \
    rpm2cpio /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.2-x86_64/RPMS/libibumad-devel-*.x86_64.rpm | cpio -idm && \
    rpm2cpio /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.2-x86_64/RPMS/libmlx4-*.x86_64.rpm | cpio -idm && \
    rpm2cpio /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.2-x86_64/RPMS/libmlx4-devel-*.x86_64.rpm | cpio -idm && \
    rpm2cpio /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.2-x86_64/RPMS/libmlx5-*.x86_64.rpm | cpio -idm && \
    rpm2cpio /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.2-x86_64/RPMS/libmlx5-devel-*.x86_64.rpm | cpio -idm && \
    rpm2cpio /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.2-x86_64/RPMS/librdmacm-devel-*.x86_64.rpm | cpio -idm && \
    rpm2cpio /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.2-x86_64/RPMS/librdmacm-*.x86_64.rpm | cpio -idm && \
    rm -rf /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.2-x86_64.tgz /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.2-x86_64''')

    @aarch64
    @ubuntu
    @docker
    def test_aarch64_ubuntu(self):
        """aarch64"""
        mofed = mlnx_ofed(version='4.5-1.0.1.0')
        self.assertEqual(str(mofed),
r'''# Mellanox OFED version 4.5-1.0.1.0
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libnl-3-200 \
        libnl-route-3-200 \
        libnuma1 \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp http://content.mellanox.com/ofed/MLNX_OFED-4.5-1.0.1.0/MLNX_OFED_LINUX-4.5-1.0.1.0-ubuntu16.04-aarch64.tgz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/MLNX_OFED_LINUX-4.5-1.0.1.0-ubuntu16.04-aarch64.tgz -C /var/tmp -z && \
    dpkg --install /var/tmp/MLNX_OFED_LINUX-4.5-1.0.1.0-ubuntu16.04-aarch64/DEBS/libibverbs1_*_arm64.deb /var/tmp/MLNX_OFED_LINUX-4.5-1.0.1.0-ubuntu16.04-aarch64/DEBS/libibverbs-dev_*_arm64.deb /var/tmp/MLNX_OFED_LINUX-4.5-1.0.1.0-ubuntu16.04-aarch64/DEBS/ibverbs-utils_*_arm64.deb /var/tmp/MLNX_OFED_LINUX-4.5-1.0.1.0-ubuntu16.04-aarch64/DEBS/libibmad_*_arm64.deb /var/tmp/MLNX_OFED_LINUX-4.5-1.0.1.0-ubuntu16.04-aarch64/DEBS/libibmad-devel_*_arm64.deb /var/tmp/MLNX_OFED_LINUX-4.5-1.0.1.0-ubuntu16.04-aarch64/DEBS/libibumad_*_arm64.deb /var/tmp/MLNX_OFED_LINUX-4.5-1.0.1.0-ubuntu16.04-aarch64/DEBS/libibumad-devel_*_arm64.deb /var/tmp/MLNX_OFED_LINUX-4.5-1.0.1.0-ubuntu16.04-aarch64/DEBS/libmlx4-1_*_arm64.deb /var/tmp/MLNX_OFED_LINUX-4.5-1.0.1.0-ubuntu16.04-aarch64/DEBS/libmlx4-dev_*_arm64.deb /var/tmp/MLNX_OFED_LINUX-4.5-1.0.1.0-ubuntu16.04-aarch64/DEBS/libmlx5-1_*_arm64.deb /var/tmp/MLNX_OFED_LINUX-4.5-1.0.1.0-ubuntu16.04-aarch64/DEBS/libmlx5-dev_*_arm64.deb /var/tmp/MLNX_OFED_LINUX-4.5-1.0.1.0-ubuntu16.04-aarch64/DEBS/librdmacm-dev_*_arm64.deb /var/tmp/MLNX_OFED_LINUX-4.5-1.0.1.0-ubuntu16.04-aarch64/DEBS/librdmacm1_*_arm64.deb && \
    rm -rf /var/tmp/MLNX_OFED_LINUX-4.5-1.0.1.0-ubuntu16.04-aarch64.tgz /var/tmp/MLNX_OFED_LINUX-4.5-1.0.1.0-ubuntu16.04-aarch64''')

    @aarch64
    @ubuntu18
    @docker
    def test_aarch64_ubuntu18(self):
        """aarch64"""
        mofed = mlnx_ofed(version='4.6-1.0.1.1')
        self.assertEqual(str(mofed),
r'''# Mellanox OFED version 4.6-1.0.1.1
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libnl-3-200 \
        libnl-route-3-200 \
        libnuma1 \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp http://content.mellanox.com/ofed/MLNX_OFED-4.6-1.0.1.1/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu18.04-aarch64.tgz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu18.04-aarch64.tgz -C /var/tmp -z && \
    dpkg --install /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu18.04-aarch64/DEBS/libibverbs1_*_arm64.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu18.04-aarch64/DEBS/libibverbs-dev_*_arm64.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu18.04-aarch64/DEBS/ibverbs-utils_*_arm64.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu18.04-aarch64/DEBS/libibmad_*_arm64.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu18.04-aarch64/DEBS/libibmad-devel_*_arm64.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu18.04-aarch64/DEBS/libibumad_*_arm64.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu18.04-aarch64/DEBS/libibumad-devel_*_arm64.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu18.04-aarch64/DEBS/libmlx4-1_*_arm64.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu18.04-aarch64/DEBS/libmlx4-dev_*_arm64.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu18.04-aarch64/DEBS/libmlx5-1_*_arm64.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu18.04-aarch64/DEBS/libmlx5-dev_*_arm64.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu18.04-aarch64/DEBS/librdmacm-dev_*_arm64.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu18.04-aarch64/DEBS/librdmacm1_*_arm64.deb && \
    rm -rf /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu18.04-aarch64.tgz /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu18.04-aarch64''')

    @aarch64
    @centos
    @docker
    def test_aarch64_centos(self):
        """aarch64"""
        mofed = mlnx_ofed()
        self.assertEqual(str(mofed),
r'''# Mellanox OFED version 4.6-1.0.1.1
RUN yum install -y \
        libnl \
        libnl3 \
        numactl-libs \
        wget && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp http://content.mellanox.com/ofed/MLNX_OFED-4.6-1.0.1.1/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.6alternate-aarch64.tgz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.6alternate-aarch64.tgz -C /var/tmp -z && \
    rpm --install /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.6alternate-aarch64/RPMS/libibverbs-*.aarch64.rpm /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.6alternate-aarch64/RPMS/libibverbs-devel-*.aarch64.rpm /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.6alternate-aarch64/RPMS/libibverbs-utils-*.aarch64.rpm /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.6alternate-aarch64/RPMS/libibmad-*.aarch64.rpm /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.6alternate-aarch64/RPMS/libibmad-devel-*.aarch64.rpm /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.6alternate-aarch64/RPMS/libibumad-*.aarch64.rpm /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.6alternate-aarch64/RPMS/libibumad-devel-*.aarch64.rpm /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.6alternate-aarch64/RPMS/libmlx4-*.aarch64.rpm /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.6alternate-aarch64/RPMS/libmlx4-devel-*.aarch64.rpm /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.6alternate-aarch64/RPMS/libmlx5-*.aarch64.rpm /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.6alternate-aarch64/RPMS/libmlx5-devel-*.aarch64.rpm /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.6alternate-aarch64/RPMS/librdmacm-devel-*.aarch64.rpm /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.6alternate-aarch64/RPMS/librdmacm-*.aarch64.rpm && \
    rm -rf /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.6alternate-aarch64.tgz /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.6alternate-aarch64''')

    @ppc64le
    @ubuntu
    @docker
    def test_ppc64le_ubuntu(self):
        """aarch64"""
        mofed = mlnx_ofed(version='4.6-1.0.1.1')
        self.assertEqual(str(mofed),
r'''# Mellanox OFED version 4.6-1.0.1.1
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libnl-3-200 \
        libnl-route-3-200 \
        libnuma1 \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp http://content.mellanox.com/ofed/MLNX_OFED-4.6-1.0.1.1/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-ppc64le.tgz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-ppc64le.tgz -C /var/tmp -z && \
    dpkg --install /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-ppc64le/DEBS/libibverbs1_*_ppc64el.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-ppc64le/DEBS/libibverbs-dev_*_ppc64el.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-ppc64le/DEBS/ibverbs-utils_*_ppc64el.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-ppc64le/DEBS/libibmad_*_ppc64el.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-ppc64le/DEBS/libibmad-devel_*_ppc64el.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-ppc64le/DEBS/libibumad_*_ppc64el.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-ppc64le/DEBS/libibumad-devel_*_ppc64el.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-ppc64le/DEBS/libmlx4-1_*_ppc64el.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-ppc64le/DEBS/libmlx4-dev_*_ppc64el.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-ppc64le/DEBS/libmlx5-1_*_ppc64el.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-ppc64le/DEBS/libmlx5-dev_*_ppc64el.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-ppc64le/DEBS/librdmacm-dev_*_ppc64el.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-ppc64le/DEBS/librdmacm1_*_ppc64el.deb && \
    rm -rf /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-ppc64le.tgz /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-ppc64le''')

    @ppc64le
    @ubuntu18
    @docker
    def test_ppc64le_ubuntu18(self):
        """aarch64"""
        mofed = mlnx_ofed(version='4.6-1.0.1.1')
        self.assertEqual(str(mofed),
r'''# Mellanox OFED version 4.6-1.0.1.1
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libnl-3-200 \
        libnl-route-3-200 \
        libnuma1 \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp http://content.mellanox.com/ofed/MLNX_OFED-4.6-1.0.1.1/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu18.04-ppc64le.tgz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu18.04-ppc64le.tgz -C /var/tmp -z && \
    dpkg --install /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu18.04-ppc64le/DEBS/libibverbs1_*_ppc64el.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu18.04-ppc64le/DEBS/libibverbs-dev_*_ppc64el.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu18.04-ppc64le/DEBS/ibverbs-utils_*_ppc64el.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu18.04-ppc64le/DEBS/libibmad_*_ppc64el.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu18.04-ppc64le/DEBS/libibmad-devel_*_ppc64el.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu18.04-ppc64le/DEBS/libibumad_*_ppc64el.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu18.04-ppc64le/DEBS/libibumad-devel_*_ppc64el.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu18.04-ppc64le/DEBS/libmlx4-1_*_ppc64el.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu18.04-ppc64le/DEBS/libmlx4-dev_*_ppc64el.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu18.04-ppc64le/DEBS/libmlx5-1_*_ppc64el.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu18.04-ppc64le/DEBS/libmlx5-dev_*_ppc64el.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu18.04-ppc64le/DEBS/librdmacm-dev_*_ppc64el.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu18.04-ppc64le/DEBS/librdmacm1_*_ppc64el.deb && \
    rm -rf /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu18.04-ppc64le.tgz /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu18.04-ppc64le''')

    @ppc64le
    @centos
    @docker
    def test_ppc64le_centos(self):
        """aarch64"""
        mofed = mlnx_ofed(version='4.6-1.0.1.1')
        self.assertEqual(str(mofed),
r'''# Mellanox OFED version 4.6-1.0.1.1
RUN yum install -y \
        libnl \
        libnl3 \
        numactl-libs \
        wget && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp http://content.mellanox.com/ofed/MLNX_OFED-4.6-1.0.1.1/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.2-ppc64le.tgz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.2-ppc64le.tgz -C /var/tmp -z && \
    rpm --install /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.2-ppc64le/RPMS/libibverbs-*.ppc64le.rpm /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.2-ppc64le/RPMS/libibverbs-devel-*.ppc64le.rpm /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.2-ppc64le/RPMS/libibverbs-utils-*.ppc64le.rpm /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.2-ppc64le/RPMS/libibmad-*.ppc64le.rpm /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.2-ppc64le/RPMS/libibmad-devel-*.ppc64le.rpm /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.2-ppc64le/RPMS/libibumad-*.ppc64le.rpm /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.2-ppc64le/RPMS/libibumad-devel-*.ppc64le.rpm /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.2-ppc64le/RPMS/libmlx4-*.ppc64le.rpm /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.2-ppc64le/RPMS/libmlx4-devel-*.ppc64le.rpm /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.2-ppc64le/RPMS/libmlx5-*.ppc64le.rpm /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.2-ppc64le/RPMS/libmlx5-devel-*.ppc64le.rpm /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.2-ppc64le/RPMS/librdmacm-devel-*.ppc64le.rpm /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.2-ppc64le/RPMS/librdmacm-*.ppc64le.rpm && \
    rm -rf /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.2-ppc64le.tgz /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-rhel7.2-ppc64le''')

    @x86_64
    @ubuntu
    @docker
    def test_runtime(self):
        """Runtime"""
        mofed = mlnx_ofed()
        r = mofed.runtime()
        self.assertEqual(r,
r'''# Mellanox OFED version 4.6-1.0.1.1
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libnl-3-200 \
        libnl-route-3-200 \
        libnuma1 \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp http://content.mellanox.com/ofed/MLNX_OFED-4.6-1.0.1.1/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64.tgz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64.tgz -C /var/tmp -z && \
    dpkg --install /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64/DEBS/libibverbs1_*_amd64.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64/DEBS/libibverbs-dev_*_amd64.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64/DEBS/ibverbs-utils_*_amd64.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64/DEBS/libibmad_*_amd64.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64/DEBS/libibmad-devel_*_amd64.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64/DEBS/libibumad_*_amd64.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64/DEBS/libibumad-devel_*_amd64.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64/DEBS/libmlx4-1_*_amd64.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64/DEBS/libmlx4-dev_*_amd64.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64/DEBS/libmlx5-1_*_amd64.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64/DEBS/libmlx5-dev_*_amd64.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64/DEBS/librdmacm-dev_*_amd64.deb /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64/DEBS/librdmacm1_*_amd64.deb && \
    rm -rf /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64.tgz /var/tmp/MLNX_OFED_LINUX-4.6-1.0.1.1-ubuntu16.04-x86_64''')

    @x86_64
    @ubuntu
    @docker
    def test_prefix_runtime(self):
        """Prefix runtime"""
        mofed = mlnx_ofed(prefix='/opt/ofed')
        r = mofed.runtime()
        self.assertEqual(r,
r'''# Mellanox OFED version 4.6-1.0.1.1
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libnl-3-200 \
        libnl-route-3-200 \
        libnuma1 \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /etc/libibverbs.d
COPY --from=0 /opt/ofed /opt/ofed''')
