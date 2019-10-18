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

"""Test cases for the charm module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import aarch64, centos, docker, ppc64le, ubuntu, x86_64

from hpccm.building_blocks.charm import charm

class Test_charm(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @x86_64
    @ubuntu
    @docker
    def test_defaults(self):
        """Default charm building block"""
        c = charm()
        self.assertEqual(str(c),
r'''# Charm++ version 6.9.0
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        autoconf \
        automake \
        git \
        libtool \
        make \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/UIUC-PPL/charm/archive/v6.9.0.tar.gz && \
    mkdir -p /usr/local && tar -x -f /var/tmp/v6.9.0.tar.gz -C /usr/local -z && \
    cd /usr/local/charm-6.9.0 && ./build charm++ multicore-linux-x86_64 --build-shared --with-production -j$(nproc) && \
    rm -rf /var/tmp/v6.9.0.tar.gz
ENV CHARMBASE=/usr/local/charm-6.9.0 \
    LD_LIBRARY_PATH=/usr/local/charm-6.9.0/lib_so:$LD_LIBRARY_PATH \
    PATH=/usr/local/charm-6.9.0/bin:$PATH''')

    @aarch64
    @ubuntu
    @docker
    def test_aarch64(self):
        """Default charm building block"""
        c = charm(version='6.9.0')
        self.assertEqual(str(c),
r'''# Charm++ version 6.9.0
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        autoconf \
        automake \
        git \
        libtool \
        make \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/UIUC-PPL/charm/archive/v6.9.0.tar.gz && \
    mkdir -p /usr/local && tar -x -f /var/tmp/v6.9.0.tar.gz -C /usr/local -z && \
    cd /usr/local/charm-6.9.0 && ./build charm++ multicore-arm8 --build-shared --with-production -j$(nproc) && \
    rm -rf /var/tmp/v6.9.0.tar.gz
ENV CHARMBASE=/usr/local/charm-6.9.0 \
    LD_LIBRARY_PATH=/usr/local/charm-6.9.0/lib_so:$LD_LIBRARY_PATH \
    PATH=/usr/local/charm-6.9.0/bin:$PATH''')

    @ppc64le
    @ubuntu
    @docker
    def test_ppc64le(self):
        """Default charm building block"""
        c = charm(version='6.9.0')
        self.assertEqual(str(c),
r'''# Charm++ version 6.9.0
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        autoconf \
        automake \
        git \
        libtool \
        make \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/UIUC-PPL/charm/archive/v6.9.0.tar.gz && \
    mkdir -p /usr/local && tar -x -f /var/tmp/v6.9.0.tar.gz -C /usr/local -z && \
    cd /usr/local/charm-6.9.0 && ./build charm++ multicore-linux-ppc64le --build-shared --with-production -j$(nproc) && \
    rm -rf /var/tmp/v6.9.0.tar.gz
ENV CHARMBASE=/usr/local/charm-6.9.0 \
    LD_LIBRARY_PATH=/usr/local/charm-6.9.0/lib_so:$LD_LIBRARY_PATH \
    PATH=/usr/local/charm-6.9.0/bin:$PATH''')

    @x86_64
    @ubuntu
    @docker
    def test_ldconfig(self):
        """ldconfig option"""
        c = charm(ldconfig=True, version='6.8.2')
        self.assertEqual(str(c),
r'''# Charm++ version 6.8.2
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        autoconf \
        automake \
        git \
        libtool \
        make \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/UIUC-PPL/charm/archive/v6.8.2.tar.gz && \
    mkdir -p /usr/local && tar -x -f /var/tmp/v6.8.2.tar.gz -C /usr/local -z && \
    cd /usr/local/charm-v6.8.2 && ./build charm++ multicore-linux-x86_64 --build-shared --with-production -j$(nproc) && \
    echo "/usr/local/charm-v6.8.2/lib_so" >> /etc/ld.so.conf.d/hpccm.conf && ldconfig && \
    rm -rf /var/tmp/v6.8.2.tar.gz
ENV CHARMBASE=/usr/local/charm-v6.8.2 \
    PATH=/usr/local/charm-v6.8.2/bin:$PATH''')

    @x86_64
    @ubuntu
    @docker
    def test_basedir(self):
        """basedir option"""
        c = charm(basedir=['/usr/local/openmpi'], version='6.9.0')
        self.assertEqual(str(c),
r'''# Charm++ version 6.9.0
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        autoconf \
        automake \
        git \
        libtool \
        make \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/UIUC-PPL/charm/archive/v6.9.0.tar.gz && \
    mkdir -p /usr/local && tar -x -f /var/tmp/v6.9.0.tar.gz -C /usr/local -z && \
    cd /usr/local/charm-6.9.0 && ./build charm++ multicore-linux-x86_64 --build-shared --with-production --basedir=/usr/local/openmpi -j$(nproc) && \
    rm -rf /var/tmp/v6.9.0.tar.gz
ENV CHARMBASE=/usr/local/charm-6.9.0 \
    LD_LIBRARY_PATH=/usr/local/charm-6.9.0/lib_so:$LD_LIBRARY_PATH \
    PATH=/usr/local/charm-6.9.0/bin:$PATH''')

    @x86_64
    @ubuntu
    @docker
    def test_runtime(self):
        """Runtime"""
        c = charm()
        r = c.runtime()
        self.assertEqual(r,
r'''# Charm++
COPY --from=0 /usr/local/charm-6.9.0 /usr/local/charm-6.9.0
ENV CHARMBASE=/usr/local/charm-6.9.0 \
    LD_LIBRARY_PATH=/usr/local/charm-6.9.0/lib_so:$LD_LIBRARY_PATH \
    PATH=/usr/local/charm-6.9.0/bin:$PATH''')
