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

from helpers import docker

from hpccm.mlnx_ofed import mlnx_ofed

class Test_mlnx_ofed(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @docker
    def test_defaults(self):
        """Default mlnx_ofed building block"""
        mofed = mlnx_ofed()
        self.assertEqual(str(mofed),
r'''# Mellanox OFED version 3.4-1.0.0.0
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        libnl-3-200 \
        libnl-route-3-200 \
        libnuma1 \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /tmp && wget -q --no-check-certificate -P /tmp http://content.mellanox.com/ofed/MLNX_OFED-3.4-1.0.0.0/MLNX_OFED_LINUX-3.4-1.0.0.0-ubuntu16.04-x86_64.tgz && \
    tar -x -f /tmp/MLNX_OFED_LINUX-3.4-1.0.0.0-ubuntu16.04-x86_64.tgz -C /tmp -z && \
    dpkg --install /tmp/MLNX_OFED_LINUX-3.4-1.0.0.0-ubuntu16.04-x86_64/DEBS/libibverbs1_*_amd64.deb && \
    dpkg --install /tmp/MLNX_OFED_LINUX-3.4-1.0.0.0-ubuntu16.04-x86_64/DEBS/libibverbs-dev_*_amd64.deb && \
    dpkg --install /tmp/MLNX_OFED_LINUX-3.4-1.0.0.0-ubuntu16.04-x86_64/DEBS/libibumad_*_amd64.deb && \
    dpkg --install /tmp/MLNX_OFED_LINUX-3.4-1.0.0.0-ubuntu16.04-x86_64/DEBS/libibmad_*_amd64.deb && \
    dpkg --install /tmp/MLNX_OFED_LINUX-3.4-1.0.0.0-ubuntu16.04-x86_64/DEBS/libmlx5-1_*_amd64.deb && \
    dpkg --install /tmp/MLNX_OFED_LINUX-3.4-1.0.0.0-ubuntu16.04-x86_64/DEBS/ibverbs-utils_*_amd64.deb && \
    rm -rf /tmp/MLNX_OFED_LINUX-3.4-1.0.0.0-ubuntu16.04-x86_64.tgz /tmp/MLNX_OFED_LINUX-3.4-1.0.0.0-ubuntu16.04-x86_64''')

    @docker
    def test_runtime(self):
        """Runtime"""
        mofed = mlnx_ofed()
        r = mofed.runtime()
        self.assertEqual(str(r),
r'''# Mellanox OFED version 3.4-1.0.0.0
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        libnl-3-200 \
        libnl-route-3-200 \
        libnuma1 \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /tmp && wget -q --no-check-certificate -P /tmp http://content.mellanox.com/ofed/MLNX_OFED-3.4-1.0.0.0/MLNX_OFED_LINUX-3.4-1.0.0.0-ubuntu16.04-x86_64.tgz && \
    tar -x -f /tmp/MLNX_OFED_LINUX-3.4-1.0.0.0-ubuntu16.04-x86_64.tgz -C /tmp -z && \
    dpkg --install /tmp/MLNX_OFED_LINUX-3.4-1.0.0.0-ubuntu16.04-x86_64/DEBS/libibverbs1_*_amd64.deb && \
    dpkg --install /tmp/MLNX_OFED_LINUX-3.4-1.0.0.0-ubuntu16.04-x86_64/DEBS/libibverbs-dev_*_amd64.deb && \
    dpkg --install /tmp/MLNX_OFED_LINUX-3.4-1.0.0.0-ubuntu16.04-x86_64/DEBS/libibumad_*_amd64.deb && \
    dpkg --install /tmp/MLNX_OFED_LINUX-3.4-1.0.0.0-ubuntu16.04-x86_64/DEBS/libibmad_*_amd64.deb && \
    dpkg --install /tmp/MLNX_OFED_LINUX-3.4-1.0.0.0-ubuntu16.04-x86_64/DEBS/libmlx5-1_*_amd64.deb && \
    dpkg --install /tmp/MLNX_OFED_LINUX-3.4-1.0.0.0-ubuntu16.04-x86_64/DEBS/ibverbs-utils_*_amd64.deb && \
    rm -rf /tmp/MLNX_OFED_LINUX-3.4-1.0.0.0-ubuntu16.04-x86_64.tgz /tmp/MLNX_OFED_LINUX-3.4-1.0.0.0-ubuntu16.04-x86_64''')
