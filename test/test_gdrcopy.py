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

"""Test cases for the gdrcopy module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import centos, docker, ubuntu

from hpccm.building_blocks.gdrcopy import gdrcopy

class Test_gdrcopy(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @ubuntu
    @docker
    def test_defaults_ubuntu(self):
        """Default gdrcopy building block"""
        g = gdrcopy()
        self.assertEqual(str(g),
r'''# GDRCOPY version 2.0
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        make \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/NVIDIA/gdrcopy/archive/v2.0.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/v2.0.tar.gz -C /var/tmp -z && \
    cd /var/tmp/gdrcopy-2.0 && \
    mkdir -p /usr/local/gdrcopy/include /usr/local/gdrcopy/lib64 && \
    make PREFIX=/usr/local/gdrcopy lib lib_install && \
    rm -rf /var/tmp/gdrcopy-2.0 /var/tmp/v2.0.tar.gz
ENV CPATH=/usr/local/gdrcopy/include:$CPATH \
    LD_LIBRARY_PATH=/usr/local/gdrcopy/lib64:$LD_LIBRARY_PATH \
    LIBRARY_PATH=/usr/local/gdrcopy/lib64:$LIBRARY_PATH''')

    @centos
    @docker
    def test_defaults_centos(self):
        """Default gdrcopy building block"""
        g = gdrcopy()
        self.assertEqual(str(g),
r'''# GDRCOPY version 2.0
RUN yum install -y \
        make \
        wget && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/NVIDIA/gdrcopy/archive/v2.0.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/v2.0.tar.gz -C /var/tmp -z && \
    cd /var/tmp/gdrcopy-2.0 && \
    mkdir -p /usr/local/gdrcopy/include /usr/local/gdrcopy/lib64 && \
    make PREFIX=/usr/local/gdrcopy lib lib_install && \
    rm -rf /var/tmp/gdrcopy-2.0 /var/tmp/v2.0.tar.gz
ENV CPATH=/usr/local/gdrcopy/include:$CPATH \
    LD_LIBRARY_PATH=/usr/local/gdrcopy/lib64:$LD_LIBRARY_PATH \
    LIBRARY_PATH=/usr/local/gdrcopy/lib64:$LIBRARY_PATH''')

    @ubuntu
    @docker
    def test_ldconfig(self):
        """ldconfig option"""
        g = gdrcopy(ldconfig=True, version='1.3')
        self.assertEqual(str(g),
r'''# GDRCOPY version 1.3
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        make \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/NVIDIA/gdrcopy/archive/v1.3.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/v1.3.tar.gz -C /var/tmp -z && \
    cd /var/tmp/gdrcopy-1.3 && \
    mkdir -p /usr/local/gdrcopy/include /usr/local/gdrcopy/lib64 && \
    make PREFIX=/usr/local/gdrcopy lib lib_install && \
    echo "/usr/local/gdrcopy/lib64" >> /etc/ld.so.conf.d/hpccm.conf && ldconfig && \
    rm -rf /var/tmp/gdrcopy-1.3 /var/tmp/v1.3.tar.gz
ENV CPATH=/usr/local/gdrcopy/include:$CPATH \
    LIBRARY_PATH=/usr/local/gdrcopy/lib64:$LIBRARY_PATH''')

    @ubuntu
    @docker
    def test_runtime(self):
        """Runtime"""
        g = gdrcopy()
        r = g.runtime()
        self.assertEqual(r,
r'''# GDRCOPY
COPY --from=0 /usr/local/gdrcopy /usr/local/gdrcopy
ENV CPATH=/usr/local/gdrcopy/include:$CPATH \
    LD_LIBRARY_PATH=/usr/local/gdrcopy/lib64:$LD_LIBRARY_PATH \
    LIBRARY_PATH=/usr/local/gdrcopy/lib64:$LIBRARY_PATH''')
