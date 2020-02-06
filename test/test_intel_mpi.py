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

"""Test cases for the intel_mpi module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import centos, docker, ubuntu

from hpccm.building_blocks.intel_mpi import intel_mpi

class Test_intel_mpi(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @ubuntu
    @docker
    def test_defaults(self):
        """Default intel_mpi building block, no eula agreement"""
        with self.assertRaises(RuntimeError):
            intel_mpi()

    @ubuntu
    @docker
    def test_basic_ubuntu(self):
        """Default intel_mpi building block"""
        impi = intel_mpi(eula=True)
        self.assertEqual(str(impi),
r'''# Intel MPI version 2019.6-088
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        apt-transport-https \
        ca-certificates \
        gnupg \
        man-db \
        openssh-client \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN wget -qO - https://apt.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS-2019.PUB | apt-key add - && \
    echo "deb https://apt.repos.intel.com/mpi all main" >> /etc/apt/sources.list.d/hpccm.list && \
    apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        intel-mpi-2019.6-088 && \
    rm -rf /var/lib/apt/lists/*
RUN echo "source /opt/intel/compilers_and_libraries/linux/mpi/intel64/bin/mpivars.sh intel64" >> /etc/bash.bashrc''')

    @centos
    @docker
    def test_basic_centos(self):
        """Default intel_mpi building block"""
        impi = intel_mpi(eula=True)
        self.assertEqual(str(impi),
r'''# Intel MPI version 2019.6-088
RUN yum install -y \
        man-db \
        openssh-clients && \
    rm -rf /var/cache/yum/*
RUN rpm --import https://yum.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS-2019.PUB && \
    yum install -y yum-utils && \
    yum-config-manager --add-repo https://yum.repos.intel.com/mpi/setup/intel-mpi.repo && \
    yum install -y \
        intel-mpi-2019.6-088 && \
    rm -rf /var/cache/yum/*
RUN echo "source /opt/intel/compilers_and_libraries/linux/mpi/intel64/bin/mpivars.sh intel64" >> /etc/bashrc''')

    @ubuntu
    @docker
    def test_version(self):
        """Version option"""
        impi = intel_mpi(eula=True, version='2018.2-046')
        self.assertEqual(str(impi),
r'''# Intel MPI version 2018.2-046
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        apt-transport-https \
        ca-certificates \
        gnupg \
        man-db \
        openssh-client \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN wget -qO - https://apt.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS-2019.PUB | apt-key add - && \
    echo "deb https://apt.repos.intel.com/mpi all main" >> /etc/apt/sources.list.d/hpccm.list && \
    apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        intel-mpi-2018.2-046 && \
    rm -rf /var/lib/apt/lists/*
RUN echo "source /opt/intel/compilers_and_libraries/linux/mpi/intel64/bin/mpivars.sh intel64" >> /etc/bash.bashrc''')

    @ubuntu
    @docker
    def test_mpivars(self):
        """mpivars is False"""
        impi = intel_mpi(eula=True, mpivars=False)
        self.assertEqual(str(impi),
r'''# Intel MPI version 2019.6-088
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        apt-transport-https \
        ca-certificates \
        gnupg \
        man-db \
        openssh-client \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN wget -qO - https://apt.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS-2019.PUB | apt-key add - && \
    echo "deb https://apt.repos.intel.com/mpi all main" >> /etc/apt/sources.list.d/hpccm.list && \
    apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        intel-mpi-2019.6-088 && \
    rm -rf /var/lib/apt/lists/*
ENV FI_PROVIDER_PATH=/opt/intel/compilers_and_libraries/linux/mpi/intel64/libfabric/lib/prov \
    I_MPI_ROOT=/opt/intel/compilers_and_libraries/linux/mpi \
    LD_LIBRARY_PATH=/opt/intel/compilers_and_libraries/linux/mpi/intel64/lib:/opt/intel/compilers_and_libraries/linux/mpi/intel64/libfabric/lib:$LD_LIBRARY_PATH \
    PATH=/opt/intel/compilers_and_libraries/linux/mpi/intel64/bin:/opt/intel/compilers_and_libraries/linux/mpi/intel64/libfabric/bin:$PATH''')

    @ubuntu
    @docker
    def test_runtime(self):
        """Runtime"""
        impi = intel_mpi(eula=True)
        r = impi.runtime()
        self.assertEqual(r,
r'''# Intel MPI version 2019.6-088
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        apt-transport-https \
        ca-certificates \
        gnupg \
        man-db \
        openssh-client \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN wget -qO - https://apt.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS-2019.PUB | apt-key add - && \
    echo "deb https://apt.repos.intel.com/mpi all main" >> /etc/apt/sources.list.d/hpccm.list && \
    apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        intel-mpi-2019.6-088 && \
    rm -rf /var/lib/apt/lists/*
RUN echo "source /opt/intel/compilers_and_libraries/linux/mpi/intel64/bin/mpivars.sh intel64" >> /etc/bash.bashrc''')
