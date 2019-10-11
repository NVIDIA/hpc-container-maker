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

# pylint: disable=invalid-name, too-few-public-methods

"""Test cases for the yum module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import aarch64, centos, centos8, docker, x86_64

from hpccm.building_blocks.yum import yum

class Test_yum(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @x86_64
    @centos
    @docker
    def test_basic(self):
        """Basic yum"""
        y = yum(ospackages=['gcc', 'gcc-c++', 'gcc-fortran'])
        self.assertEqual(str(y),
r'''RUN yum install -y \
        gcc \
        gcc-c++ \
        gcc-fortran && \
    rm -rf /var/cache/yum/*''')

    @x86_64
    @centos
    @docker
    def test_add_repo(self):
        """Add repo and key"""
        y = yum(keys=['https://www.example.com/key.pub'],
                ospackages=['example'],
                repositories=['http://www.example.com/example.repo'])
        self.assertEqual(str(y),
r'''RUN rpm --import https://www.example.com/key.pub && \
    yum install -y yum-utils && \
    yum-config-manager --add-repo http://www.example.com/example.repo && \
    yum install -y \
        example && \
    rm -rf /var/cache/yum/*''')

    @x86_64
    @centos8
    @docker
    def test_add_repo_centos8(self):
        """Add repo and key"""
        y = yum(keys=['https://www.example.com/key.pub'],
                ospackages=['example'],
                repositories=['http://www.example.com/example.repo'])
        self.assertEqual(str(y),
r'''RUN rpm --import https://www.example.com/key.pub && \
    yum install -y dnf-utils && \
    yum-config-manager --add-repo http://www.example.com/example.repo && \
    yum install -y \
        example && \
    rm -rf /var/cache/yum/*''')

    @x86_64
    @centos8
    @docker
    def test_add_repo_powertools_centos8(self):
        """Add repo and key and enable PowerTools"""
        y = yum(keys=['https://www.example.com/key.pub'],
                ospackages=['example'],
                repositories=['http://www.example.com/example.repo'],
                powertools=True)
        self.assertEqual(str(y),
r'''RUN rpm --import https://www.example.com/key.pub && \
    yum install -y dnf-utils && \
    yum-config-manager --add-repo http://www.example.com/example.repo && \
    yum-config-manager --set-enabled PowerTools && \
    yum install -y \
        example && \
    rm -rf /var/cache/yum/*''')

    @x86_64
    @centos
    @docker
    def test_download(self):
        """Download parameter"""
        y = yum(download=True, download_directory='/tmp/download',
                ospackages=['rdma-core'])
        self.assertEqual(str(y),
r'''RUN yum install -y yum-utils && \
    mkdir -p /tmp/download && \
    yumdownloader --destdir=/tmp/download -x \*i?86 --archlist=x86_64 \
        rdma-core && \
    rm -rf /var/cache/yum/*''')

    @aarch64
    @centos
    @docker
    def test_download_aarch64(self):
        """Download parameter"""
        y = yum(download=True, download_directory='/tmp/download',
                ospackages=['rdma-core'])
        self.assertEqual(str(y),
r'''RUN yum install -y yum-utils && \
    mkdir -p /tmp/download && \
    yumdownloader --destdir=/tmp/download  \
        rdma-core && \
    rm -rf /var/cache/yum/*''')

    @x86_64
    @centos
    @docker
    def test_extract(self):
        """Extract parameter"""
        y = yum(download=True, extract='/usr/local/ofed',
                ospackages=['rdma-core'])
        self.assertEqual(str(y),
r'''RUN yum install -y yum-utils && \
    mkdir -p /var/tmp/yum_download && \
    yumdownloader --destdir=/var/tmp/yum_download -x \*i?86 --archlist=x86_64 \
        rdma-core && \
    mkdir -p /usr/local/ofed && cd /usr/local/ofed && \
    find /var/tmp/yum_download -regextype posix-extended -type f -regex "/var/tmp/yum_download/(rdma-core).*rpm" -exec sh -c "rpm2cpio {} | cpio -idm" \; && \
    rm -rf /var/tmp/yum_download && \
    rm -rf /var/cache/yum/*''')

    @x86_64
    @centos
    @docker
    def test_powertools_centos7(self):
        """Powertools repo"""
        y = yum(ospackages=['hwloc-devel'], powertools=True)
        self.assertEqual(str(y),
r'''RUN yum install -y \
        hwloc-devel && \
    rm -rf /var/cache/yum/*''')

    @x86_64
    @centos8
    @docker
    def test_powertools_centos8(self):
        """Powertools repo"""
        y = yum(ospackages=['hwloc-devel'], powertools=True)
        self.assertEqual(str(y),
r'''RUN yum install -y dnf-utils && \
    yum-config-manager --set-enabled PowerTools && \
    yum install -y \
        hwloc-devel && \
    rm -rf /var/cache/yum/*''')
