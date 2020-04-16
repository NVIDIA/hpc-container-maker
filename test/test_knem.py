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

"""Test cases for the knem module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import centos, docker, ubuntu

from hpccm.building_blocks.knem import knem

class Test_knem(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @ubuntu
    @docker
    def test_defaults_ubuntu(self):
        """Default knem building block"""
        k = knem()
        self.assertEqual(str(k),
r'''# KNEM version 1.1.3
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ca-certificates \
        git && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && cd /var/tmp && git clone --depth=1 --branch knem-1.1.3 https://gforge.inria.fr/git/knem/knem.git knem && cd - && \
    mkdir -p /usr/local/knem && \
    cd /var/tmp/knem && \
    mkdir -p /usr/local/knem/include && \
    cp common/*.h /usr/local/knem/include && \
    rm -rf /var/tmp/knem
ENV CPATH=/usr/local/knem/include:$CPATH''')

    @centos
    @docker
    def test_defaults_centos(self):
        """Default knem building block"""
        k = knem()
        self.assertEqual(str(k),
r'''# KNEM version 1.1.3
RUN yum install -y \
        ca-certificates \
        git && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp && cd /var/tmp && git clone --depth=1 --branch knem-1.1.3 https://gforge.inria.fr/git/knem/knem.git knem && cd - && \
    mkdir -p /usr/local/knem && \
    cd /var/tmp/knem && \
    mkdir -p /usr/local/knem/include && \
    cp common/*.h /usr/local/knem/include && \
    rm -rf /var/tmp/knem
ENV CPATH=/usr/local/knem/include:$CPATH''')

    @ubuntu
    @docker
    def test_runtime(self):
        """Runtime"""
        k = knem()
        r = k.runtime()
        self.assertEqual(r,
r'''# KNEM
COPY --from=0 /usr/local/knem /usr/local/knem
ENV CPATH=/usr/local/knem/include:$CPATH''')
