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

"""Test cases for the mkl module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import centos, docker, ubuntu

from hpccm.building_blocks.mkl import mkl

class Test_mkl(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @ubuntu
    @docker
    def test_defaults(self):
        """Default mkl building block, no eula agreement"""
        with self.assertRaises(RuntimeError):
            mkl()

    @ubuntu
    @docker
    def test_basic_ubuntu(self):
        """Default mkl building block"""
        m = mkl(eula=True)
        self.assertEqual(str(m),
r'''# MKL version 2020.0-088
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        apt-transport-https \
        ca-certificates \
        gnupg \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN wget -qO - https://apt.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS-2019.PUB | apt-key add - && \
    echo "deb https://apt.repos.intel.com/mkl all main" >> /etc/apt/sources.list.d/hpccm.list && \
    apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        intel-mkl-64bit-2020.0-088 && \
    rm -rf /var/lib/apt/lists/*
RUN echo "source /opt/intel/mkl/bin/mklvars.sh intel64" >> /etc/bash.bashrc''')

    @centos
    @docker
    def test_basic_centos(self):
        """Default mkl building block"""
        m = mkl(eula=True)
        self.assertEqual(str(m),
r'''# MKL version 2020.0-088
RUN rpm --import https://yum.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS-2019.PUB && \
    yum install -y yum-utils && \
    yum-config-manager --add-repo https://yum.repos.intel.com/mkl/setup/intel-mkl.repo && \
    yum install -y \
        intel-mkl-64bit-2020.0-088 && \
    rm -rf /var/cache/yum/*
RUN echo "source /opt/intel/mkl/bin/mklvars.sh intel64" >> /etc/bashrc''')

    @ubuntu
    @docker
    def test_version(self):
        """Version option"""
        m = mkl(eula=True, version='2018.2-046')
        self.assertEqual(str(m),
r'''# MKL version 2018.2-046
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        apt-transport-https \
        ca-certificates \
        gnupg \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN wget -qO - https://apt.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS-2019.PUB | apt-key add - && \
    echo "deb https://apt.repos.intel.com/mkl all main" >> /etc/apt/sources.list.d/hpccm.list && \
    apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        intel-mkl-64bit-2018.2-046 && \
    rm -rf /var/lib/apt/lists/*
RUN echo "source /opt/intel/mkl/bin/mklvars.sh intel64" >> /etc/bash.bashrc''')

    @ubuntu
    @docker
    def test_mklvars(self):
        """mklvars is False"""
        m = mkl(eula=True, mklvars=False, version='2019.4-070')
        self.assertEqual(str(m),
r'''# MKL version 2019.4-070
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        apt-transport-https \
        ca-certificates \
        gnupg \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN wget -qO - https://apt.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS-2019.PUB | apt-key add - && \
    echo "deb https://apt.repos.intel.com/mkl all main" >> /etc/apt/sources.list.d/hpccm.list && \
    apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        intel-mkl-64bit-2019.4-070 && \
    rm -rf /var/lib/apt/lists/*
ENV CPATH=/opt/intel/mkl/include:$CPATH \
    LD_LIBRARY_PATH=/opt/intel/mkl/lib/intel64:/opt/intel/lib/intel64:$LD_LIBRARY_PATH \
    LIBRARY_PATH=/opt/intel/mkl/lib/intel64:/opt/intel/lib/intel64:$LIBRARY_PATH \
    MKLROOT=/opt/intel/mkl''')

    @ubuntu
    @docker
    def test_runtime(self):
        """Runtime"""
        m = mkl(eula=True)
        r = m.runtime()
        self.assertEqual(r,
r'''# MKL version 2020.0-088
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        apt-transport-https \
        ca-certificates \
        gnupg \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN wget -qO - https://apt.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS-2019.PUB | apt-key add - && \
    echo "deb https://apt.repos.intel.com/mkl all main" >> /etc/apt/sources.list.d/hpccm.list && \
    apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        intel-mkl-64bit-2020.0-088 && \
    rm -rf /var/lib/apt/lists/*
RUN echo "source /opt/intel/mkl/bin/mklvars.sh intel64" >> /etc/bash.bashrc''')
