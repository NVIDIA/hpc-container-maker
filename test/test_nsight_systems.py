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

"""Test cases for the nsight_systems module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import aarch64, centos, centos8, docker, ppc64le, ubuntu, ubuntu18, x86_64

from hpccm.building_blocks.nsight_systems import nsight_systems

class Test_nsight_systems(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @x86_64
    @ubuntu
    @docker
    def test_basic_ubuntu(self):
        """Default nsight_systems building block"""
        n = nsight_systems()
        self.assertEqual(str(n),
r'''# NVIDIA Nsight Systems 2020.2.1
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        apt-transport-https \
        ca-certificates \
        gnupg \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN wget -qO - https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64/7fa2af80.pub | apt-key add - && \
    echo "deb https://developer.download.nvidia.com/devtools/repo-deb/x86_64/ /" >> /etc/apt/sources.list.d/hpccm.list && \
    apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        nsight-systems-cli-2020.2.1 && \
    rm -rf /var/lib/apt/lists/*''')

    @x86_64
    @centos8
    @docker
    def test_basic_centos8(self):
        """Default nsight_systems building block"""
        n = nsight_systems()
        self.assertEqual(str(n),
r'''# NVIDIA Nsight Systems 2020.2.1
RUN rpm --import https://developer.download.nvidia.com/compute/cuda/repos/rhel8/x86_64/7fa2af80.pub && \
    yum install -y dnf-utils && \
    yum-config-manager --add-repo https://developer.download.nvidia.com/devtools/repo-rpm/x86_64 && \
    yum install -y \
        nsight-systems-cli-2020.2.1 && \
    rm -rf /var/cache/yum/*''')

    @x86_64
    @ubuntu
    @docker
    def test_version(self):
        """Version option"""
        n = nsight_systems(version='2020.1.1')
        self.assertEqual(str(n),
r'''# NVIDIA Nsight Systems 2020.1.1
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        apt-transport-https \
        ca-certificates \
        gnupg \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN wget -qO - https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64/7fa2af80.pub | apt-key add - && \
    echo "deb https://developer.download.nvidia.com/devtools/repo-deb/x86_64/ /" >> /etc/apt/sources.list.d/hpccm.list && \
    apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        nsight-systems-cli-2020.1.1 && \
    rm -rf /var/lib/apt/lists/*''')

    @x86_64
    @ubuntu
    @docker
    def test_cli(self):
        """cli option"""
        n = nsight_systems(cli=False, version='2020.1.1')
        self.assertEqual(str(n),
r'''# NVIDIA Nsight Systems 2020.1.1
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        apt-transport-https \
        ca-certificates \
        gnupg \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN wget -qO - https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64/7fa2af80.pub | apt-key add - && \
    echo "deb https://developer.download.nvidia.com/devtools/repo-deb/x86_64/ /" >> /etc/apt/sources.list.d/hpccm.list && \
    apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        nsight-systems-2020.1.1 && \
    rm -rf /var/lib/apt/lists/*''')

    @ppc64le
    @ubuntu18
    @docker
    def test_ppc64le_ubuntu18(self):
        """Power"""
        n = nsight_systems(version='2020.1.1')
        self.assertEqual(str(n),
r'''# NVIDIA Nsight Systems 2020.1.1
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        apt-transport-https \
        ca-certificates \
        gnupg \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN wget -qO - https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/ppc64el/7fa2af80.pub | apt-key add - && \
    echo "deb https://developer.download.nvidia.com/devtools/repo-deb/ppc64/ /" >> /etc/apt/sources.list.d/hpccm.list && \
    apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        nsight-systems-cli-2020.1.1 && \
    rm -rf /var/lib/apt/lists/*''')

    @ppc64le
    @centos
    @docker
    def test_ppc64le_centos(self):
        """Power"""
        n = nsight_systems(version='2020.1.1')
        self.assertEqual(str(n),
r'''# NVIDIA Nsight Systems 2020.1.1
RUN rpm --import https://developer.download.nvidia.com/compute/cuda/repos/rhel7/ppc64le/7fa2af80.pub && \
    yum install -y yum-utils && \
    yum-config-manager --add-repo https://developer.download.nvidia.com/devtools/repo-rpm/ppc64 && \
    yum install -y \
        nsight-systems-cli-2020.1.1 && \
    rm -rf /var/cache/yum/*''')

    @aarch64
    @centos
    @docker
    def test_aarch64_centos(self):
        """Power"""
        n = nsight_systems(version='2020.2.1')
        self.assertEqual(str(n),
r'''# NVIDIA Nsight Systems 2020.2.1
RUN rpm --import https://developer.download.nvidia.com/compute/cuda/repos/rhel7/x86_64/7fa2af80.pub && \
    yum install -y yum-utils && \
    yum-config-manager --add-repo https://developer.download.nvidia.com/devtools/repo-rpm/arm64 && \
    yum install -y \
        nsight-systems-cli-2020.2.1 && \
    rm -rf /var/cache/yum/*''')
