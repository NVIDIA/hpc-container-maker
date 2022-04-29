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

"""Test cases for the nvhpc module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import aarch64, centos, docker, ppc64le, ubuntu, x86_64

from hpccm.building_blocks.nvhpc import nvhpc
from hpccm.toolchain import toolchain

class Test_nvhpc(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @x86_64
    @ubuntu
    @docker
    def test_defaults_ubuntu(self):
        """Default HPC SDK building block"""
        n = nvhpc(eula=True)
        self.assertMultiLineEqual(str(n),
r'''# NVIDIA HPC SDK version 22.3
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ca-certificates && \
    rm -rf /var/lib/apt/lists/*
RUN echo "deb [trusted=yes] https://developer.download.nvidia.com/hpc-sdk/ubuntu/amd64 /" >> /etc/apt/sources.list.d/hpccm.list && \
    apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        nvhpc-22-3-cuda-multi && \
    rm -rf /var/lib/apt/lists/*
ENV CPATH=/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/comm_libs/nvshmem/include:/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/comm_libs/nccl/include:/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/compilers/extras/qd/include/qd:/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/math_libs/include:/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/comm_libs/mpi/include:$CPATH \
    LD_LIBRARY_PATH=/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/comm_libs/nvshmem/lib:/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/comm_libs/nccl/lib:/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/math_libs/lib64:/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/compilers/lib:/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/cuda/lib64:/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/comm_libs/mpi/lib:$LD_LIBRARY_PATH \
    MANPATH=/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/compilers/man:$MANPATH \
    PATH=/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/comm_libs/nvshmem/bin:/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/comm_libs/nccl/bin:/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/profilers/bin:/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/compilers/bin:/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/cuda/bin:/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/comm_libs/mpi/bin:$PATH''')

    @x86_64
    @centos
    @docker
    def test_defaults_centos(self):
        """Default HPC SDK building block"""
        n = nvhpc(eula=True)
        self.assertMultiLineEqual(str(n),
r'''# NVIDIA HPC SDK version 22.3
RUN yum install -y \
        ca-certificates && \
    rm -rf /var/cache/yum/*
RUN yum install -y yum-utils && \
    yum-config-manager --add-repo https://developer.download.nvidia.com/hpc-sdk/rhel/nvhpc.repo && \
    yum install -y \
        nvhpc-cuda-multi-22.3 && \
    rm -rf /var/cache/yum/*
ENV CPATH=/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/comm_libs/nvshmem/include:/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/comm_libs/nccl/include:/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/compilers/extras/qd/include/qd:/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/math_libs/include:/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/comm_libs/mpi/include:$CPATH \
    LD_LIBRARY_PATH=/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/comm_libs/nvshmem/lib:/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/comm_libs/nccl/lib:/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/math_libs/lib64:/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/compilers/lib:/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/cuda/lib64:/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/comm_libs/mpi/lib:$LD_LIBRARY_PATH \
    MANPATH=/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/compilers/man:$MANPATH \
    PATH=/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/comm_libs/nvshmem/bin:/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/comm_libs/nccl/bin:/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/profilers/bin:/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/compilers/bin:/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/cuda/bin:/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/comm_libs/mpi/bin:$PATH''')

    @x86_64
    @centos
    @docker
    def test_package_centos(self):
        """Local package"""
        n = nvhpc(eula=True,
                  package='nvhpc_2020_207_Linux_x86_64_cuda_multi.tar.gz')
        self.assertMultiLineEqual(str(n),
r'''# NVIDIA HPC SDK version 20.7
COPY nvhpc_2020_207_Linux_x86_64_cuda_multi.tar.gz /var/tmp/nvhpc_2020_207_Linux_x86_64_cuda_multi.tar.gz
RUN yum install -y \
        bc \
        gcc \
        gcc-c++ \
        gcc-gfortran \
        libatomic \
        numactl-libs \
        openssh-clients \
        wget \
        which && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp && tar -x -f /var/tmp/nvhpc_2020_207_Linux_x86_64_cuda_multi.tar.gz -C /var/tmp -z && \
    cd /var/tmp/nvhpc_2020_207_Linux_x86_64_cuda_multi && NVHPC_ACCEPT_EULA=accept NVHPC_INSTALL_DIR=/opt/nvidia/hpc_sdk NVHPC_SILENT=true ./install && \
    rm -rf /var/tmp/nvhpc_2020_207_Linux_x86_64_cuda_multi /var/tmp/nvhpc_2020_207_Linux_x86_64_cuda_multi.tar.gz
ENV CPATH=/opt/nvidia/hpc_sdk/Linux_x86_64/20.7/comm_libs/nvshmem/include:/opt/nvidia/hpc_sdk/Linux_x86_64/20.7/comm_libs/nccl/include:/opt/nvidia/hpc_sdk/Linux_x86_64/20.7/compilers/extras/qd/include/qd:/opt/nvidia/hpc_sdk/Linux_x86_64/20.7/math_libs/include:/opt/nvidia/hpc_sdk/Linux_x86_64/20.7/comm_libs/mpi/include:$CPATH \
    LD_LIBRARY_PATH=/opt/nvidia/hpc_sdk/Linux_x86_64/20.7/comm_libs/nvshmem/lib:/opt/nvidia/hpc_sdk/Linux_x86_64/20.7/comm_libs/nccl/lib:/opt/nvidia/hpc_sdk/Linux_x86_64/20.7/math_libs/lib64:/opt/nvidia/hpc_sdk/Linux_x86_64/20.7/compilers/lib:/opt/nvidia/hpc_sdk/Linux_x86_64/20.7/cuda/lib64:/opt/nvidia/hpc_sdk/Linux_x86_64/20.7/comm_libs/mpi/lib:$LD_LIBRARY_PATH \
    MANPATH=/opt/nvidia/hpc_sdk/Linux_x86_64/20.7/compilers/man:$MANPATH \
    PATH=/opt/nvidia/hpc_sdk/Linux_x86_64/20.7/comm_libs/nvshmem/bin:/opt/nvidia/hpc_sdk/Linux_x86_64/20.7/comm_libs/nccl/bin:/opt/nvidia/hpc_sdk/Linux_x86_64/20.7/profilers/bin:/opt/nvidia/hpc_sdk/Linux_x86_64/20.7/compilers/bin:/opt/nvidia/hpc_sdk/Linux_x86_64/20.7/cuda/bin:/opt/nvidia/hpc_sdk/Linux_x86_64/20.7/comm_libs/mpi/bin:$PATH''')

    @x86_64
    @centos
    @docker
    def test_extended_environment(self):
        """Extended environment"""
        n = nvhpc(eula=True, extended_environment=True,
                  package='nvhpc_2020_207_Linux_x86_64_cuda_multi.tar.gz')
        self.assertMultiLineEqual(str(n),
r'''# NVIDIA HPC SDK version 20.7
COPY nvhpc_2020_207_Linux_x86_64_cuda_multi.tar.gz /var/tmp/nvhpc_2020_207_Linux_x86_64_cuda_multi.tar.gz
RUN yum install -y \
        bc \
        gcc \
        gcc-c++ \
        gcc-gfortran \
        libatomic \
        numactl-libs \
        openssh-clients \
        wget \
        which && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp && tar -x -f /var/tmp/nvhpc_2020_207_Linux_x86_64_cuda_multi.tar.gz -C /var/tmp -z && \
    cd /var/tmp/nvhpc_2020_207_Linux_x86_64_cuda_multi && NVHPC_ACCEPT_EULA=accept NVHPC_INSTALL_DIR=/opt/nvidia/hpc_sdk NVHPC_SILENT=true ./install && \
    rm -rf /var/tmp/nvhpc_2020_207_Linux_x86_64_cuda_multi /var/tmp/nvhpc_2020_207_Linux_x86_64_cuda_multi.tar.gz
ENV CC=/opt/nvidia/hpc_sdk/Linux_x86_64/20.7/compilers/bin/nvc \
    CPATH=/opt/nvidia/hpc_sdk/Linux_x86_64/20.7/comm_libs/nvshmem/include:/opt/nvidia/hpc_sdk/Linux_x86_64/20.7/comm_libs/nccl/include:/opt/nvidia/hpc_sdk/Linux_x86_64/20.7/compilers/extras/qd/include/qd:/opt/nvidia/hpc_sdk/Linux_x86_64/20.7/math_libs/include:/opt/nvidia/hpc_sdk/Linux_x86_64/20.7/comm_libs/mpi/include:$CPATH \
    CPP=cpp \
    CXX=/opt/nvidia/hpc_sdk/Linux_x86_64/20.7/compilers/bin/nvc++ \
    F77=/opt/nvidia/hpc_sdk/Linux_x86_64/20.7/compilers/bin/nvfortran \
    F90=/opt/nvidia/hpc_sdk/Linux_x86_64/20.7/compilers/bin/nvfortran \
    FC=/opt/nvidia/hpc_sdk/Linux_x86_64/20.7/compilers/bin/nvfortran \
    LD_LIBRARY_PATH=/opt/nvidia/hpc_sdk/Linux_x86_64/20.7/comm_libs/nvshmem/lib:/opt/nvidia/hpc_sdk/Linux_x86_64/20.7/comm_libs/nccl/lib:/opt/nvidia/hpc_sdk/Linux_x86_64/20.7/math_libs/lib64:/opt/nvidia/hpc_sdk/Linux_x86_64/20.7/compilers/lib:/opt/nvidia/hpc_sdk/Linux_x86_64/20.7/cuda/lib64:/opt/nvidia/hpc_sdk/Linux_x86_64/20.7/comm_libs/mpi/lib:$LD_LIBRARY_PATH \
    MANPATH=/opt/nvidia/hpc_sdk/Linux_x86_64/20.7/compilers/man:$MANPATH \
    PATH=/opt/nvidia/hpc_sdk/Linux_x86_64/20.7/comm_libs/nvshmem/bin:/opt/nvidia/hpc_sdk/Linux_x86_64/20.7/comm_libs/nccl/bin:/opt/nvidia/hpc_sdk/Linux_x86_64/20.7/profilers/bin:/opt/nvidia/hpc_sdk/Linux_x86_64/20.7/compilers/bin:/opt/nvidia/hpc_sdk/Linux_x86_64/20.7/cuda/bin:/opt/nvidia/hpc_sdk/Linux_x86_64/20.7/comm_libs/mpi/bin:$PATH''')

    @aarch64
    @ubuntu
    @docker
    def test_aarch64(self):
        """Default HPC SDK building block on aarch64"""
        n = nvhpc(cuda_multi=False, eula=True, version='21.2', tarball=True)
        self.assertMultiLineEqual(str(n),
r'''# NVIDIA HPC SDK version 21.2
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        bc \
        debianutils \
        g++ \
        gcc \
        gfortran \
        libatomic1 \
        libnuma1 \
        openssh-client \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://developer.download.nvidia.com/hpc-sdk/21.2/nvhpc_2021_212_Linux_aarch64_cuda_11.2.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/nvhpc_2021_212_Linux_aarch64_cuda_11.2.tar.gz -C /var/tmp -z && \
    cd /var/tmp/nvhpc_2021_212_Linux_aarch64_cuda_11.2 && NVHPC_ACCEPT_EULA=accept NVHPC_INSTALL_DIR=/opt/nvidia/hpc_sdk NVHPC_SILENT=true ./install && \
    rm -rf /var/tmp/nvhpc_2021_212_Linux_aarch64_cuda_11.2 /var/tmp/nvhpc_2021_212_Linux_aarch64_cuda_11.2.tar.gz
ENV CPATH=/opt/nvidia/hpc_sdk/Linux_aarch64/21.2/comm_libs/nvshmem/include:/opt/nvidia/hpc_sdk/Linux_aarch64/21.2/comm_libs/nccl/include:/opt/nvidia/hpc_sdk/Linux_aarch64/21.2/compilers/extras/qd/include/qd:/opt/nvidia/hpc_sdk/Linux_aarch64/21.2/math_libs/include:/opt/nvidia/hpc_sdk/Linux_aarch64/21.2/comm_libs/mpi/include:$CPATH \
    LD_LIBRARY_PATH=/opt/nvidia/hpc_sdk/Linux_aarch64/21.2/comm_libs/nvshmem/lib:/opt/nvidia/hpc_sdk/Linux_aarch64/21.2/comm_libs/nccl/lib:/opt/nvidia/hpc_sdk/Linux_aarch64/21.2/math_libs/lib64:/opt/nvidia/hpc_sdk/Linux_aarch64/21.2/compilers/lib:/opt/nvidia/hpc_sdk/Linux_aarch64/21.2/cuda/lib64:/opt/nvidia/hpc_sdk/Linux_aarch64/21.2/comm_libs/mpi/lib:$LD_LIBRARY_PATH \
    MANPATH=/opt/nvidia/hpc_sdk/Linux_aarch64/21.2/compilers/man:$MANPATH \
    PATH=/opt/nvidia/hpc_sdk/Linux_aarch64/21.2/comm_libs/nvshmem/bin:/opt/nvidia/hpc_sdk/Linux_aarch64/21.2/comm_libs/nccl/bin:/opt/nvidia/hpc_sdk/Linux_aarch64/21.2/profilers/bin:/opt/nvidia/hpc_sdk/Linux_aarch64/21.2/compilers/bin:/opt/nvidia/hpc_sdk/Linux_aarch64/21.2/cuda/bin:/opt/nvidia/hpc_sdk/Linux_aarch64/21.2/comm_libs/mpi/bin:$PATH''')

    @ppc64le
    @ubuntu
    @docker
    def test_ppc64le(self):
        """Default HPC SDK building block on ppc64le"""
        n = nvhpc(eula=True, cuda_multi=False, cuda='11.0', version='20.7',
                  tarball=True)
        self.assertMultiLineEqual(str(n),
r'''# NVIDIA HPC SDK version 20.7
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        bc \
        debianutils \
        g++ \
        gcc \
        gfortran \
        libatomic1 \
        libnuma1 \
        openssh-client \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://developer.download.nvidia.com/hpc-sdk/20.7/nvhpc_2020_207_Linux_ppc64le_cuda_11.0.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/nvhpc_2020_207_Linux_ppc64le_cuda_11.0.tar.gz -C /var/tmp -z && \
    cd /var/tmp/nvhpc_2020_207_Linux_ppc64le_cuda_11.0 && NVHPC_ACCEPT_EULA=accept NVHPC_DEFAULT_CUDA=11.0 NVHPC_INSTALL_DIR=/opt/nvidia/hpc_sdk NVHPC_SILENT=true ./install && \
    rm -rf /var/tmp/nvhpc_2020_207_Linux_ppc64le_cuda_11.0 /var/tmp/nvhpc_2020_207_Linux_ppc64le_cuda_11.0.tar.gz
ENV CPATH=/opt/nvidia/hpc_sdk/Linux_ppc64le/20.7/comm_libs/nvshmem/include:/opt/nvidia/hpc_sdk/Linux_ppc64le/20.7/comm_libs/nccl/include:/opt/nvidia/hpc_sdk/Linux_ppc64le/20.7/compilers/extras/qd/include/qd:/opt/nvidia/hpc_sdk/Linux_ppc64le/20.7/math_libs/include:/opt/nvidia/hpc_sdk/Linux_ppc64le/20.7/comm_libs/mpi/include:$CPATH \
    LD_LIBRARY_PATH=/opt/nvidia/hpc_sdk/Linux_ppc64le/20.7/comm_libs/nvshmem/lib:/opt/nvidia/hpc_sdk/Linux_ppc64le/20.7/comm_libs/nccl/lib:/opt/nvidia/hpc_sdk/Linux_ppc64le/20.7/math_libs/lib64:/opt/nvidia/hpc_sdk/Linux_ppc64le/20.7/compilers/lib:/opt/nvidia/hpc_sdk/Linux_ppc64le/20.7/cuda/lib64:/opt/nvidia/hpc_sdk/Linux_ppc64le/20.7/comm_libs/mpi/lib:$LD_LIBRARY_PATH \
    MANPATH=/opt/nvidia/hpc_sdk/Linux_ppc64le/20.7/compilers/man:$MANPATH \
    PATH=/opt/nvidia/hpc_sdk/Linux_ppc64le/20.7/comm_libs/nvshmem/bin:/opt/nvidia/hpc_sdk/Linux_ppc64le/20.7/comm_libs/nccl/bin:/opt/nvidia/hpc_sdk/Linux_ppc64le/20.7/profilers/bin:/opt/nvidia/hpc_sdk/Linux_ppc64le/20.7/compilers/bin:/opt/nvidia/hpc_sdk/Linux_ppc64le/20.7/cuda/bin:/opt/nvidia/hpc_sdk/Linux_ppc64le/20.7/comm_libs/mpi/bin:$PATH''')

    @x86_64
    @ubuntu
    @docker
    def test_runtime_ubuntu(self):
        """Runtime"""
        n = nvhpc(eula=True, redist=['compilers/lib/*'])
        r = n.runtime()
        self.assertMultiLineEqual(r,
r'''# NVIDIA HPC SDK
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libatomic1 \
        libnuma1 \
        openssh-client && \
    rm -rf /var/lib/apt/lists/*
COPY --from=0 /opt/nvidia/hpc_sdk/Linux_x86_64/22.3/REDIST/compilers/lib/* /opt/nvidia/hpc_sdk/Linux_x86_64/22.3/compilers/lib/
COPY --from=0 /opt/nvidia/hpc_sdk/Linux_x86_64/22.3/comm_libs/mpi /opt/nvidia/hpc_sdk/Linux_x86_64/22.3/comm_libs/mpi
ENV LD_LIBRARY_PATH=/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/comm_libs/mpi/lib:/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/compilers/lib:$LD_LIBRARY_PATH \
    PATH=/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/comm_libs/mpi/bin:$PATH''')

    @x86_64
    @centos
    @docker
    def test_runtime_centos(self):
        """Runtime"""
        n = nvhpc(eula=True, mpi=False,
                  redist=['comm_libs/11.0/nccl/lib/libnccl.so',
                          'compilers/lib/*',
                          'math_libs/11.0/lib64/libcufft.so.10',
                          'math_libs/11.0/lib64/libcublas.so.11'])
        r = n.runtime()
        self.assertMultiLineEqual(r,
r'''# NVIDIA HPC SDK
RUN yum install -y \
        libatomic \
        numactl-libs \
        openssh-clients && \
    rm -rf /var/cache/yum/*
COPY --from=0 /opt/nvidia/hpc_sdk/Linux_x86_64/22.3/REDIST/comm_libs/11.0/nccl/lib/libnccl.so /opt/nvidia/hpc_sdk/Linux_x86_64/22.3/comm_libs/11.0/nccl/lib/libnccl.so
COPY --from=0 /opt/nvidia/hpc_sdk/Linux_x86_64/22.3/REDIST/compilers/lib/* /opt/nvidia/hpc_sdk/Linux_x86_64/22.3/compilers/lib/
COPY --from=0 /opt/nvidia/hpc_sdk/Linux_x86_64/22.3/REDIST/math_libs/11.0/lib64/libcufft.so.10 /opt/nvidia/hpc_sdk/Linux_x86_64/22.3/math_libs/11.0/lib64/libcufft.so.10
COPY --from=0 /opt/nvidia/hpc_sdk/Linux_x86_64/22.3/REDIST/math_libs/11.0/lib64/libcublas.so.11 /opt/nvidia/hpc_sdk/Linux_x86_64/22.3/math_libs/11.0/lib64/libcublas.so.11
ENV LD_LIBRARY_PATH=/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/comm_libs/11.0/nccl/lib:/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/compilers/lib:/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/math_libs/11.0/lib64:$LD_LIBRARY_PATH''')

    @x86_64
    @ubuntu
    @docker
    def test_makelocalrc(self):
        """makelocalrc"""
        tc = toolchain(CC='gcc-10', CXX='g++-10', F77='gfortran-10')
        n = nvhpc(eula=True, mpi=False, toolchain=tc, version='22.3')
        self.assertMultiLineEqual(str(n),
r'''# NVIDIA HPC SDK version 22.3
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ca-certificates && \
    rm -rf /var/lib/apt/lists/*
RUN echo "deb [trusted=yes] https://developer.download.nvidia.com/hpc-sdk/ubuntu/amd64 /" >> /etc/apt/sources.list.d/hpccm.list && \
    apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        nvhpc-22-3-cuda-multi && \
    rm -rf /var/lib/apt/lists/*
RUN /opt/nvidia/hpc_sdk/Linux_x86_64/22.3/compilers/bin/makelocalrc /opt/nvidia/hpc_sdk/Linux_x86_64/22.3/compilers/bin -x -gcc gcc-10 -gpp g++-10 -g77 gfortran-10
ENV CPATH=/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/comm_libs/nvshmem/include:/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/comm_libs/nccl/include:/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/compilers/extras/qd/include/qd:/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/math_libs/include:$CPATH \
    LD_LIBRARY_PATH=/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/comm_libs/nvshmem/lib:/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/comm_libs/nccl/lib:/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/math_libs/lib64:/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/compilers/lib:/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/cuda/lib64:$LD_LIBRARY_PATH \
    MANPATH=/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/compilers/man:$MANPATH \
    PATH=/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/comm_libs/nvshmem/bin:/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/comm_libs/nccl/bin:/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/profilers/bin:/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/compilers/bin:/opt/nvidia/hpc_sdk/Linux_x86_64/22.3/cuda/bin:$PATH''')

    def test_toolchain(self):
        """Toolchain"""
        n = nvhpc()
        tc = n.toolchain
        self.assertEqual(tc.CC, 'nvc')
        self.assertEqual(tc.CXX, 'nvc++')
        self.assertEqual(tc.FC, 'nvfortran')
        self.assertEqual(tc.F77, 'nvfortran')
        self.assertEqual(tc.F90, 'nvfortran')
