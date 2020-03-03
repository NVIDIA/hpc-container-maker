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

"""Test cases for the ofed module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import aarch64, centos, centos8, docker, ubuntu, ubuntu18, ppc64le, x86_64

from hpccm.building_blocks.ofed import ofed

class Test_ofed(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @x86_64
    @ubuntu
    @docker
    def test_defaults_ubuntu(self):
        """Default ofed building block"""
        o = ofed()
        self.assertEqual(str(o),
r'''# OFED
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends -t xenial \
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
    rm -rf /var/lib/apt/lists/*''')

    @x86_64
    @ubuntu18
    @docker
    def test_defaults_ubuntu18(self):
        """Default ofed building block"""
        o = ofed()
        self.assertEqual(str(o),
r'''# OFED
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends -t bionic \
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
    rm -rf /var/lib/apt/lists/*''')

    @x86_64
    @centos
    @docker
    def test_defaults_centos(self):
        """Default ofed building block"""
        o = ofed()
        self.assertEqual(str(o),
r'''# OFED
RUN yum install -y --disablerepo=mlnx\* \
        dapl \
        dapl-devel \
        ibutils \
        libibcm \
        libibmad \
        libibmad-devel \
        libibumad \
        libibverbs \
        libibverbs-utils \
        libmlx5 \
        librdmacm \
        rdma-core \
        rdma-core-devel && \
    rm -rf /var/cache/yum/*''')

    @x86_64
    @centos8
    @docker
    def test_defaults_centos8(self):
        """Default ofed building block"""
        o = ofed()
        self.assertEqual(str(o),
r'''# OFED
RUN yum install -y dnf-utils && \
    yum-config-manager --set-enabled PowerTools && \
    yum install -y --disablerepo=mlnx\* \
        libibmad \
        libibmad-devel \
        libibumad \
        libibverbs \
        libibverbs-utils \
        libmlx5 \
        librdmacm \
        rdma-core \
        rdma-core-devel && \
    rm -rf /var/cache/yum/*''')

    @x86_64
    @ubuntu
    @docker
    def test_prefix_ubuntu16(self):
        o = ofed(prefix='/usr/local/ofed')
        self.assertEqual(str(o),
r'''# OFED
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libnl-3-200 \
        libnl-route-3-200 \
        libnuma1 && \
    rm -rf /var/lib/apt/lists/*
RUN apt-get update -y && \
    mkdir -m 777 -p /var/tmp/packages_download && cd /var/tmp/packages_download && \
    DEBIAN_FRONTEND=noninteractive apt-get download -y --no-install-recommends -t xenial \
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
    mkdir -p /usr/local/ofed && \
    find /var/tmp/packages_download -regextype posix-extended -type f -regex "/var/tmp/packages_download/(dapl2-utils|ibutils|ibverbs-utils|infiniband-diags|libdapl-dev|libdapl2|libibcm-dev|libibcm1|libibmad-dev|libibmad5|libibverbs-dev|libibverbs1|libmlx4-1|libmlx4-dev|libmlx5-1|libmlx5-dev|librdmacm-dev|librdmacm1|rdmacm-utils).*deb" -exec dpkg --extract {} /usr/local/ofed \; && \
    rm -rf /var/tmp/packages_download && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /etc/libibverbs.d''')

    @aarch64
    @ubuntu
    @docker
    def test_aarch64_ubuntu16(self):
        """aarch64"""
        o = ofed()
        self.assertEqual(str(o),
r'''# OFED
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends -t xenial \
        ibutils \
        ibverbs-utils \
        infiniband-diags \
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
    rm -rf /var/lib/apt/lists/*''')

    @ppc64le
    @ubuntu
    @docker
    def test_ppc64le_ubuntu16(self):
        """ppc64le"""
        o = ofed()
        self.assertEqual(str(o),
r'''# OFED
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends -t xenial \
        dapl2-utils \
        ibutils \
        ibverbs-utils \
        infiniband-diags \
        libdapl-dev \
        libdapl2 \
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
    rm -rf /var/lib/apt/lists/*''')

    @x86_64
    @ubuntu
    @docker
    def test_runtime(self):
        """Runtime"""
        o = ofed()
        r = o.runtime()
        self.assertEqual(r,
r'''# OFED
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends -t xenial \
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
    rm -rf /var/lib/apt/lists/*''')

    @ubuntu
    @docker
    def test_runtime_prefix(self):
        """Prefix + runtime"""
        o = ofed(prefix='/usr/local/ofed')
        r = o.runtime()
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
