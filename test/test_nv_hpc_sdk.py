# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
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

"""Test cases for the nv_hpc_sdk module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import aarch64, centos, docker, ppc64le, ubuntu, x86_64

from hpccm.building_blocks.nv_hpc_sdk import nv_hpc_sdk

class Test_nv_hpc_sdk(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @x86_64
    @ubuntu
    @docker
    def test_defaults_ubuntu(self):
        """Default HPC SDK building block"""
        n = nv_hpc_sdk(eula=True, tarball='nvhpc_2020_205_Linux_x86_64.tar.gz')
        self.assertEqual(str(n),
r'''# NVIDIA HPC SDK version 20.5
COPY nvhpc_2020_205_Linux_x86_64.tar.gz /var/tmp/nvhpc_2020_205_Linux_x86_64.tar.gz
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        g++ \
        gcc \
        gfortran \
        libnuma1 && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp/nv_hpc_sdk && tar -x -f /var/tmp/nvhpc_2020_205_Linux_x86_64.tar.gz -C /var/tmp/nv_hpc_sdk -z && \
    cd /var/tmp/nv_hpc_sdk && NVCOMPILER_ACCEPT_EULA=accept NVCOMPILER_INSTALL_DIR=/opt/nvidia/hpcsdk NVCOMPILER_INSTALL_MPI=false NVCOMPILER_INSTALL_NVIDIA=true NVCOMPILER_MPI_GPU_SUPPORT=false NVCOMPILER_SILENT=true ./install && \
    rm -rf /var/tmp/nvhpc_2020_205_Linux_x86_64.tar.gz /var/tmp/nv_hpc_sdk
ENV LD_LIBRARY_PATH=/opt/nvidia/hpcsdk/Linux_x86_64/20.5/compilers/lib:$LD_LIBRARY_PATH \
    PATH=/opt/nvidia/hpcsdk/Linux_x86_64/20.5/compilers/bin:$PATH''')

    @x86_64
    @centos
    @docker
    def test_defaults_centos(self):
        """Default HPC SDK building block"""
        n = nv_hpc_sdk(eula=True, tarball='nvhpc_2020_205_Linux_x86_64.tar.gz')
        self.assertEqual(str(n),        
r'''# NVIDIA HPC SDK version 20.5
COPY nvhpc_2020_205_Linux_x86_64.tar.gz /var/tmp/nvhpc_2020_205_Linux_x86_64.tar.gz
RUN yum install -y \
        gcc \
        gcc-c++ \
        gcc-gfortran \
        numactl-libs && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp/nv_hpc_sdk && tar -x -f /var/tmp/nvhpc_2020_205_Linux_x86_64.tar.gz -C /var/tmp/nv_hpc_sdk -z && \
    cd /var/tmp/nv_hpc_sdk && NVCOMPILER_ACCEPT_EULA=accept NVCOMPILER_INSTALL_DIR=/opt/nvidia/hpcsdk NVCOMPILER_INSTALL_MPI=false NVCOMPILER_INSTALL_NVIDIA=true NVCOMPILER_MPI_GPU_SUPPORT=false NVCOMPILER_SILENT=true ./install && \
    rm -rf /var/tmp/nvhpc_2020_205_Linux_x86_64.tar.gz /var/tmp/nv_hpc_sdk
ENV LD_LIBRARY_PATH=/opt/nvidia/hpcsdk/Linux_x86_64/20.5/compilers/lib:$LD_LIBRARY_PATH \
    PATH=/opt/nvidia/hpcsdk/Linux_x86_64/20.5/compilers/bin:$PATH''')

    @x86_64
    @ubuntu
    @docker
    def test_system_cuda(self):
        """System CUDA"""
        n = nv_hpc_sdk(eula=True, system_cuda=True,
                       tarball='nvhpc_2020_205_Linux_x86_64.tar.gz')
        self.assertEqual(str(n),
r'''# NVIDIA HPC SDK version 20.5
COPY nvhpc_2020_205_Linux_x86_64.tar.gz /var/tmp/nvhpc_2020_205_Linux_x86_64.tar.gz
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        g++ \
        gcc \
        gfortran \
        libnuma1 && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp/nv_hpc_sdk && tar -x -f /var/tmp/nvhpc_2020_205_Linux_x86_64.tar.gz -C /var/tmp/nv_hpc_sdk -z && \
    cd /var/tmp/nv_hpc_sdk && NVCOMPILER_ACCEPT_EULA=accept NVCOMPILER_INSTALL_DIR=/opt/nvidia/hpcsdk NVCOMPILER_INSTALL_MPI=false NVCOMPILER_INSTALL_NVIDIA=false NVCOMPILER_MPI_GPU_SUPPORT=false NVCOMPILER_SILENT=true ./install && \
    echo "set CUDAROOT=/usr/local/cuda;" >> /opt/nvidia/hpcsdk/Linux_x86_64/20.5/compilers/bin/siterc && \
    echo "variable LIBRARY_PATH is environment(LIBRARY_PATH);" >> /opt/nvidia/hpcsdk/Linux_x86_64/20.5/compilers/bin/siterc && \
    echo "variable library_path is default(\$if(\$LIBRARY_PATH,\$foreach(ll,\$replace(\$LIBRARY_PATH,":",), -L\$ll)));" >> /opt/nvidia/hpcsdk/Linux_x86_64/20.5/compilers/bin/siterc && \
    echo "append LDLIBARGS=\$library_path;" >> /opt/nvidia/hpcsdk/Linux_x86_64/20.5/compilers/bin/siterc && \
    rm -rf /var/tmp/nvhpc_2020_205_Linux_x86_64.tar.gz /var/tmp/nv_hpc_sdk
ENV LD_LIBRARY_PATH=/opt/nvidia/hpcsdk/Linux_x86_64/20.5/compilers/lib:$LD_LIBRARY_PATH \
    PATH=/opt/nvidia/hpcsdk/Linux_x86_64/20.5/compilers/bin:$PATH''')

    @x86_64
    @ubuntu
    @docker
    def test_mpi(self):
        """MPI enabled"""
        n = nv_hpc_sdk(eula=True, mpi=True,
                       tarball='nvhpc_2020_205_Linux_x86_64.tar.gz')
        self.assertEqual(str(n),
r'''# NVIDIA HPC SDK version 20.5
COPY nvhpc_2020_205_Linux_x86_64.tar.gz /var/tmp/nvhpc_2020_205_Linux_x86_64.tar.gz
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        g++ \
        gcc \
        gfortran \
        libnuma1 \
        openssh-client && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp/nv_hpc_sdk && tar -x -f /var/tmp/nvhpc_2020_205_Linux_x86_64.tar.gz -C /var/tmp/nv_hpc_sdk -z && \
    cd /var/tmp/nv_hpc_sdk && NVCOMPILER_ACCEPT_EULA=accept NVCOMPILER_INSTALL_DIR=/opt/nvidia/hpcsdk NVCOMPILER_INSTALL_MPI=true NVCOMPILER_INSTALL_NVIDIA=true NVCOMPILER_MPI_GPU_SUPPORT=true NVCOMPILER_SILENT=true ./install && \
    rm -rf /var/tmp/nvhpc_2020_205_Linux_x86_64.tar.gz /var/tmp/nv_hpc_sdk
ENV LD_LIBRARY_PATH=/opt/nvidia/hpcsdk/Linux_x86_64/2020/mpi/openmpi-3.1.5/lib:/opt/nvidia/hpcsdk/Linux_x86_64/20.5/compilers/lib:$LD_LIBRARY_PATH \
    PATH=/opt/nvidia/hpcsdk/Linux_x86_64/2020/mpi/openmpi-3.1.5/bin:/opt/nvidia/hpcsdk/Linux_x86_64/20.5/compilers/bin:$PATH''')

    @x86_64
    @ubuntu
    @docker
    def test_extended_environment(self):
        """Extended environment without MPI"""
        n = nv_hpc_sdk(eula=True, extended_environment=True,
                       tarball='nvhpc_2020_205_Linux_x86_64.tar.gz')
        self.assertEqual(str(n),
r'''# NVIDIA HPC SDK version 20.5
COPY nvhpc_2020_205_Linux_x86_64.tar.gz /var/tmp/nvhpc_2020_205_Linux_x86_64.tar.gz
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        g++ \
        gcc \
        gfortran \
        libnuma1 && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp/nv_hpc_sdk && tar -x -f /var/tmp/nvhpc_2020_205_Linux_x86_64.tar.gz -C /var/tmp/nv_hpc_sdk -z && \
    cd /var/tmp/nv_hpc_sdk && NVCOMPILER_ACCEPT_EULA=accept NVCOMPILER_INSTALL_DIR=/opt/nvidia/hpcsdk NVCOMPILER_INSTALL_MPI=false NVCOMPILER_INSTALL_NVIDIA=true NVCOMPILER_MPI_GPU_SUPPORT=false NVCOMPILER_SILENT=true ./install && \
    rm -rf /var/tmp/nvhpc_2020_205_Linux_x86_64.tar.gz /var/tmp/nv_hpc_sdk
ENV CC=/opt/nvidia/hpcsdk/Linux_x86_64/20.5/compilers/bin/pgcc \
    CPP="/opt/nvidia/hpcsdk/Linux_x86_64/20.5/compilers/bin/nvc -Mcpp" \
    CXX=/opt/nvidia/hpcsdk/Linux_x86_64/20.5/compilers/bin/nvc++ \
    F77=/opt/nvidia/hpcsdk/Linux_x86_64/20.5/compilers/bin/nvfortran \
    F90=/opt/nvidia/hpcsdk/Linux_x86_64/20.5/compilers/bin/nvfortran \
    FC=/opt/nvidia/hpcsdk/Linux_x86_64/20.5/compilers/bin/nvfortran \
    LD_LIBRARY_PATH=/opt/nvidia/hpcsdk/Linux_x86_64/20.5/compilers/lib:$LD_LIBRARY_PATH \
    MODULEPATH=/opt/nvidia/hpcsdk/modulefiles:$MODULEPATH \
    PATH=/opt/nvidia/hpcsdk/Linux_x86_64/20.5/compilers/bin:$PATH''')

    @x86_64
    @ubuntu
    @docker
    def test_extended_environment_mpi(self):
        """Extended environment with MPI"""
        n = nv_hpc_sdk(eula=True, extended_environment=True, mpi=True,
                       tarball='nvhpc_2020_205_Linux_x86_64.tar.gz')
        self.assertEqual(str(n),
r'''# NVIDIA HPC SDK version 20.5
COPY nvhpc_2020_205_Linux_x86_64.tar.gz /var/tmp/nvhpc_2020_205_Linux_x86_64.tar.gz
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        g++ \
        gcc \
        gfortran \
        libnuma1 \
        openssh-client && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp/nv_hpc_sdk && tar -x -f /var/tmp/nvhpc_2020_205_Linux_x86_64.tar.gz -C /var/tmp/nv_hpc_sdk -z && \
    cd /var/tmp/nv_hpc_sdk && NVCOMPILER_ACCEPT_EULA=accept NVCOMPILER_INSTALL_DIR=/opt/nvidia/hpcsdk NVCOMPILER_INSTALL_MPI=true NVCOMPILER_INSTALL_NVIDIA=true NVCOMPILER_MPI_GPU_SUPPORT=true NVCOMPILER_SILENT=true ./install && \
    rm -rf /var/tmp/nvhpc_2020_205_Linux_x86_64.tar.gz /var/tmp/nv_hpc_sdk
ENV CC=/opt/nvidia/hpcsdk/Linux_x86_64/20.5/compilers/bin/pgcc \
    CPP="/opt/nvidia/hpcsdk/Linux_x86_64/20.5/compilers/bin/nvc -Mcpp" \
    CXX=/opt/nvidia/hpcsdk/Linux_x86_64/20.5/compilers/bin/nvc++ \
    F77=/opt/nvidia/hpcsdk/Linux_x86_64/20.5/compilers/bin/nvfortran \
    F90=/opt/nvidia/hpcsdk/Linux_x86_64/20.5/compilers/bin/nvfortran \
    FC=/opt/nvidia/hpcsdk/Linux_x86_64/20.5/compilers/bin/nvfortran \
    LD_LIBRARY_PATH=/opt/nvidia/hpcsdk/Linux_x86_64/2020/mpi/openmpi-3.1.5/lib:/opt/nvidia/hpcsdk/Linux_x86_64/20.5/compilers/lib:$LD_LIBRARY_PATH \
    MODULEPATH=/opt/nvidia/hpcsdk/modulefiles:$MODULEPATH \
    PATH=/opt/nvidia/hpcsdk/Linux_x86_64/2020/mpi/openmpi-3.1.5/bin:/opt/nvidia/hpcsdk/Linux_x86_64/20.5/compilers/bin:$PATH \
    PGI_OPTL_INCLUDE_DIRS=/opt/nvidia/hpcsdk/Linux_x86_64/2020/mpi/openmpi-3.1.5/include \
    PGI_OPTL_LIB_DIRS=/opt/nvidia/hpcsdk/Linux_x86_64/2020/mpi/openmpi-3.1.5/lib''')

    @aarch64
    @ubuntu
    @docker
    def test_aarch64(self):
        """Default HPC SDK building block on aarch64"""
        n = nv_hpc_sdk(eula=True, mpi=True,
                       tarball='nvhpc_2020_205_Linux_aarch64.tar.gz')
        self.assertEqual(str(n),
r'''# NVIDIA HPC SDK version 20.5
COPY nvhpc_2020_205_Linux_aarch64.tar.gz /var/tmp/nvhpc_2020_205_Linux_aarch64.tar.gz
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        g++ \
        gcc \
        gfortran \
        libnuma1 \
        openssh-client && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp/nv_hpc_sdk && tar -x -f /var/tmp/nvhpc_2020_205_Linux_aarch64.tar.gz -C /var/tmp/nv_hpc_sdk -z && \
    cd /var/tmp/nv_hpc_sdk && NVCOMPILER_ACCEPT_EULA=accept NVCOMPILER_INSTALL_DIR=/opt/nvidia/hpcsdk NVCOMPILER_INSTALL_MPI=true NVCOMPILER_INSTALL_NVIDIA=true NVCOMPILER_MPI_GPU_SUPPORT=true NVCOMPILER_SILENT=true ./install && \
    rm -rf /var/tmp/nvhpc_2020_205_Linux_aarch64.tar.gz /var/tmp/nv_hpc_sdk
ENV LD_LIBRARY_PATH=/opt/nvidia/hpcsdk/Linux_aarch64/2020/mpi/openmpi-3.1.5/lib:/opt/nvidia/hpcsdk/Linux_aarch64/20.5/compilers/lib:$LD_LIBRARY_PATH \
    PATH=/opt/nvidia/hpcsdk/Linux_aarch64/2020/mpi/openmpi-3.1.5/bin:/opt/nvidia/hpcsdk/Linux_aarch64/20.5/compilers/bin:$PATH''')

    @ppc64le
    @centos
    @docker
    def test_ppc64le(self):
        """Default HPC SDK building block on ppc64le"""
        n = nv_hpc_sdk(eula=True, mpi=True,
                       tarball='nvhpc_2020_205_Linux_ppc64le.tar.gz')
        self.assertEqual(str(n),
r'''# NVIDIA HPC SDK version 20.5
COPY nvhpc_2020_205_Linux_ppc64le.tar.gz /var/tmp/nvhpc_2020_205_Linux_ppc64le.tar.gz
RUN yum install -y \
        gcc \
        gcc-c++ \
        gcc-gfortran \
        numactl-libs \
        openssh-clients && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp/nv_hpc_sdk && tar -x -f /var/tmp/nvhpc_2020_205_Linux_ppc64le.tar.gz -C /var/tmp/nv_hpc_sdk -z && \
    cd /var/tmp/nv_hpc_sdk && NVCOMPILER_ACCEPT_EULA=accept NVCOMPILER_INSTALL_DIR=/opt/nvidia/hpcsdk NVCOMPILER_INSTALL_MPI=true NVCOMPILER_INSTALL_NVIDIA=true NVCOMPILER_MPI_GPU_SUPPORT=true NVCOMPILER_SILENT=true ./install && \
    rm -rf /var/tmp/nvhpc_2020_205_Linux_ppc64le.tar.gz /var/tmp/nv_hpc_sdk
ENV LD_LIBRARY_PATH=/opt/nvidia/hpcsdk/Linux_ppc64le/2020/mpi/openmpi-3.1.5/lib:/opt/nvidia/hpcsdk/Linux_ppc64le/20.5/compilers/lib:$LD_LIBRARY_PATH \
    PATH=/opt/nvidia/hpcsdk/Linux_ppc64le/2020/mpi/openmpi-3.1.5/bin:/opt/nvidia/hpcsdk/Linux_ppc64le/20.5/compilers/bin:$PATH''')

    @x86_64
    @ubuntu
    @docker
    def test_runtime_ubuntu(self):
        """Runtime"""
        n = nv_hpc_sdk(tarball='nvhpc_2020_205_Linux_x86_64.tar.gz')
        r = n.runtime()
        self.assertEqual(r,
r'''# NVIDIA HPC SDK
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libatomic1 \
        libnuma1 && \
    rm -rf /var/lib/apt/lists/*
COPY --from=0 /opt/nvidia/hpcsdk/Linux_x86_64/20.5/compilers/REDIST/*.so* /opt/nvidia/hpcsdk/Linux_x86_64/20.5/compilers/lib/
ENV LD_LIBRARY_PATH=/opt/nvidia/hpcsdk/Linux_x86_64/20.5/compilers/lib:$LD_LIBRARY_PATH''')

    @x86_64
    @centos
    @docker
    def test_runtime_centos(self):
        """Runtime"""
        n = nv_hpc_sdk(tarball='nvhpc_2020_205_Linux_x86_64.tar.gz')
        r = n.runtime()
        self.assertEqual(r,
r'''# NVIDIA HPC SDK
RUN yum install -y \
        libatomic \
        numactl-libs && \
    rm -rf /var/cache/yum/*
COPY --from=0 /opt/nvidia/hpcsdk/Linux_x86_64/20.5/compilers/REDIST/*.so* /opt/nvidia/hpcsdk/Linux_x86_64/20.5/compilers/lib/
ENV LD_LIBRARY_PATH=/opt/nvidia/hpcsdk/Linux_x86_64/20.5/compilers/lib:$LD_LIBRARY_PATH''')

    @x86_64
    @centos
    @docker
    def test_runtime_mpi_centos(self):
        """Runtime"""
        n = nv_hpc_sdk(mpi=True, tarball='nvhpc_2020_205_Linux_x86_64.tar.gz')
        r = n.runtime()
        self.assertEqual(r,
r'''# NVIDIA HPC SDK
RUN yum install -y \
        libatomic \
        numactl-libs \
        openssh-clients && \
    rm -rf /var/cache/yum/*
COPY --from=0 /opt/nvidia/hpcsdk/Linux_x86_64/20.5/compilers/REDIST/*.so* /opt/nvidia/hpcsdk/Linux_x86_64/20.5/compilers/lib/
COPY --from=0 /opt/nvidia/hpcsdk/Linux_x86_64/2020/mpi/openmpi-3.1.5 /opt/nvidia/hpcsdk/Linux_x86_64/2020/mpi/openmpi-3.1.5
ENV LD_LIBRARY_PATH=/opt/nvidia/hpcsdk/Linux_x86_64/2020/mpi/openmpi-3.1.5/lib:/opt/nvidia/hpcsdk/Linux_x86_64/20.5/compilers/lib:$LD_LIBRARY_PATH \
    PATH=/opt/nvidia/hpcsdk/Linux_x86_64/2020/mpi/openmpi-3.1.5/bin:$PATH''')

    def test_toolchain(self):
        """Toolchain"""
        n = nv_hpc_sdk(tarball='nvhpc_2020_205_Linux_x86_64.tar.gz')
        tc = n.toolchain
        self.assertEqual(tc.CC, 'nvc')
        self.assertEqual(tc.CXX, 'nvc++')
        self.assertEqual(tc.FC, 'nvfortran')
        self.assertEqual(tc.F77, 'nvfortran')
        self.assertEqual(tc.F90, 'nvfortran')
