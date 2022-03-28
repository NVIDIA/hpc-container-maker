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

"""Test cases for the arm_allinea_studio module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import aarch64, centos, centos8, docker, thunderx2, ubuntu20, ubuntu

from hpccm.building_blocks.arm_allinea_studio import arm_allinea_studio

class Test_arm_allinea_studio(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @aarch64
    @ubuntu20
    @docker
    def test_defaults_ubuntu(self):
        """Default arm_allinea_studio building block"""
        a = arm_allinea_studio(eula=True)
        self.assertEqual(str(a),
r'''# Arm Allinea Studio version 22.0
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libc6-dev \
        lmod \
        python \
        tar \
        tcl \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://developer.arm.com/-/media/Files/downloads/hpc/arm-allinea-studio/22-0/ACfL/arm-compiler-for-linux_22.0_Ubuntu-20.04_aarch64.tar && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/arm-compiler-for-linux_22.0_Ubuntu-20.04_aarch64.tar -C /var/tmp && \
    cd /var/tmp/arm-compiler-for-linux_22.0_Ubuntu-20.04 && ./arm-compiler-for-linux_22.0_Ubuntu-20.04.sh --install-to /opt/arm --accept && \
    rm -rf /var/tmp/arm-compiler-for-linux_22.0_Ubuntu-20.04_aarch64.tar /var/tmp/arm-compiler-for-linux_22.0_Ubuntu-20.04
ENV MODULEPATH=/opt/arm/modulefiles:$MODULEPATH''')

    @aarch64
    @centos
    @docker
    def test_defaults_centos(self):
        """Default arm_allinea_studio building block"""
        a = arm_allinea_studio(eula=True)
        self.assertEqual(str(a),
r'''# Arm Allinea Studio version 22.0
RUN yum install -y epel-release && \
    yum install -y \
        Lmod \
        glibc-devel \
        tar \
        wget && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://developer.arm.com/-/media/Files/downloads/hpc/arm-allinea-studio/22-0/ACfL/arm-compiler-for-linux_22.0_RHEL-7_aarch64.tar && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/arm-compiler-for-linux_22.0_RHEL-7_aarch64.tar -C /var/tmp && \
    cd /var/tmp/arm-compiler-for-linux_22.0_RHEL-7 && ./arm-compiler-for-linux_22.0_RHEL-7.sh --install-to /opt/arm --accept && \
    rm -rf /var/tmp/arm-compiler-for-linux_22.0_RHEL-7_aarch64.tar /var/tmp/arm-compiler-for-linux_22.0_RHEL-7
ENV MODULEPATH=/opt/arm/modulefiles:$MODULEPATH''')

    @aarch64
    @centos8
    @docker
    def test_thunderx2_centos8(self):
        """Default arm_allinea_studio building block"""
        a = arm_allinea_studio(eula=True, version='20.3',
                               microarchitectures=['generic', 'thunderx2t99'])
        self.assertEqual(str(a),
r'''# Arm Allinea Studio version 20.3
RUN yum install -y epel-release && \
    yum install -y \
        Lmod \
        glibc-devel \
        tar \
        wget && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://developer.arm.com/-/media/Files/downloads/hpc/arm-allinea-studio/20-3/RHEL8/arm-compiler-for-linux_20.3_RHEL-8_aarch64.tar && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/arm-compiler-for-linux_20.3_RHEL-8_aarch64.tar -C /var/tmp && \
    cd /var/tmp/arm-compiler-for-linux_20.3_RHEL-8_aarch64 && ./arm-compiler-for-linux_20.3_RHEL-8.sh --install-to /opt/arm --accept --only-install-microarchitectures=generic,thunderx2t99 && \
    rm -rf /var/tmp/arm-compiler-for-linux_20.3_RHEL-8_aarch64.tar /var/tmp/arm-compiler-for-linux_20.3_RHEL-8_aarch64
ENV MODULEPATH=/opt/arm/modulefiles:$MODULEPATH''')

    @aarch64
    @ubuntu
    @docker
    def test_eula(self):
        """Decline EULA"""
        with self.assertRaises(RuntimeError):
            a = arm_allinea_studio(eula=False)
            str(a)

    @aarch64
    @ubuntu
    @docker
    def test_tarball(self):
        """tarball"""
        a = arm_allinea_studio(eula=True,
                               tarball='arm-compiler-for-linux_22.0_Ubuntu-18.04_aarch64.tar')
        self.assertEqual(str(a),
r'''# Arm Allinea Studio version 22.0
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libc6-dev \
        lmod \
        python \
        tar \
        tcl \
        wget && \
    rm -rf /var/lib/apt/lists/*
COPY arm-compiler-for-linux_22.0_Ubuntu-18.04_aarch64.tar /var/tmp
RUN mkdir -p /var/tmp && tar -x -f /var/tmp/arm-compiler-for-linux_22.0_Ubuntu-18.04_aarch64.tar -C /var/tmp && \
    cd /var/tmp/arm-compiler-for-linux_22.0_Ubuntu-18.04 && ./arm-compiler-for-linux_22.0_Ubuntu-18.04.sh --install-to /opt/arm --accept && \
    rm -rf /var/tmp/arm-compiler-for-linux_22.0_Ubuntu-18.04_aarch64.tar /var/tmp/arm-compiler-for-linux_22.0_Ubuntu-18.04
ENV MODULEPATH=/opt/arm/modulefiles:$MODULEPATH''')

    @aarch64
    @centos
    @docker
    def test_runtime_centos(self):
        """Runtime"""
        a = arm_allinea_studio(eula=True)
        r = a.runtime()
        self.assertEqual(r,
r'''# Arm Allinea Studio
COPY --from=0 /opt/arm/arm-linux-compiler-22.0_Generic-AArch64_RHEL-7_aarch64-linux/lib/libgomp.so \
    /opt/arm/arm-linux-compiler-22.0_Generic-AArch64_RHEL-7_aarch64-linux/lib/libiomp5.so \
    /opt/arm/arm-linux-compiler-22.0_Generic-AArch64_RHEL-7_aarch64-linux/lib/libomp.so \
    /opt/arm/arm-linux-compiler-22.0_Generic-AArch64_RHEL-7_aarch64-linux/lib/libflang.so \
    /opt/arm/arm-linux-compiler-22.0_Generic-AArch64_RHEL-7_aarch64-linux/lib/libflangrti.so \
    /opt/arm/arm-linux-compiler-22.0_Generic-AArch64_RHEL-7_aarch64-linux/lib/
COPY --from=0 /opt/arm/armpl-22.0.0_AArch64_RHEL-7_arm-linux-compiler_aarch64-linux/lib/libamath.so \
    /opt/arm/armpl-22.0.0_AArch64_RHEL-7_arm-linux-compiler_aarch64-linux/lib/libastring.so \
    /opt/arm/armpl-22.0.0_AArch64_RHEL-7_arm-linux-compiler_aarch64-linux/lib/
COPY --from=0 /opt/arm/armpl-22.0.0_AArch64_RHEL-7_gcc_aarch64-linux/lib/libamath.so \
    /opt/arm/armpl-22.0.0_AArch64_RHEL-7_gcc_aarch64-linux/lib/libastring.so \
    /opt/arm/armpl-22.0.0_AArch64_RHEL-7_gcc_aarch64-linux/lib/
ENV LD_LIBRARY_PATH=/opt/arm/arm-linux-compiler-22.0_Generic-AArch64_RHEL-7_aarch64-linux/lib:/opt/arm/armpl-22.0.0_AArch64_RHEL-7_arm-linux-compiler_aarch64-linux/lib:/opt/arm/armpl-22.0.0_AArch64_RHEL-7_gcc_aarch64-linux/lib:$LD_LIBRARY_PATH''')

    def test_toolchain(self):
        """Toolchain"""
        a = arm_allinea_studio(eula=True)
        tc = a.toolchain
        self.assertEqual(tc.CC, 'armclang')
        self.assertEqual(tc.CXX, 'armclang++')
        self.assertEqual(tc.FC, 'armflang')
        self.assertEqual(tc.F77, 'armflang')
        self.assertEqual(tc.F90, 'armflang')

    @thunderx2
    def test_toolchain_thunderx2(self):
        """CPU target optimization flags"""
        a = arm_allinea_studio(eula=True)
        tc = a.toolchain
        self.assertEqual(tc.CFLAGS, '-mcpu=thunderx2t99')
        self.assertEqual(tc.CXXFLAGS, '-mcpu=thunderx2t99')
