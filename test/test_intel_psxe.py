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

"""Test cases for the intel_psxe module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import centos, docker, ubuntu

from hpccm.building_blocks.intel_psxe import intel_psxe

class Test_intel_psxe(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @ubuntu
    @docker
    def test_defaults(self):
        """Default intel_psxe building block, no eula agreement"""
        with self.assertRaises(RuntimeError):
            psxe = intel_psxe()
            str(psxe)

    @ubuntu
    @docker
    def test_license_file(self):
        """intel_psxe building license file"""
        psxe = intel_psxe(eula=True, license='XXXXXXXX.lic', tarball='parallel_studio_xe_2018_update1_professional_edition.tgz')
        self.assertEqual(str(psxe),
r'''# Intel Parallel Studio XE
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        build-essential \
        cpio && \
    rm -rf /var/lib/apt/lists/*
COPY parallel_studio_xe_2018_update1_professional_edition.tgz /var/tmp/parallel_studio_xe_2018_update1_professional_edition.tgz
COPY XXXXXXXX.lic /var/tmp/license.lic
RUN mkdir -p /var/tmp && tar -x -f /var/tmp/parallel_studio_xe_2018_update1_professional_edition.tgz -C /var/tmp -z && \
    sed -i -e 's/^#\?\(COMPONENTS\)=.*/\1=DEFAULTS/g' \
        -e 's|^#\?\(PSET_INSTALL_DIR\)=.*|\1=/opt/intel|g' \
        -e 's/^#\?\(ACCEPT_EULA\)=.*/\1=accept/g' \
        -e 's/^#\?\(ACTIVATION_TYPE\)=.*/\1=license_file/g' \
        -e 's|^#\?\(ACTIVATION_LICENSE_FILE\)=.*|\1=/var/tmp/license.lic|g' /var/tmp/parallel_studio_xe_2018_update1_professional_edition/silent.cfg && \
    cd /var/tmp/parallel_studio_xe_2018_update1_professional_edition && ./install.sh --silent=silent.cfg && \
    rm -rf /var/tmp/parallel_studio_xe_2018_update1_professional_edition.tgz /var/tmp/parallel_studio_xe_2018_update1_professional_edition
RUN echo "source /opt/intel/compilers_and_libraries/linux/bin/compilervars.sh intel64" >> /etc/bash.bashrc''')

    @centos
    @docker
    def test_centos(self):
        """centos"""
        psxe = intel_psxe(eula=True, tarball='parallel_studio_xe_2018_update1_professional_edition.tgz')
        self.assertEqual(str(psxe),
r'''# Intel Parallel Studio XE
RUN yum install -y \
        gcc \
        gcc-c++ \
        make \
        which && \
    rm -rf /var/cache/yum/*
COPY parallel_studio_xe_2018_update1_professional_edition.tgz /var/tmp/parallel_studio_xe_2018_update1_professional_edition.tgz
RUN mkdir -p /var/tmp && tar -x -f /var/tmp/parallel_studio_xe_2018_update1_professional_edition.tgz -C /var/tmp -z && \
    sed -i -e 's/^#\?\(COMPONENTS\)=.*/\1=DEFAULTS/g' \
        -e 's|^#\?\(PSET_INSTALL_DIR\)=.*|\1=/opt/intel|g' \
        -e 's/^#\?\(ACCEPT_EULA\)=.*/\1=accept/g' /var/tmp/parallel_studio_xe_2018_update1_professional_edition/silent.cfg && \
    cd /var/tmp/parallel_studio_xe_2018_update1_professional_edition && ./install.sh --silent=silent.cfg && \
    rm -rf /var/tmp/parallel_studio_xe_2018_update1_professional_edition.tgz /var/tmp/parallel_studio_xe_2018_update1_professional_edition
RUN echo "source /opt/intel/compilers_and_libraries/linux/bin/compilervars.sh intel64" >> /etc/bashrc''')

    @ubuntu
    @docker
    def test_license_server(self):
        """intel_psxe building license server"""
        psxe = intel_psxe(eula=True, license='12345@server-lic', tarball='parallel_studio_xe_2018_update1_professional_edition.tgz')
        self.assertEqual(str(psxe),
r'''# Intel Parallel Studio XE
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        build-essential \
        cpio && \
    rm -rf /var/lib/apt/lists/*
COPY parallel_studio_xe_2018_update1_professional_edition.tgz /var/tmp/parallel_studio_xe_2018_update1_professional_edition.tgz
RUN mkdir -p /var/tmp && tar -x -f /var/tmp/parallel_studio_xe_2018_update1_professional_edition.tgz -C /var/tmp -z && \
    sed -i -e 's/^#\?\(COMPONENTS\)=.*/\1=DEFAULTS/g' \
        -e 's|^#\?\(PSET_INSTALL_DIR\)=.*|\1=/opt/intel|g' \
        -e 's/^#\?\(ACCEPT_EULA\)=.*/\1=accept/g' \
        -e 's/^#\?\(ACTIVATION_TYPE\)=.*/\1=license_server/g' \
        -e 's/^#\?\(ACTIVATION_LICENSE_FILE\)=.*/\1=12345@server-lic/g' /var/tmp/parallel_studio_xe_2018_update1_professional_edition/silent.cfg && \
    cd /var/tmp/parallel_studio_xe_2018_update1_professional_edition && ./install.sh --silent=silent.cfg && \
    rm -rf /var/tmp/parallel_studio_xe_2018_update1_professional_edition.tgz /var/tmp/parallel_studio_xe_2018_update1_professional_edition
RUN echo "source /opt/intel/compilers_and_libraries/linux/bin/compilervars.sh intel64" >> /etc/bash.bashrc''')

    @ubuntu
    @docker
    def test_psxevars_false(self):
        """psxevars is false"""
        psxe = intel_psxe(eula=True, psxevars=False, tarball='parallel_studio_xe_2018_update1_professional_edition.tgz')
        self.assertEqual(str(psxe),
r'''# Intel Parallel Studio XE
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        build-essential \
        cpio && \
    rm -rf /var/lib/apt/lists/*
COPY parallel_studio_xe_2018_update1_professional_edition.tgz /var/tmp/parallel_studio_xe_2018_update1_professional_edition.tgz
RUN mkdir -p /var/tmp && tar -x -f /var/tmp/parallel_studio_xe_2018_update1_professional_edition.tgz -C /var/tmp -z && \
    sed -i -e 's/^#\?\(COMPONENTS\)=.*/\1=DEFAULTS/g' \
        -e 's|^#\?\(PSET_INSTALL_DIR\)=.*|\1=/opt/intel|g' \
        -e 's/^#\?\(ACCEPT_EULA\)=.*/\1=accept/g' /var/tmp/parallel_studio_xe_2018_update1_professional_edition/silent.cfg && \
    cd /var/tmp/parallel_studio_xe_2018_update1_professional_edition && ./install.sh --silent=silent.cfg && \
    rm -rf /var/tmp/parallel_studio_xe_2018_update1_professional_edition.tgz /var/tmp/parallel_studio_xe_2018_update1_professional_edition
ENV CPATH=/opt/intel/compilers_and_libraries/linux/daal/include:/opt/intel/compilers_and_libraries/linux/pstl/include:/opt/intel/compilers_and_libraries/linux/ipp/include:/opt/intel/compilers_and_libraries/linux/mkl/include:/opt/intel/compilers_and_libraries/linux/mpi/include:/opt/intel/compilers_and_libraries/linux/tbb/include:$CPATH \
    DAALROOT=/opt/intel/compilers_and_libraries/linux/daal \
    IPPROOT=/opt/intel/compilers_and_libraries/linux/ipp \
    I_MPI_ROOT=/opt/intel/compilers_and_libraries/linux/mpi \
    LD_LIBRARY_PATH=/opt/intel/compilers_and_libraries/linux/daal/lib/intel64:/opt/intel/compilers_and_libraries/linux/compiler/lib/intel64:/opt/intel/compilers_and_libraries/linux/compiler/lib/intel64:/opt/intel/compilers_and_libraries/linux/ipp/lib/intel64:/opt/intel/compilers_and_libraries/linux/mkl/lib/intel64:/opt/intel/compilers_and_libraries/linux/mpi/intel64/lib:/opt/intel/compilers_and_libraries/linux/tbb/lib/intel64/gcc4.7:$LD_LIBRARY_PATH \
    LIBRARY_PATH=/opt/intel/compilers_and_libraries/linux/daal/lib/intel64:/opt/intel/compilers_and_libraries/linux/ipp/lib/intel64:/opt/intel/compilers_and_libraries/linux/mkl/lib/intel64:/opt/intel/compilers_and_libraries/linux/tbb/lib/intel64/gcc4.7:$LIBRARY_PATH \
    MKLROOT=/opt/intel/compilers_and_libraries/linux/mkl \
    PATH=/opt/intel/compilers_and_libraries/linux/bin/intel64:/opt/intel/compilers_and_libraries/linux/bin/intel64:/opt/intel/compilers_and_libraries/linux/mpi/intel64/bin:$PATH''')

    @ubuntu
    @docker
    def test_runtime(self):
        """Runtime"""
        psxe = intel_psxe(eula=True, tarball='parallel_studio_xe_2018_update1_professional_edition.tgz', runtime_version='2018.4-274')
        r = psxe.runtime()
        self.assertEqual(r,
r'''# Intel Parallel Studio XE runtime version 2018.4-274
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
RUN wget -qO - https://apt.repos.intel.com/2018/GPG-PUB-KEY-INTEL-PSXE-RUNTIME-2018 | apt-key add - && \
    echo "deb [trusted=yes] https://apt.repos.intel.com/2018 intel-psxe-runtime main" >> /etc/apt/sources.list.d/hpccm.list && \
    apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends aptitude && \
    aptitude install -y --without-recommends -o Aptitude::ProblemResolver::SolutionCost='100*canceled-actions,200*removals' \
        intel-psxe-runtime=2018.4-274 && \
    rm -rf /var/lib/apt/lists/*
RUN echo "source /opt/intel/psxe_runtime/linux/bin/psxevars.sh intel64" >> /etc/bash.bashrc''')

    def test_toolchain(self):
        """Toolchain"""
        psxe = intel_psxe(tarball='foo.tgz')
        tc = psxe.toolchain
        self.assertEqual(tc.CC, 'icc')
        self.assertEqual(tc.CXX, 'icpc')
        self.assertEqual(tc.FC, 'ifort')
        self.assertEqual(tc.F77, 'ifort')
        self.assertEqual(tc.F90, 'ifort')
