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

"""Test cases for the pgi module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from hpccm.common import container_type
from hpccm.pgi import pgi

class Test_pgi(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    def test_defaults(self):
        """Default pgi building block"""
        p = pgi()
        self.assertEqual(p.toString(container_type.DOCKER),
r'''# PGI compiler version 17.10
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        libnuma1 \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /tmp/pgi && wget -q --no-check-certificate -O /tmp/pgi/pgi-community-linux-x64-latest.tar.gz --referer http://www.pgroup.com/products/community.htm -P /tmp/pgi http://www.pgroup.com/support/downloader.php?file=pgi-community-linux-x64 && \
    tar -x -f /tmp/pgi/pgi-community-linux-x64-latest.tar.gz -C /tmp/pgi -z && \
    cd /tmp/pgi && PGI_ACCEPT_EULA=decline ./install && \
    rm -rf /tmp/pgi/pgi-community-linux-x64-latest.tar.gz /tmp/pgi
ENV LD_LIBRARY_PATH=/opt/pgi/linux86-64/17.10/lib:$LD_LIBRARY_PATH \
    PATH=/opt/pgi/linux86-64/17.10/bin:$PATH''')

    def test_eula(self):
        """Accept EULA"""
        p = pgi(eula=True)
        self.assertEqual(p.toString(container_type.DOCKER),
r'''# PGI compiler version 17.10
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        libnuma1 \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /tmp/pgi && wget -q --no-check-certificate -O /tmp/pgi/pgi-community-linux-x64-latest.tar.gz --referer http://www.pgroup.com/products/community.htm -P /tmp/pgi http://www.pgroup.com/support/downloader.php?file=pgi-community-linux-x64 && \
    tar -x -f /tmp/pgi/pgi-community-linux-x64-latest.tar.gz -C /tmp/pgi -z && \
    cd /tmp/pgi && PGI_SILENT=true PGI_ACCEPT_EULA=accept ./install && \
    rm -rf /tmp/pgi/pgi-community-linux-x64-latest.tar.gz /tmp/pgi
ENV LD_LIBRARY_PATH=/opt/pgi/linux86-64/17.10/lib:$LD_LIBRARY_PATH \
    PATH=/opt/pgi/linux86-64/17.10/bin:$PATH''')

    def test_tarball(self):
        """tarball"""
        p = pgi(eula=True, tarball='pgilinux-2017-1710-x86_64.tar.gz')
        self.assertEqual(p.toString(container_type.DOCKER),
r'''# PGI compiler version 17.10
COPY pgilinux-2017-1710-x86_64.tar.gz /tmp/pgi/pgilinux-2017-1710-x86_64.tar.gz
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        libnuma1 && \
    rm -rf /var/lib/apt/lists/*
RUN tar -x -f /tmp/pgi/pgilinux-2017-1710-x86_64.tar.gz -C /tmp/pgi -z && \
    cd /tmp/pgi && PGI_SILENT=true PGI_ACCEPT_EULA=accept ./install && \
    rm -rf /tmp/pgi/pgilinux-2017-1710-x86_64.tar.gz /tmp/pgi
ENV LD_LIBRARY_PATH=/opt/pgi/linux86-64/17.10/lib:$LD_LIBRARY_PATH \
    PATH=/opt/pgi/linux86-64/17.10/bin:$PATH''')

    def test_runtime(self):
        """Runtime"""
        p = pgi()
        r = p.runtime()
        s = '\n'.join(x.toString(container_type.DOCKER) for x in r)
        self.maxDiff = None
        self.assertEqual(s,
r'''# PGI compiler
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        libnuma1 && \
    rm -rf /var/lib/apt/lists/*
COPY --from=0 /opt/pgi/linux86-64/17.10/REDIST/*.so /opt/pgi/linux86-64/17.10/lib/
RUN ln -s /opt/pgi/linux86-64/17.10/lib/libpgnuma.so /opt/pgi/linux86-64/17.10/lib/libnuma.so
ENV LD_LIBRARY_PATH=/opt/pgi/linux86-64/17.10/lib:$LD_LIBRARY_PATH''')

    def test_toolchain(self):
        """Toolchain"""
        p = pgi()
        tc = p.toolchain
        self.assertEqual(tc.CC, 'pgcc')
        self.assertEqual(tc.CXX, 'pgc++')
        self.assertEqual(tc.FC, 'pgfortran')
        self.assertEqual(tc.F77, 'pgfortran')
        self.assertEqual(tc.F90, 'pgfortran')
