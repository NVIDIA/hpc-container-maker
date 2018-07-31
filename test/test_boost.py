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

"""Test cases for the boost module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import centos, docker, ubuntu

from hpccm.building_blocks.boost import boost

class Test_boost(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @ubuntu
    @docker
    def test_defaults_ubuntu(self):
        """Default boost building block"""
        b = boost()
        self.assertEqual(str(b),
r'''# Boost version 1.67.0
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        bzip2 \
        tar \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://dl.bintray.com/boostorg/release/1.67.0/source/boost_1_67_0.tar.bz2 && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/boost_1_67_0.tar.bz2 -C /var/tmp -j && \
    cd /var/tmp/boost_1_67_0 && ./bootstrap.sh --prefix=/usr/local/boost  && \
    ./b2 -j4 install && \
    rm -rf /var/tmp/boost_1_67_0.tar.bz2 /var/tmp/boost_1_67_0
ENV LD_LIBRARY_PATH=/usr/local/boost/lib:$LD_LIBRARY_PATH''')

    @ubuntu
    @docker
    def test_runtime(self):
        """Runtime"""
        b = boost()
        r = b.runtime()
        self.assertEqual(r,
r'''# Boost
COPY --from=0 /usr/local/boost /usr/local/boost
ENV LD_LIBRARY_PATH=/usr/local/boost/lib:$LD_LIBRARY_PATH''')
