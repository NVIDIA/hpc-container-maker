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

from helpers import aarch64, centos, docker, ubuntu

from hpccm.building_blocks.arm_allinea_studio import arm_allinea_studio

class Test_arm_allinea_studio(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @aarch64
    @ubuntu
    @docker
    def test_defaults_ubuntu(self):
        """Default arm_allinea_studio building block"""
        a = arm_allinea_studio(eula=True)
        self.assertEqual(str(a),
r'''# Arm Allinea Studio version 19.3
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libc6-dev \
        python \
        tar \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://developer.arm.com/-/media/Files/downloads/hpc/arm-allinea-studio/19-3/Ubuntu16.04/Arm-Compiler-for-HPC_19.3_Ubuntu_16.04_aarch64.tar && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/Arm-Compiler-for-HPC_19.3_Ubuntu_16.04_aarch64.tar -C /var/tmp && \
    cd /var/tmp/ARM-Compiler-for-HPC_19.3_AArch64_Ubuntu_16.04_aarch64 && ./arm-compiler-for-hpc-19.3_Generic-AArch64_Ubuntu-16.04_aarch64-linux-deb.sh --install-to /opt/arm --accept && \
    find /opt/arm -maxdepth 1 -type d -name "armpl-*" -not -name "*Generic-AArch64*" -print0 | xargs -0 rm -rf && \
    rm -rf /var/tmp/Arm-Compiler-for-HPC_19.3_Ubuntu_16.04_aarch64.tar /var/tmp/ARM-Compiler-for-HPC_19.3_AArch64_Ubuntu_16.04_aarch64
ENV COMPILER_PATH=/opt/arm/gcc-8.2.0_Generic-AArch64_Ubuntu-16.04_aarch64-linux:$COMPILER_PATH \
    CPATH=/opt/arm/gcc-8.2.0_Generic-AArch64_Ubuntu-16.04_aarch64-linux/include:/opt/arm/arm-hpc-compiler-19.3_Generic-AArch64_Ubuntu-16.04_aarch64-linux/include:$CPATH \
    LD_LIBRARY_PATH=/opt/arm/gcc-8.2.0_Generic-AArch64_Ubuntu-16.04_aarch64-linux/lib:/opt/arm/gcc-8.2.0_Generic-AArch64_Ubuntu-16.04_aarch64-linux/lib64:/opt/arm/arm-hpc-compiler-19.3_Generic-AArch64_Ubuntu-16.04_aarch64-linux/lib:$LD_LIBRARY_PATH \
    LIBRARY_PATH=/opt/arm/gcc-8.2.0_Generic-AArch64_Ubuntu-16.04_aarch64-linux/lib:/opt/arm/gcc-8.2.0_Generic-AArch64_Ubuntu-16.04_aarch64-linux/lib64:/opt/arm/arm-hpc-compiler-19.3_Generic-AArch64_Ubuntu-16.04_aarch64-linux/lib:$LIBRARY_PATH \
    PATH=/opt/arm/gcc-8.2.0_Generic-AArch64_Ubuntu-16.04_aarch64-linux/bin:/opt/arm/arm-hpc-compiler-19.3_Generic-AArch64_Ubuntu-16.04_aarch64-linux/bin:$PATH''')

    @aarch64
    @centos
    @docker
    def test_defaults_centos(self):
        """Default arm_allinea_studio building block"""
        a = arm_allinea_studio(eula=True)
        self.assertEqual(str(a),
r'''# Arm Allinea Studio version 19.3
RUN yum install -y \
        glibc-devel \
        tar \
        wget && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://developer.arm.com/-/media/Files/downloads/hpc/arm-allinea-studio/19-3/RHEL7/Arm-Compiler-for-HPC_19.3_RHEL_7_aarch64.tar && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/Arm-Compiler-for-HPC_19.3_RHEL_7_aarch64.tar -C /var/tmp && \
    cd /var/tmp/ARM-Compiler-for-HPC_19.3_AArch64_RHEL_7_aarch64 && ./arm-compiler-for-hpc-19.3_Generic-AArch64_RHEL-7_aarch64-linux-rpm.sh --install-to /opt/arm --accept && \
    rpm --erase $(rpm -qa | grep armpl | grep -v Generic-AArch64) && \
    rm -rf /var/tmp/Arm-Compiler-for-HPC_19.3_RHEL_7_aarch64.tar /var/tmp/ARM-Compiler-for-HPC_19.3_AArch64_RHEL_7_aarch64
ENV COMPILER_PATH=/opt/arm/gcc-8.2.0_Generic-AArch64_RHEL-7_aarch64-linux:$COMPILER_PATH \
    CPATH=/opt/arm/gcc-8.2.0_Generic-AArch64_RHEL-7_aarch64-linux/include:/opt/arm/arm-hpc-compiler-19.3_Generic-AArch64_RHEL-7_aarch64-linux/include:$CPATH \
    LD_LIBRARY_PATH=/opt/arm/gcc-8.2.0_Generic-AArch64_RHEL-7_aarch64-linux/lib:/opt/arm/gcc-8.2.0_Generic-AArch64_RHEL-7_aarch64-linux/lib64:/opt/arm/arm-hpc-compiler-19.3_Generic-AArch64_RHEL-7_aarch64-linux/lib:$LD_LIBRARY_PATH \
    LIBRARY_PATH=/opt/arm/gcc-8.2.0_Generic-AArch64_RHEL-7_aarch64-linux/lib:/opt/arm/gcc-8.2.0_Generic-AArch64_RHEL-7_aarch64-linux/lib64:/opt/arm/arm-hpc-compiler-19.3_Generic-AArch64_RHEL-7_aarch64-linux/lib:$LIBRARY_PATH \
    PATH=/opt/arm/gcc-8.2.0_Generic-AArch64_RHEL-7_aarch64-linux/bin:/opt/arm/arm-hpc-compiler-19.3_Generic-AArch64_RHEL-7_aarch64-linux/bin:$PATH''')

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
                               tarball='Arm-Compiler-for-HPC_19.3_Ubuntu_16.04_aarch64.tar')
        self.assertEqual(str(a),
r'''# Arm Allinea Studio version 19.3
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libc6-dev \
        python \
        tar \
        wget && \
    rm -rf /var/lib/apt/lists/*
COPY Arm-Compiler-for-HPC_19.3_Ubuntu_16.04_aarch64.tar /var/tmp
RUN mkdir -p /var/tmp && tar -x -f /var/tmp/Arm-Compiler-for-HPC_19.3_Ubuntu_16.04_aarch64.tar -C /var/tmp && \
    cd /var/tmp/ARM-Compiler-for-HPC_19.3_AArch64_Ubuntu_16.04_aarch64 && ./arm-compiler-for-hpc-19.3_Generic-AArch64_Ubuntu-16.04_aarch64-linux-deb.sh --install-to /opt/arm --accept && \
    find /opt/arm -maxdepth 1 -type d -name "armpl-*" -not -name "*Generic-AArch64*" -print0 | xargs -0 rm -rf && \
    rm -rf /var/tmp/Arm-Compiler-for-HPC_19.3_Ubuntu_16.04_aarch64.tar /var/tmp/ARM-Compiler-for-HPC_19.3_AArch64_Ubuntu_16.04_aarch64
ENV COMPILER_PATH=/opt/arm/gcc-8.2.0_Generic-AArch64_Ubuntu-16.04_aarch64-linux:$COMPILER_PATH \
    CPATH=/opt/arm/gcc-8.2.0_Generic-AArch64_Ubuntu-16.04_aarch64-linux/include:/opt/arm/arm-hpc-compiler-19.3_Generic-AArch64_Ubuntu-16.04_aarch64-linux/include:$CPATH \
    LD_LIBRARY_PATH=/opt/arm/gcc-8.2.0_Generic-AArch64_Ubuntu-16.04_aarch64-linux/lib:/opt/arm/gcc-8.2.0_Generic-AArch64_Ubuntu-16.04_aarch64-linux/lib64:/opt/arm/arm-hpc-compiler-19.3_Generic-AArch64_Ubuntu-16.04_aarch64-linux/lib:$LD_LIBRARY_PATH \
    LIBRARY_PATH=/opt/arm/gcc-8.2.0_Generic-AArch64_Ubuntu-16.04_aarch64-linux/lib:/opt/arm/gcc-8.2.0_Generic-AArch64_Ubuntu-16.04_aarch64-linux/lib64:/opt/arm/arm-hpc-compiler-19.3_Generic-AArch64_Ubuntu-16.04_aarch64-linux/lib:$LIBRARY_PATH \
    PATH=/opt/arm/gcc-8.2.0_Generic-AArch64_Ubuntu-16.04_aarch64-linux/bin:/opt/arm/arm-hpc-compiler-19.3_Generic-AArch64_Ubuntu-16.04_aarch64-linux/bin:$PATH''')

    @aarch64
    @centos
    @docker
    def test_runtime_centos(self):
        """Runtime"""
        a = arm_allinea_studio(eula=True)
        r = a.runtime()
        self.assertEqual(r,
r'''# Arm Allinea Studio
COPY --from=0 /opt/arm/gcc-8.2.0_Generic-AArch64_RHEL-7_aarch64-linux/lib64/*.so* /opt/arm/gcc-8.2.0_Generic-AArch64_RHEL-7_aarch64-linux/lib64/
COPY --from=0 /opt/arm/arm-hpc-compiler-19.3_Generic-AArch64_RHEL-7_aarch64-linux/lib/*.so* /opt/arm/arm-hpc-compiler-19.3_Generic-AArch64_RHEL-7_aarch64-linux/lib/
COPY --from=0 /opt/arm/arm-hpc-compiler-19.3_Generic-AArch64_RHEL-7_aarch64-linux/lib/clang/7.1.0/lib/linux/*.so* /opt/arm/arm-hpc-compiler-19.3_Generic-AArch64_RHEL-7_aarch64-linux/lib/clang/7.1.0/lib/linux/
COPY --from=0 /opt/arm/armpl-19.3.0_Generic-AArch64_RHEL-7_arm-hpc-compiler_19.3_aarch64-linux/lib/*.so* /opt/arm/armpl-19.3.0_Generic-AArch64_RHEL-7_arm-hpc-compiler_19.3_aarch64-linux/lib/
COPY --from=0 /opt/arm/arm-hpc-compiler-19.3_Generic-AArch64_RHEL-7_aarch64-linux/lib/clang/7.1.0/armpl_links/lib /opt/arm/arm-hpc-compiler-19.3_Generic-AArch64_RHEL-7_aarch64-linux/lib/clang/7.1.0/armpl_links/lib
ENV LD_LIBRARY_PATH=/opt/arm/gcc-8.2.0_Generic-AArch64_RHEL-7_aarch64-linux/lib64:/opt/arm/arm-hpc-compiler-19.3_Generic-AArch64_RHEL-7_aarch64-linux/lib:/opt/arm/arm-hpc-compiler-19.3_Generic-AArch64_RHEL-7_aarch64-linux/lib/clang/7.1.0/lib/linux:/opt/arm/armpl-19.3.0_Generic-AArch64_RHEL-7_arm-hpc-compiler_19.3_aarch64-linux/lib:$LD_LIBRARY_PATH''')

    def test_toolchain(self):
        """Toolchain"""
        a = arm_allinea_studio(eula=True)
        tc = a.toolchain
        self.assertEqual(tc.CC, 'armclang')
        self.assertEqual(tc.CXX, 'armclang++')
        self.assertEqual(tc.FC, 'armflang')
        self.assertEqual(tc.F77, 'armflang')
        self.assertEqual(tc.F90, 'armflang')
