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
        k = kokkos(url='https://github.com/kokkos/kokkos/archive/master.tar.gz')
        self.assertEqual(str(k),
r'''# https://github.com/kokkos/kokkos/archive/master.tar.gz
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/kokkos/kokkos/archive/master.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/master.tar.gz -C /var/tmp -z && \
    mkdir -p /var/tmp/master/build && cd /var/tmp/master/build && cmake -DCMAKE_INSTALL_PREFIX=/usr/local /var/tmp/master && \
    cmake --build /var/tmp/master/build --target all -- -j$(nproc) && \
    cmake --build /var/tmp/master/build --target install -- -j$(nproc) && \
    rm -rf /var/tmp/master /var/tmp/master.tar.gz''')

    @centos
    @docker
    def test_defaults_centos(self):
        """Default kokkos building block"""
        k = kokkos(url='https://github.com/kokkos/kokkos/archive/master.tar.gz')
        self.assertEqual(str(k),
r'''# https://github.com/kokkos/kokkos/archive/master.tar.gz
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/kokkos/kokkos/archive/master.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/master.tar.gz -C /var/tmp -z && \
    mkdir -p /var/tmp/master/build && cd /var/tmp/master/build && cmake -DCMAKE_INSTALL_PREFIX=/usr/local /var/tmp/master && \
    cmake --build /var/tmp/master/build --target all -- -j$(nproc) && \
    cmake --build /var/tmp/master/build --target install -- -j$(nproc) && \
    rm -rf /var/tmp/master /var/tmp/master.tar.gz''')

    @centos8
    @docker
    def test_defaults_centos8(self):
        """Default kokkos building block"""
        k = kokkos(url='https://github.com/kokkos/kokkos/archive/master.tar.gz')
        self.assertEqual(str(k),
r'''# https://github.com/kokkos/kokkos/archive/master.tar.gz
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/kokkos/kokkos/archive/master.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/master.tar.gz -C /var/tmp -z && \
    mkdir -p /var/tmp/master/build && cd /var/tmp/master/build && cmake -DCMAKE_INSTALL_PREFIX=/usr/local /var/tmp/master && \
    cmake --build /var/tmp/master/build --target all -- -j$(nproc) && \
    cmake --build /var/tmp/master/build --target install -- -j$(nproc) && \
    rm -rf /var/tmp/master /var/tmp/master.tar.gz''')

    @ubuntu
    @docker
    def test_runtime(self):
        """Runtime"""
        k = kokkos(url='https://github.com/kokkos/kokkos/archive/master.tar.gz')
        r = k.runtime()
        self.assertEqual(r,
r'''# https://github.com/kokkos/kokkos/archive/master.tar.gz
COPY --from=0 /usr/local /usr/local
ENV PATH=/usr/local/bin:$PATH''')
