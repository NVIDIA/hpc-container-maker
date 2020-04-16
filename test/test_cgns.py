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

"""Test cases for the cgns module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import centos, docker, ubuntu

from hpccm.building_blocks.cgns import cgns

class Test_cgns(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @ubuntu
    @docker
    def test_defaults_ubuntu(self):
        """Default cgns building block"""
        c = cgns()
        self.assertEqual(str(c),
r'''# CGNS version 3.4.0
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        file \
        make \
        wget \
        zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/CGNS/CGNS/archive/v3.4.0.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/v3.4.0.tar.gz -C /var/tmp -z && \
    cd /var/tmp/CGNS-3.4.0/src &&  FLIBS='-Wl,--no-as-needed -ldl' LIBS='-Wl,--no-as-needed -ldl' ./configure --prefix=/usr/local/cgns --with-hdf5=/usr/local/hdf5 --with-zlib && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/CGNS-3.4.0/src /var/tmp/v3.4.0.tar.gz''')

    @centos
    @docker
    def test_defaults_centos(self):
        """Default cgns building block"""
        c = cgns()
        self.assertEqual(str(c),
r'''# CGNS version 3.4.0
RUN yum install -y \
        bzip2 \
        file \
        make \
        wget \
        zlib-devel && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/CGNS/CGNS/archive/v3.4.0.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/v3.4.0.tar.gz -C /var/tmp -z && \
    cd /var/tmp/CGNS-3.4.0/src &&  FLIBS='-Wl,--no-as-needed -ldl' LIBS='-Wl,--no-as-needed -ldl' ./configure --prefix=/usr/local/cgns --with-hdf5=/usr/local/hdf5 --with-zlib && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/CGNS-3.4.0/src /var/tmp/v3.4.0.tar.gz''')

    @ubuntu
    @docker
    def test_runtime(self):
        """Runtime"""
        c = cgns()
        r = c.runtime()
        self.assertEqual(r,
r'''# CGNS
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        zlib1g && \
    rm -rf /var/lib/apt/lists/*
COPY --from=0 /usr/local/cgns /usr/local/cgns''')
