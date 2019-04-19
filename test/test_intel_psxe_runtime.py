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

"""Test cases for the intel_psxe_runtime module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import centos, docker, ubuntu

from hpccm.building_blocks.intel_psxe_runtime import intel_psxe_runtime

class Test_intel_psxe_runtime(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @ubuntu
    @docker
    def test_defaults(self):
        """Default intel_psxe_runtime building block, no eula agreement"""
        with self.assertRaises(RuntimeError):
            psxe_rt = intel_psxe_runtime()
            str(psxe_rt)

    @ubuntu
    @docker
    def test_defaults_eula(self):
        """eula"""
        psxe_rt = intel_psxe_runtime(eula=True)
        self.assertEqual(str(psxe_rt),
r'''# Intel Parallel Studio XE runtime version 2019
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        apt-transport-https \
        ca-certificates \
        gcc \
        gnupg \
        man-db \
        openssh-client \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN wget -qO - https://apt.repos.intel.com/2019/GPG-PUB-KEY-INTEL-PSXE-RUNTIME-2019 | apt-key add - && \
    echo "deb https://apt.repos.intel.com/2019 intel-psxe-runtime main" >> /etc/apt/sources.list.d/hpccm.list && \
    apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        intel-psxe-runtime && \
    rm -rf /var/lib/apt/lists/*
RUN echo "source /opt/intel/psxe_runtime/linux/bin/psxevars.sh intel64" >> /etc/bash.bashrc''')

    @ubuntu
    @docker
    def test_psxevars_false(self):
        """psxevars is false"""
        psxe_rt = intel_psxe_runtime(eula=True, psxevars=False)
        self.assertEqual(str(psxe_rt),
r'''# Intel Parallel Studio XE runtime version 2019
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        apt-transport-https \
        ca-certificates \
        gcc \
        gnupg \
        man-db \
        openssh-client \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN wget -qO - https://apt.repos.intel.com/2019/GPG-PUB-KEY-INTEL-PSXE-RUNTIME-2019 | apt-key add - && \
    echo "deb https://apt.repos.intel.com/2019 intel-psxe-runtime main" >> /etc/apt/sources.list.d/hpccm.list && \
    apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        intel-psxe-runtime && \
    rm -rf /var/lib/apt/lists/*
ENV DAALROOT=/opt/intel/psxe_runtime/linux/daal \
    FI_PROVIDER_PATH=/opt/intel/psxe_runtime/linux/mpi/intel64/libfabric/lib/prov \
    IPPROOT=/opt/intel/psxe_runtime/linux/ipp \
    I_MPI_ROOT=/opt/intel/psxe_runtime/linux/mpi \
    LD_LIBRARY_PATH=/opt/intel/psxe_runtime/linux/daal/lib/intel64:/opt/intel/psxe_runtime/linux/compiler/lib/intel64_lin:/opt/intel/psxe_runtime/linux/compiler/lib/intel64_lin:/opt/intel/psxe_runtime/linux/ipp/lib/intel64:/opt/intel/psxe_runtime/linux/mkl/lib/intel64:/opt/intel/psxe_runtime/linux/mpi/intel64/lib:/opt/intel/psxe_runtime/linux/mpi/intel64/libfabric/lib:/opt/intel/psxe_runtime/linux/tbb/lib/intel64/gcc4.7:$LD_LIBRARY_PATH \
    MKLROOT=/opt/intel/psxe_runtime/linux/mkl \
    PATH=/opt/intel/psxe_runtime/linux/mpi/intel64/bin:/opt/intel/psxe_runtime/linux/mpi/intel64/libfabric/bin:$PATH''')

    @centos
    @docker
    def test_component_off(self):
        """disable one of the runtimes"""
        psxe_rt = intel_psxe_runtime(daal=False, eula=True)
        self.assertEqual(str(psxe_rt),
r'''# Intel Parallel Studio XE runtime version 2019
RUN yum install -y \
        man-db \
        openssh-clients \
        which && \
    rm -rf /var/cache/yum/*
RUN rpm --import https://yum.repos.intel.com/2019/setup/RPM-GPG-KEY-intel-psxe-runtime-2019 && \
    yum-config-manager --add-repo https://yum.repos.intel.com/2019/setup/intel-psxe-runtime-2019.repo && \
    yum install -y \
        intel-icc-runtime \
        intel-ifort-runtime \
        intel-ipp-runtime \
        intel-mkl-runtime \
        intel-mpi-runtime \
        intel-tbb-runtime && \
    rm -rf /var/cache/yum/*
RUN echo "source /opt/intel/psxe_runtime/linux/bin/psxevars.sh intel64" >> /etc/bashrc''')
