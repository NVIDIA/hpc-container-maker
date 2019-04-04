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

"""Test cases for the sensei module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import centos, docker, ubuntu

from hpccm.building_blocks.sensei import sensei
from hpccm.toolchain import toolchain

class Test_sensei(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @ubuntu
    @docker
    def test_defaults_ubuntu(self):
        """Default sensei building block"""
        s = sensei(libsim='/usr/local/visit', vtk='/usr/local/visit/third-party/vtk/6.1.0/linux-x86_64_gcc-5.4/lib/cmake/vtk-6.1')
        self.assertEqual(str(s),
r'''# SENSEI version v2.1.1
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ca-certificates \
        git \
        make && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && cd /var/tmp && git clone --depth=1 --branch v2.1.1 https://gitlab.kitware.com/sensei/sensei.git sensei && cd - && \
    mkdir -p /var/tmp/sensei/build && cd /var/tmp/sensei/build && cmake -DCMAKE_INSTALL_PREFIX=/usr/local/sensei -DENABLE_SENSEI=ON -DENABLE_LIBSIM=ON -DLIBSIM_DIR=/usr/local/visit -DENABLE_PARALLEL3D=OFF -DENABLE_OSCILLATORS=OFF -DVTK_DIR=/usr/local/visit/third-party/vtk/6.1.0/linux-x86_64_gcc-5.4/lib/cmake/vtk-6.1 /var/tmp/sensei && \
    cmake --build /var/tmp/sensei/build --target all -- -j$(nproc) && \
    cmake --build /var/tmp/sensei/build --target install -- -j$(nproc) && \
    rm -rf /var/tmp/sensei''')

    @centos
    @docker
    def test_defaults_centos(self):
        """Default sensei building block"""
        s = sensei(catalyst='/usr/local/catalyst')
        self.assertEqual(str(s),
r'''# SENSEI version v2.1.1
RUN yum install -y \
        ca-certificates \
        git \
        make && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp && cd /var/tmp && git clone --depth=1 --branch v2.1.1 https://gitlab.kitware.com/sensei/sensei.git sensei && cd - && \
    mkdir -p /var/tmp/sensei/build && cd /var/tmp/sensei/build && cmake -DCMAKE_INSTALL_PREFIX=/usr/local/sensei -DENABLE_SENSEI=ON -DENABLE_CATALYST=ON -DParaView_DIR=/usr/local/catalyst -DENABLE_PARALLEL3D=OFF -DENABLE_OSCILLATORS=OFF /var/tmp/sensei && \
    cmake --build /var/tmp/sensei/build --target all -- -j$(nproc) && \
    cmake --build /var/tmp/sensei/build --target install -- -j$(nproc) && \
    rm -rf /var/tmp/sensei''')

    @ubuntu
    @docker
    def test_runtime(self):
        """Runtime"""
        s = sensei()
        r = s.runtime()
        self.assertEqual(r,
r'''# SENSEI
COPY --from=0 /usr/local/sensei /usr/local/sensei''')
