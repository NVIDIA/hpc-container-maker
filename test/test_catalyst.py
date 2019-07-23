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

"""Test cases for the catalyst module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import centos, docker, ubuntu

from hpccm.building_blocks.catalyst import catalyst
from hpccm.toolchain import toolchain

class Test_catalyst(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @ubuntu
    @docker
    def test_defaults_ubuntu(self):
        """Default catalyst building block"""
        c = catalyst()
        self.assertEqual(str(c),
r'''# ParaView Catalyst version 5.6.1
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        git \
        gzip \
        libgl1-mesa-dev \
        libice-dev \
        libsm-dev \
        libx11-dev \
        libxau-dev \
        libxext-dev \
        libxt-dev \
        make \
        tar \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -O /var/tmp/Catalyst-v5.6.1-Base-Enable-Python-Essentials-Extras-Rendering-Base.tar.gz -P /var/tmp https://www.paraview.org/paraview-downloads/download.php?submit=Download\&version=v5.6\&type=catalyst\&os=Sources\&downloadFile=Catalyst-v5.6.1-Base-Enable-Python-Essentials-Extras-Rendering-Base.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/Catalyst-v5.6.1-Base-Enable-Python-Essentials-Extras-Rendering-Base.tar.gz -C /var/tmp -z && \
    mkdir -p /var/tmp/Catalyst-v5.6.1-Base-Enable-Python-Essentials-Extras-Rendering-Base/build && cd /var/tmp/Catalyst-v5.6.1-Base-Enable-Python-Essentials-Extras-Rendering-Base/build && /var/tmp/Catalyst-v5.6.1-Base-Enable-Python-Essentials-Extras-Rendering-Base/cmake.sh -DCMAKE_INSTALL_PREFIX=/usr/local/catalyst /var/tmp/Catalyst-v5.6.1-Base-Enable-Python-Essentials-Extras-Rendering-Base && \
    cmake --build /var/tmp/Catalyst-v5.6.1-Base-Enable-Python-Essentials-Extras-Rendering-Base/build --target all -- -j$(nproc) && \
    cmake --build /var/tmp/Catalyst-v5.6.1-Base-Enable-Python-Essentials-Extras-Rendering-Base/build --target install -- -j$(nproc) && \
    rm -rf /var/tmp/Catalyst-v5.6.1-Base-Enable-Python-Essentials-Extras-Rendering-Base.tar.gz /var/tmp/Catalyst-v5.6.1-Base-Enable-Python-Essentials-Extras-Rendering-Base
ENV LD_LIBRARY_PATH=/usr/local/catalyst/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/catalyst/bin:$PATH''')

    @centos
    @docker
    def test_defaults_centos(self):
        """Default catalyst building block"""
        c = catalyst()
        self.assertEqual(str(c),
r'''# ParaView Catalyst version 5.6.1
RUN yum install -y \
        git \
        gzip \
        libICE-devel \
        libSM-devel \
        libX11-devel \
        libXau-devel \
        libXext-devel \
        libXt-devel \
        libglvnd-devel \
        make \
        mesa-libGL-devel \
        tar \
        wget \
        which && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -O /var/tmp/Catalyst-v5.6.1-Base-Enable-Python-Essentials-Extras-Rendering-Base.tar.gz -P /var/tmp https://www.paraview.org/paraview-downloads/download.php?submit=Download\&version=v5.6\&type=catalyst\&os=Sources\&downloadFile=Catalyst-v5.6.1-Base-Enable-Python-Essentials-Extras-Rendering-Base.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/Catalyst-v5.6.1-Base-Enable-Python-Essentials-Extras-Rendering-Base.tar.gz -C /var/tmp -z && \
    mkdir -p /var/tmp/Catalyst-v5.6.1-Base-Enable-Python-Essentials-Extras-Rendering-Base/build && cd /var/tmp/Catalyst-v5.6.1-Base-Enable-Python-Essentials-Extras-Rendering-Base/build && /var/tmp/Catalyst-v5.6.1-Base-Enable-Python-Essentials-Extras-Rendering-Base/cmake.sh -DCMAKE_INSTALL_PREFIX=/usr/local/catalyst /var/tmp/Catalyst-v5.6.1-Base-Enable-Python-Essentials-Extras-Rendering-Base && \
    cmake --build /var/tmp/Catalyst-v5.6.1-Base-Enable-Python-Essentials-Extras-Rendering-Base/build --target all -- -j$(nproc) && \
    cmake --build /var/tmp/Catalyst-v5.6.1-Base-Enable-Python-Essentials-Extras-Rendering-Base/build --target install -- -j$(nproc) && \
    rm -rf /var/tmp/Catalyst-v5.6.1-Base-Enable-Python-Essentials-Extras-Rendering-Base.tar.gz /var/tmp/Catalyst-v5.6.1-Base-Enable-Python-Essentials-Extras-Rendering-Base
ENV LD_LIBRARY_PATH=/usr/local/catalyst/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/catalyst/bin:$PATH''')

    @ubuntu
    @docker
    def test_edition(self):
        """edition option"""
        c = catalyst(edition='Base-Essentials')
        self.assertEqual(str(c),
r'''# ParaView Catalyst version 5.6.1
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        git \
        gzip \
        make \
        tar \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -O /var/tmp/Catalyst-v5.6.1-Base-Essentials.tar.gz -P /var/tmp https://www.paraview.org/paraview-downloads/download.php?submit=Download\&version=v5.6\&type=catalyst\&os=Sources\&downloadFile=Catalyst-v5.6.1-Base-Essentials.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/Catalyst-v5.6.1-Base-Essentials.tar.gz -C /var/tmp -z && \
    mkdir -p /var/tmp/Catalyst-v5.6.1-Base-Essentials/build && cd /var/tmp/Catalyst-v5.6.1-Base-Essentials/build && /var/tmp/Catalyst-v5.6.1-Base-Essentials/cmake.sh -DCMAKE_INSTALL_PREFIX=/usr/local/catalyst /var/tmp/Catalyst-v5.6.1-Base-Essentials && \
    cmake --build /var/tmp/Catalyst-v5.6.1-Base-Essentials/build --target all -- -j$(nproc) && \
    cmake --build /var/tmp/Catalyst-v5.6.1-Base-Essentials/build --target install -- -j$(nproc) && \
    rm -rf /var/tmp/Catalyst-v5.6.1-Base-Essentials.tar.gz /var/tmp/Catalyst-v5.6.1-Base-Essentials
ENV LD_LIBRARY_PATH=/usr/local/catalyst/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/catalyst/bin:$PATH''')

    @ubuntu
    @docker
    def test_ldconfig(self):
        """ldconfig option"""
        c = catalyst(ldconfig=True, version='5.6.0')
        self.assertEqual(str(c),
r'''# ParaView Catalyst version 5.6.0
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        git \
        gzip \
        libgl1-mesa-dev \
        libice-dev \
        libsm-dev \
        libx11-dev \
        libxau-dev \
        libxext-dev \
        libxt-dev \
        make \
        tar \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -O /var/tmp/Catalyst-v5.6.0-Base-Enable-Python-Essentials-Extras-Rendering-Base.tar.gz -P /var/tmp https://www.paraview.org/paraview-downloads/download.php?submit=Download\&version=v5.6\&type=catalyst\&os=Sources\&downloadFile=Catalyst-v5.6.0-Base-Enable-Python-Essentials-Extras-Rendering-Base.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/Catalyst-v5.6.0-Base-Enable-Python-Essentials-Extras-Rendering-Base.tar.gz -C /var/tmp -z && \
    mkdir -p /var/tmp/Catalyst-v5.6.0-Base-Enable-Python-Essentials-Extras-Rendering-Base/build && cd /var/tmp/Catalyst-v5.6.0-Base-Enable-Python-Essentials-Extras-Rendering-Base/build && /var/tmp/Catalyst-v5.6.0-Base-Enable-Python-Essentials-Extras-Rendering-Base/cmake.sh -DCMAKE_INSTALL_PREFIX=/usr/local/catalyst /var/tmp/Catalyst-v5.6.0-Base-Enable-Python-Essentials-Extras-Rendering-Base && \
    cmake --build /var/tmp/Catalyst-v5.6.0-Base-Enable-Python-Essentials-Extras-Rendering-Base/build --target all -- -j$(nproc) && \
    cmake --build /var/tmp/Catalyst-v5.6.0-Base-Enable-Python-Essentials-Extras-Rendering-Base/build --target install -- -j$(nproc) && \
    echo "/usr/local/catalyst/lib" >> /etc/ld.so.conf.d/hpccm.conf && ldconfig && \
    rm -rf /var/tmp/Catalyst-v5.6.0-Base-Enable-Python-Essentials-Extras-Rendering-Base.tar.gz /var/tmp/Catalyst-v5.6.0-Base-Enable-Python-Essentials-Extras-Rendering-Base
ENV PATH=/usr/local/catalyst/bin:$PATH''')

    @ubuntu
    @docker
    def test_runtime(self):
        """Runtime"""
        c = catalyst()
        r = c.runtime()
        self.assertEqual(r,
r'''# ParaView Catalyst
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libgl1-mesa-glx \
        libice6 \
        libsm6 \
        libx11-6 \
        libxau6 \
        libxext6 \
        libxt6 && \
    rm -rf /var/lib/apt/lists/*
COPY --from=0 /usr/local/catalyst /usr/local/catalyst
ENV LD_LIBRARY_PATH=/usr/local/catalyst/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/catalyst/bin:$PATH''')
