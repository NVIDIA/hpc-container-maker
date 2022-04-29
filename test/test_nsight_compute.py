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

"""Test cases for the nsight_compute module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import aarch64, centos, centos8, docker, ppc64le, ubuntu, ubuntu18, x86_64

from hpccm.building_blocks.nsight_compute import nsight_compute

class Test_nsight_compute(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @x86_64
    @ubuntu
    @docker
    def test_basic_ubuntu(self):
        """Default nsight_compute building block"""
        n = nsight_compute()
        self.assertEqual(str(n),
r'''# NVIDIA Nsight Compute 2022.1.1
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        apt-transport-https \
        ca-certificates \
        gnupg \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN wget -qO - https://developer.download.nvidia.com/devtools/repos/ubuntu1604/amd64/nvidia.pub | apt-key add - && \
    echo "deb https://developer.download.nvidia.com/devtools/repos/ubuntu1604/amd64/ /" >> /etc/apt/sources.list.d/hpccm.list && \
    apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        nsight-compute-2022.1.1 && \
    rm -rf /var/lib/apt/lists/*
ENV NV_COMPUTE_PROFILER_DISABLE_STOCK_FILE_DEPLOYMENT=1 \
    PATH=/opt/nvidia/nsight-compute/2022.1.1:$PATH''')

    @x86_64
    @centos8
    @docker
    def test_basic_centos8(self):
        """Default nsight_compute building block"""
        n = nsight_compute()
        self.assertEqual(str(n),
r'''# NVIDIA Nsight Compute 2022.1.1
RUN rpm --import https://developer.download.nvidia.com/devtools/repos/rhel8/x86_64/nvidia.pub && \
    yum install -y dnf-utils && \
    (yum-config-manager --add-repo https://developer.download.nvidia.com/devtools/repos/rhel8/x86_64 || true) && \
    yum install -y \
        nsight-compute-2022.1.1 && \
    rm -rf /var/cache/yum/*
ENV NV_COMPUTE_PROFILER_DISABLE_STOCK_FILE_DEPLOYMENT=1 \
    PATH=/opt/nvidia/nsight-compute/2022.1.1:$PATH''')

    @x86_64
    @ubuntu
    @docker
    def test_version(self):
        """Version option"""
        n = nsight_compute(version='2020.2.1')
        self.assertEqual(str(n),
r'''# NVIDIA Nsight Compute 2020.2.1
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        apt-transport-https \
        ca-certificates \
        gnupg \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN wget -qO - https://developer.download.nvidia.com/devtools/repos/ubuntu1604/amd64/nvidia.pub | apt-key add - && \
    echo "deb https://developer.download.nvidia.com/devtools/repos/ubuntu1604/amd64/ /" >> /etc/apt/sources.list.d/hpccm.list && \
    apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        nsight-compute-2020.2.1 && \
    rm -rf /var/lib/apt/lists/*
ENV NV_COMPUTE_PROFILER_DISABLE_STOCK_FILE_DEPLOYMENT=1 \
    PATH=/opt/nvidia/nsight-compute/2020.2.1:$PATH''')

    @ppc64le
    @ubuntu18
    @docker
    def test_ppc64le_ubuntu18(self):
        """Power"""
        n = nsight_compute(version='2020.2.1')
        self.assertEqual(str(n),
r'''# NVIDIA Nsight Compute 2020.2.1
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        apt-transport-https \
        ca-certificates \
        gnupg \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN wget -qO - https://developer.download.nvidia.com/devtools/repos/ubuntu1804/ppc64el/nvidia.pub | apt-key add - && \
    echo "deb https://developer.download.nvidia.com/devtools/repos/ubuntu1804/ppc64el/ /" >> /etc/apt/sources.list.d/hpccm.list && \
    apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        nsight-compute-2020.2.1 && \
    rm -rf /var/lib/apt/lists/*
ENV NV_COMPUTE_PROFILER_DISABLE_STOCK_FILE_DEPLOYMENT=1 \
    PATH=/opt/nvidia/nsight-compute/2020.2.1:$PATH''')

    @ppc64le
    @centos
    @docker
    def test_ppc64le_centos(self):
        """Power"""
        n = nsight_compute(version='2020.2.1')
        self.assertEqual(str(n),
r'''# NVIDIA Nsight Compute 2020.2.1
RUN rpm --import https://developer.download.nvidia.com/devtools/repos/rhel7/ppc64le/nvidia.pub && \
    yum install -y yum-utils && \
    (yum-config-manager --add-repo https://developer.download.nvidia.com/devtools/repos/rhel7/ppc64le || true) && \
    yum install -y \
        nsight-compute-2020.2.1 && \
    rm -rf /var/cache/yum/*
ENV NV_COMPUTE_PROFILER_DISABLE_STOCK_FILE_DEPLOYMENT=1 \
    PATH=/opt/nvidia/nsight-compute/2020.2.1:$PATH''')

    @aarch64
    @centos
    @docker
    def test_aarch64_centos(self):
        """Arm"""
        n = nsight_compute(version='2020.2.1')
        self.assertEqual(str(n),
r'''# NVIDIA Nsight Compute 2020.2.1
RUN rpm --import https://developer.download.nvidia.com/devtools/repos/rhel7/arm64/nvidia.pub && \
    yum install -y yum-utils && \
    (yum-config-manager --add-repo https://developer.download.nvidia.com/devtools/repos/rhel7/arm64 || true) && \
    yum install -y \
        nsight-compute-2020.2.1 && \
    rm -rf /var/cache/yum/*
ENV NV_COMPUTE_PROFILER_DISABLE_STOCK_FILE_DEPLOYMENT=1 \
    PATH=/opt/nvidia/nsight-compute/2020.2.1:$PATH''')

    @x86_64
    @ubuntu
    @docker
    def test_runfile(self):
        """Runfile"""
        n = nsight_compute(eula=True,
                           runfile='nsight_compute-linux-x86_64-2020.2.0.18_28964561.run')
        self.assertEqual(str(n),
r'''# NVIDIA Nsight Compute nsight_compute-linux-x86_64-2020.2.0.18_28964561.run
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        perl \
        wget && \
    rm -rf /var/lib/apt/lists/*
COPY nsight_compute-linux-x86_64-2020.2.0.18_28964561.run /var/tmp/nsight_compute/nsight_compute-linux-x86_64-2020.2.0.18_28964561.run
RUN cd /var/tmp/nsight_compute && \
    sh ./nsight_compute-linux-x86_64-2020.2.0.18_28964561.run --nox11 -- -noprompt -targetpath=/usr/local/NVIDIA-Nsight-Compute && \
    mkdir -p /tmp/var/target && \
    ln -sf /usr/local/NVIDIA-Nsight-Compute/target/* /tmp/var/target && \
    ln -sf /usr/local/NVIDIA-Nsight-Compute/sections /tmp/var/ && \
    chmod -R a+w /tmp/var && \
    rm -rf /var/tmp/nsight_compute /var/tmp/nsight_compute/nsight_compute-linux-x86_64-2020.2.0.18_28964561.run
ENV PATH=/usr/local/NVIDIA-Nsight-Compute:$PATH
ENV NV_COMPUTE_PROFILER_DISABLE_STOCK_FILE_DEPLOYMENT=1''')

    @x86_64
    @ubuntu
    @docker
    def test_basic_ubuntu_url(self):
        """Default nsight_compute building block"""
        n = nsight_compute(eula=True, runfile='https://foo/bar/nsight_compute-linux-x86_64-2020.2.0.18_28964561.run')
        self.assertEqual(str(n),
r'''# NVIDIA Nsight Compute nsight_compute-linux-x86_64-2020.2.0.18_28964561.run
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        perl \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp/nsight_compute && wget -q -nc --no-check-certificate -P /var/tmp/nsight_compute https://foo/bar/nsight_compute-linux-x86_64-2020.2.0.18_28964561.run && \
    cd /var/tmp/nsight_compute && \
    sh ./nsight_compute-linux-x86_64-2020.2.0.18_28964561.run --nox11 -- -noprompt -targetpath=/usr/local/NVIDIA-Nsight-Compute && \
    mkdir -p /tmp/var/target && \
    ln -sf /usr/local/NVIDIA-Nsight-Compute/target/* /tmp/var/target && \
    ln -sf /usr/local/NVIDIA-Nsight-Compute/sections /tmp/var/ && \
    chmod -R a+w /tmp/var && \
    rm -rf /var/tmp/nsight_compute /var/tmp/nsight_compute/nsight_compute-linux-x86_64-2020.2.0.18_28964561.run
ENV PATH=/usr/local/NVIDIA-Nsight-Compute:$PATH
ENV NV_COMPUTE_PROFILER_DISABLE_STOCK_FILE_DEPLOYMENT=1''')
