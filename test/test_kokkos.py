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

"""Test cases for the kokkos module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import centos, centos8, docker, ubuntu

from hpccm.building_blocks.kokkos import kokkos

class Test_kokkos(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @ubuntu
    @docker
    def test_defaults_ubuntu(self):
        """Default kokkos building block"""
        k = kokkos()
        self.assertEqual(str(k),
r'''# Kokkos version 2.9.00
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        bc \
        gzip \
        libhwloc-dev \
        make \
        tar \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/kokkos/kokkos/archive/2.9.00.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/2.9.00.tar.gz -C /var/tmp -z && \
    mkdir -p /var/tmp/kokkos-2.9.00/build && cd /var/tmp/kokkos-2.9.00/build && \
    /var/tmp/kokkos-2.9.00/generate_makefile.bash --arch=Pascal60 --with-cuda --with-hwloc --prefix=/usr/local/kokkos && \
    make kokkoslib -j$(nproc) && \
    make install -j$(nproc) && \
    rm -rf /var/tmp/2.9.00.tar.gz /var/tmp/kokkos-2.9.00
ENV PATH=/usr/local/kokkos/bin:$PATH''')

    @centos
    @docker
    def test_defaults_centos(self):
        """Default kokkos building block"""
        k = kokkos()
        self.assertEqual(str(k),
r'''# Kokkos version 2.9.00
RUN yum install -y \
        bc \
        gzip \
        hwloc-devel \
        make \
        tar \
        wget \
        which && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/kokkos/kokkos/archive/2.9.00.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/2.9.00.tar.gz -C /var/tmp -z && \
    mkdir -p /var/tmp/kokkos-2.9.00/build && cd /var/tmp/kokkos-2.9.00/build && \
    /var/tmp/kokkos-2.9.00/generate_makefile.bash --arch=Pascal60 --with-cuda --with-hwloc --prefix=/usr/local/kokkos && \
    make kokkoslib -j$(nproc) && \
    make install -j$(nproc) && \
    rm -rf /var/tmp/2.9.00.tar.gz /var/tmp/kokkos-2.9.00
ENV PATH=/usr/local/kokkos/bin:$PATH''')

    @centos8
    @docker
    def test_defaults_centos8(self):
        """Default kokkos building block"""
        k = kokkos()
        self.assertEqual(str(k),
r'''# Kokkos version 2.9.00
RUN yum install -y dnf-utils && \
    yum-config-manager --set-enabled PowerTools && \
    yum install -y \
        bc \
        gzip \
        hwloc-devel \
        make \
        tar \
        wget \
        which && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/kokkos/kokkos/archive/2.9.00.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/2.9.00.tar.gz -C /var/tmp -z && \
    mkdir -p /var/tmp/kokkos-2.9.00/build && cd /var/tmp/kokkos-2.9.00/build && \
    /var/tmp/kokkos-2.9.00/generate_makefile.bash --arch=Pascal60 --with-cuda --with-hwloc --prefix=/usr/local/kokkos && \
    make kokkoslib -j$(nproc) && \
    make install -j$(nproc) && \
    rm -rf /var/tmp/2.9.00.tar.gz /var/tmp/kokkos-2.9.00
ENV PATH=/usr/local/kokkos/bin:$PATH''')

    @ubuntu
    @docker
    def test_runtime(self):
        """Runtime"""
        k = kokkos()
        r = k.runtime()
        self.assertEqual(r,
r'''# Kokkos
COPY --from=0 /usr/local/kokkos /usr/local/kokkos
ENV PATH=/usr/local/kokkos/bin:$PATH''')
