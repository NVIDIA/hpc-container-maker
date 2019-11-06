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

"""Test cases for the pgi module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import centos, docker, ppc64le, ubuntu, x86_64

from hpccm.building_blocks.pgi import pgi

class Test_pgi(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @x86_64
    @ubuntu
    @docker
    def test_defaults_ubuntu(self):
        """Default pgi building block"""
        p = pgi()
        self.assertEqual(str(p),
r'''# PGI compiler version 19.10
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        g++ \
        gcc \
        libnuma1 \
        perl \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -O /var/tmp/pgi-community-linux-x64-latest.tar.gz --referer https://www.pgroup.com/products/community.htm?utm_source=hpccm\&utm_medium=wgt\&utm_campaign=CE\&nvid=nv-int-14-39155 -P /var/tmp https://www.pgroup.com/support/downloader.php?file=pgi-community-linux-x64 && \
    mkdir -p /var/tmp/pgi && tar -x -f /var/tmp/pgi-community-linux-x64-latest.tar.gz -C /var/tmp/pgi -z && \
    cd /var/tmp/pgi && PGI_ACCEPT_EULA=decline PGI_INSTALL_DIR=/opt/pgi PGI_INSTALL_MPI=false PGI_INSTALL_NVIDIA=true PGI_MPI_GPU_SUPPORT=false PGI_SILENT=false ./install && \
    echo "variable LIBRARY_PATH is environment(LIBRARY_PATH);" >> /opt/pgi/linux86-64/19.10/bin/siterc && \
    echo "variable library_path is default(\$if(\$LIBRARY_PATH,\$foreach(ll,\$replace(\$LIBRARY_PATH,":",), -L\$ll)));" >> /opt/pgi/linux86-64/19.10/bin/siterc && \
    echo "append LDLIBARGS=\$library_path;" >> /opt/pgi/linux86-64/19.10/bin/siterc && \
    ln -sf /usr/lib/x86_64-linux-gnu/libnuma.so.1 /opt/pgi/linux86-64/19.10/lib/libnuma.so && \
    ln -sf /usr/lib/x86_64-linux-gnu/libnuma.so.1 /opt/pgi/linux86-64/19.10/lib/libnuma.so.1 && \
    rm -rf /var/tmp/pgi-community-linux-x64-latest.tar.gz /var/tmp/pgi
ENV LD_LIBRARY_PATH=/opt/pgi/linux86-64/19.10/lib:$LD_LIBRARY_PATH \
    PATH=/opt/pgi/linux86-64/19.10/bin:$PATH''')

    @x86_64
    @centos
    @docker
    def test_defaults_centos(self):
        """Default pgi building block"""
        p = pgi()
        self.assertEqual(str(p),
r'''# PGI compiler version 19.10
RUN yum install -y \
        gcc \
        gcc-c++ \
        numactl-libs \
        perl \
        wget && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -O /var/tmp/pgi-community-linux-x64-latest.tar.gz --referer https://www.pgroup.com/products/community.htm?utm_source=hpccm\&utm_medium=wgt\&utm_campaign=CE\&nvid=nv-int-14-39155 -P /var/tmp https://www.pgroup.com/support/downloader.php?file=pgi-community-linux-x64 && \
    mkdir -p /var/tmp/pgi && tar -x -f /var/tmp/pgi-community-linux-x64-latest.tar.gz -C /var/tmp/pgi -z && \
    cd /var/tmp/pgi && PGI_ACCEPT_EULA=decline PGI_INSTALL_DIR=/opt/pgi PGI_INSTALL_MPI=false PGI_INSTALL_NVIDIA=true PGI_MPI_GPU_SUPPORT=false PGI_SILENT=false ./install && \
    echo "variable LIBRARY_PATH is environment(LIBRARY_PATH);" >> /opt/pgi/linux86-64/19.10/bin/siterc && \
    echo "variable library_path is default(\$if(\$LIBRARY_PATH,\$foreach(ll,\$replace(\$LIBRARY_PATH,":",), -L\$ll)));" >> /opt/pgi/linux86-64/19.10/bin/siterc && \
    echo "append LDLIBARGS=\$library_path;" >> /opt/pgi/linux86-64/19.10/bin/siterc && \
    ln -sf /usr/lib64/libnuma.so.1 /opt/pgi/linux86-64/19.10/lib/libnuma.so && \
    ln -sf /usr/lib64/libnuma.so.1 /opt/pgi/linux86-64/19.10/lib/libnuma.so.1 && \
    rm -rf /var/tmp/pgi-community-linux-x64-latest.tar.gz /var/tmp/pgi
ENV LD_LIBRARY_PATH=/opt/pgi/linux86-64/19.10/lib:$LD_LIBRARY_PATH \
    PATH=/opt/pgi/linux86-64/19.10/bin:$PATH''')

    @x86_64
    @ubuntu
    @docker
    def test_eula(self):
        """Accept EULA"""
        p = pgi(eula=True)
        self.assertEqual(str(p),
r'''# PGI compiler version 19.10
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        g++ \
        gcc \
        libnuma1 \
        perl \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -O /var/tmp/pgi-community-linux-x64-latest.tar.gz --referer https://www.pgroup.com/products/community.htm?utm_source=hpccm\&utm_medium=wgt\&utm_campaign=CE\&nvid=nv-int-14-39155 -P /var/tmp https://www.pgroup.com/support/downloader.php?file=pgi-community-linux-x64 && \
    mkdir -p /var/tmp/pgi && tar -x -f /var/tmp/pgi-community-linux-x64-latest.tar.gz -C /var/tmp/pgi -z && \
    cd /var/tmp/pgi && PGI_ACCEPT_EULA=accept PGI_INSTALL_DIR=/opt/pgi PGI_INSTALL_MPI=false PGI_INSTALL_NVIDIA=true PGI_MPI_GPU_SUPPORT=false PGI_SILENT=true ./install && \
    echo "variable LIBRARY_PATH is environment(LIBRARY_PATH);" >> /opt/pgi/linux86-64/19.10/bin/siterc && \
    echo "variable library_path is default(\$if(\$LIBRARY_PATH,\$foreach(ll,\$replace(\$LIBRARY_PATH,":",), -L\$ll)));" >> /opt/pgi/linux86-64/19.10/bin/siterc && \
    echo "append LDLIBARGS=\$library_path;" >> /opt/pgi/linux86-64/19.10/bin/siterc && \
    ln -sf /usr/lib/x86_64-linux-gnu/libnuma.so.1 /opt/pgi/linux86-64/19.10/lib/libnuma.so && \
    ln -sf /usr/lib/x86_64-linux-gnu/libnuma.so.1 /opt/pgi/linux86-64/19.10/lib/libnuma.so.1 && \
    rm -rf /var/tmp/pgi-community-linux-x64-latest.tar.gz /var/tmp/pgi
ENV LD_LIBRARY_PATH=/opt/pgi/linux86-64/19.10/lib:$LD_LIBRARY_PATH \
    PATH=/opt/pgi/linux86-64/19.10/bin:$PATH''')

    @x86_64
    @ubuntu
    @docker
    def test_tarball(self):
        """tarball"""
        p = pgi(eula=True, tarball='pgilinux-2017-1710-x86_64.tar.gz')
        self.assertEqual(str(p),
r'''# PGI compiler version 17.10
COPY pgilinux-2017-1710-x86_64.tar.gz /var/tmp/pgilinux-2017-1710-x86_64.tar.gz
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        g++ \
        gcc \
        libnuma1 \
        perl && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp/pgi && tar -x -f /var/tmp/pgilinux-2017-1710-x86_64.tar.gz -C /var/tmp/pgi -z && \
    cd /var/tmp/pgi && PGI_ACCEPT_EULA=accept PGI_INSTALL_DIR=/opt/pgi PGI_INSTALL_MPI=false PGI_INSTALL_NVIDIA=true PGI_MPI_GPU_SUPPORT=false PGI_SILENT=true ./install && \
    echo "variable LIBRARY_PATH is environment(LIBRARY_PATH);" >> /opt/pgi/linux86-64/17.10/bin/siterc && \
    echo "variable library_path is default(\$if(\$LIBRARY_PATH,\$foreach(ll,\$replace(\$LIBRARY_PATH,":",), -L\$ll)));" >> /opt/pgi/linux86-64/17.10/bin/siterc && \
    echo "append LDLIBARGS=\$library_path;" >> /opt/pgi/linux86-64/17.10/bin/siterc && \
    ln -sf /usr/lib/x86_64-linux-gnu/libnuma.so.1 /opt/pgi/linux86-64/17.10/lib/libnuma.so && \
    ln -sf /usr/lib/x86_64-linux-gnu/libnuma.so.1 /opt/pgi/linux86-64/17.10/lib/libnuma.so.1 && \
    rm -rf /var/tmp/pgilinux-2017-1710-x86_64.tar.gz /var/tmp/pgi
ENV LD_LIBRARY_PATH=/opt/pgi/linux86-64/17.10/lib:$LD_LIBRARY_PATH \
    PATH=/opt/pgi/linux86-64/17.10/bin:$PATH''')

    @x86_64
    @ubuntu
    @docker
    def test_tarball2(self):
        """tarball"""
        p = pgi(eula=True, tarball='pkg/pgilinux-2018-1804-x86_64.tar.gz')
        self.assertEqual(str(p),
r'''# PGI compiler version 18.4
COPY pkg/pgilinux-2018-1804-x86_64.tar.gz /var/tmp/pgilinux-2018-1804-x86_64.tar.gz
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        g++ \
        gcc \
        libnuma1 \
        perl && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp/pgi && tar -x -f /var/tmp/pgilinux-2018-1804-x86_64.tar.gz -C /var/tmp/pgi -z && \
    cd /var/tmp/pgi && PGI_ACCEPT_EULA=accept PGI_INSTALL_DIR=/opt/pgi PGI_INSTALL_MPI=false PGI_INSTALL_NVIDIA=true PGI_MPI_GPU_SUPPORT=false PGI_SILENT=true ./install && \
    echo "variable LIBRARY_PATH is environment(LIBRARY_PATH);" >> /opt/pgi/linux86-64/18.4/bin/siterc && \
    echo "variable library_path is default(\$if(\$LIBRARY_PATH,\$foreach(ll,\$replace(\$LIBRARY_PATH,":",), -L\$ll)));" >> /opt/pgi/linux86-64/18.4/bin/siterc && \
    echo "append LDLIBARGS=\$library_path;" >> /opt/pgi/linux86-64/18.4/bin/siterc && \
    ln -sf /usr/lib/x86_64-linux-gnu/libnuma.so.1 /opt/pgi/linux86-64/18.4/lib/libnuma.so && \
    ln -sf /usr/lib/x86_64-linux-gnu/libnuma.so.1 /opt/pgi/linux86-64/18.4/lib/libnuma.so.1 && \
    rm -rf /var/tmp/pgilinux-2018-1804-x86_64.tar.gz /var/tmp/pgi
ENV LD_LIBRARY_PATH=/opt/pgi/linux86-64/18.4/lib:$LD_LIBRARY_PATH \
    PATH=/opt/pgi/linux86-64/18.4/bin:$PATH''')

    @x86_64
    @ubuntu
    @docker
    def test_tarball_no_leading_zero(self):
        """tarball"""
        p = pgi(eula=True, tarball='pgilinux-2018-184-x86_64.tar.gz')
        self.assertEqual(str(p),
r'''# PGI compiler version 18.4
COPY pgilinux-2018-184-x86_64.tar.gz /var/tmp/pgilinux-2018-184-x86_64.tar.gz
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        g++ \
        gcc \
        libnuma1 \
        perl && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp/pgi && tar -x -f /var/tmp/pgilinux-2018-184-x86_64.tar.gz -C /var/tmp/pgi -z && \
    cd /var/tmp/pgi && PGI_ACCEPT_EULA=accept PGI_INSTALL_DIR=/opt/pgi PGI_INSTALL_MPI=false PGI_INSTALL_NVIDIA=true PGI_MPI_GPU_SUPPORT=false PGI_SILENT=true ./install && \
    echo "variable LIBRARY_PATH is environment(LIBRARY_PATH);" >> /opt/pgi/linux86-64/18.4/bin/siterc && \
    echo "variable library_path is default(\$if(\$LIBRARY_PATH,\$foreach(ll,\$replace(\$LIBRARY_PATH,":",), -L\$ll)));" >> /opt/pgi/linux86-64/18.4/bin/siterc && \
    echo "append LDLIBARGS=\$library_path;" >> /opt/pgi/linux86-64/18.4/bin/siterc && \
    ln -sf /usr/lib/x86_64-linux-gnu/libnuma.so.1 /opt/pgi/linux86-64/18.4/lib/libnuma.so && \
    ln -sf /usr/lib/x86_64-linux-gnu/libnuma.so.1 /opt/pgi/linux86-64/18.4/lib/libnuma.so.1 && \
    rm -rf /var/tmp/pgilinux-2018-184-x86_64.tar.gz /var/tmp/pgi
ENV LD_LIBRARY_PATH=/opt/pgi/linux86-64/18.4/lib:$LD_LIBRARY_PATH \
    PATH=/opt/pgi/linux86-64/18.4/bin:$PATH''')

    @x86_64
    @ubuntu
    @docker
    def test_system_cuda(self):
        """System CUDA"""
        p = pgi(eula=True, system_cuda=True)
        self.assertEqual(str(p),
r'''# PGI compiler version 19.10
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        g++ \
        gcc \
        libnuma1 \
        perl \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -O /var/tmp/pgi-community-linux-x64-latest.tar.gz --referer https://www.pgroup.com/products/community.htm?utm_source=hpccm\&utm_medium=wgt\&utm_campaign=CE\&nvid=nv-int-14-39155 -P /var/tmp https://www.pgroup.com/support/downloader.php?file=pgi-community-linux-x64 && \
    mkdir -p /var/tmp/pgi && tar -x -f /var/tmp/pgi-community-linux-x64-latest.tar.gz -C /var/tmp/pgi -z && \
    cd /var/tmp/pgi && PGI_ACCEPT_EULA=accept PGI_INSTALL_DIR=/opt/pgi PGI_INSTALL_MPI=false PGI_INSTALL_NVIDIA=false PGI_MPI_GPU_SUPPORT=false PGI_SILENT=true ./install && \
    echo "set CUDAROOT=/usr/local/cuda;" >> /opt/pgi/linux86-64/19.10/bin/siterc && \
    echo "variable LIBRARY_PATH is environment(LIBRARY_PATH);" >> /opt/pgi/linux86-64/19.10/bin/siterc && \
    echo "variable library_path is default(\$if(\$LIBRARY_PATH,\$foreach(ll,\$replace(\$LIBRARY_PATH,":",), -L\$ll)));" >> /opt/pgi/linux86-64/19.10/bin/siterc && \
    echo "append LDLIBARGS=\$library_path;" >> /opt/pgi/linux86-64/19.10/bin/siterc && \
    ln -sf /usr/lib/x86_64-linux-gnu/libnuma.so.1 /opt/pgi/linux86-64/19.10/lib/libnuma.so && \
    ln -sf /usr/lib/x86_64-linux-gnu/libnuma.so.1 /opt/pgi/linux86-64/19.10/lib/libnuma.so.1 && \
    rm -rf /var/tmp/pgi-community-linux-x64-latest.tar.gz /var/tmp/pgi
ENV LD_LIBRARY_PATH=/opt/pgi/linux86-64/19.10/lib:$LD_LIBRARY_PATH \
    PATH=/opt/pgi/linux86-64/19.10/bin:$PATH''')

    @x86_64
    @ubuntu
    @docker
    def test_mpi(self):
        """System CUDA"""
        p = pgi(eula=True, mpi=True)
        self.assertEqual(str(p),
r'''# PGI compiler version 19.10
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        g++ \
        gcc \
        libnuma1 \
        openssh-client \
        perl \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -O /var/tmp/pgi-community-linux-x64-latest.tar.gz --referer https://www.pgroup.com/products/community.htm?utm_source=hpccm\&utm_medium=wgt\&utm_campaign=CE\&nvid=nv-int-14-39155 -P /var/tmp https://www.pgroup.com/support/downloader.php?file=pgi-community-linux-x64 && \
    mkdir -p /var/tmp/pgi && tar -x -f /var/tmp/pgi-community-linux-x64-latest.tar.gz -C /var/tmp/pgi -z && \
    cd /var/tmp/pgi && PGI_ACCEPT_EULA=accept PGI_INSTALL_DIR=/opt/pgi PGI_INSTALL_MPI=true PGI_INSTALL_NVIDIA=true PGI_MPI_GPU_SUPPORT=true PGI_SILENT=true ./install && \
    echo "variable LIBRARY_PATH is environment(LIBRARY_PATH);" >> /opt/pgi/linux86-64/19.10/bin/siterc && \
    echo "variable library_path is default(\$if(\$LIBRARY_PATH,\$foreach(ll,\$replace(\$LIBRARY_PATH,":",), -L\$ll)));" >> /opt/pgi/linux86-64/19.10/bin/siterc && \
    echo "append LDLIBARGS=\$library_path;" >> /opt/pgi/linux86-64/19.10/bin/siterc && \
    ln -sf /usr/lib/x86_64-linux-gnu/libnuma.so.1 /opt/pgi/linux86-64/19.10/lib/libnuma.so && \
    ln -sf /usr/lib/x86_64-linux-gnu/libnuma.so.1 /opt/pgi/linux86-64/19.10/lib/libnuma.so.1 && \
    rm -rf /var/tmp/pgi-community-linux-x64-latest.tar.gz /var/tmp/pgi
ENV LD_LIBRARY_PATH=/opt/pgi/linux86-64/19.10/mpi/openmpi-3.1.3/lib:/opt/pgi/linux86-64/19.10/lib:$LD_LIBRARY_PATH \
    PATH=/opt/pgi/linux86-64/19.10/mpi/openmpi-3.1.3/bin:/opt/pgi/linux86-64/19.10/bin:$PATH''')

    @x86_64
    @ubuntu
    @docker
    def test_extended_environment(self):
        """Extended environment without MPI"""
        p = pgi(eula=True, extended_environment=True, mpi=False)
        self.assertEqual(str(p),
r'''# PGI compiler version 19.10
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        g++ \
        gcc \
        libnuma1 \
        perl \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -O /var/tmp/pgi-community-linux-x64-latest.tar.gz --referer https://www.pgroup.com/products/community.htm?utm_source=hpccm\&utm_medium=wgt\&utm_campaign=CE\&nvid=nv-int-14-39155 -P /var/tmp https://www.pgroup.com/support/downloader.php?file=pgi-community-linux-x64 && \
    mkdir -p /var/tmp/pgi && tar -x -f /var/tmp/pgi-community-linux-x64-latest.tar.gz -C /var/tmp/pgi -z && \
    cd /var/tmp/pgi && PGI_ACCEPT_EULA=accept PGI_INSTALL_DIR=/opt/pgi PGI_INSTALL_MPI=false PGI_INSTALL_NVIDIA=true PGI_MPI_GPU_SUPPORT=false PGI_SILENT=true ./install && \
    echo "variable LIBRARY_PATH is environment(LIBRARY_PATH);" >> /opt/pgi/linux86-64/19.10/bin/siterc && \
    echo "variable library_path is default(\$if(\$LIBRARY_PATH,\$foreach(ll,\$replace(\$LIBRARY_PATH,":",), -L\$ll)));" >> /opt/pgi/linux86-64/19.10/bin/siterc && \
    echo "append LDLIBARGS=\$library_path;" >> /opt/pgi/linux86-64/19.10/bin/siterc && \
    ln -sf /usr/lib/x86_64-linux-gnu/libnuma.so.1 /opt/pgi/linux86-64/19.10/lib/libnuma.so && \
    ln -sf /usr/lib/x86_64-linux-gnu/libnuma.so.1 /opt/pgi/linux86-64/19.10/lib/libnuma.so.1 && \
    rm -rf /var/tmp/pgi-community-linux-x64-latest.tar.gz /var/tmp/pgi
ENV CC=/opt/pgi/linux86-64/19.10/bin/pgcc \
    CPP="/opt/pgi/linux86-64/19.10/bin/pgcc -Mcpp" \
    CXX=/opt/pgi/linux86-64/19.10/bin/pgc++ \
    F77=/opt/pgi/linux86-64/19.10/bin/pgf77 \
    F90=/opt/pgi/linux86-64/19.10/bin/pgf90 \
    FC=/opt/pgi/linux86-64/19.10/bin/pgfortran \
    LD_LIBRARY_PATH=/opt/pgi/linux86-64/19.10/lib:$LD_LIBRARY_PATH \
    MODULEPATH=/opt/pgi/modulefiles:$MODULEPATH \
    PATH=/opt/pgi/linux86-64/19.10/bin:$PATH''')

    @x86_64
    @ubuntu
    @docker
    def test_extended_environment_mpi(self):
        """Extended environment with MPI"""
        p = pgi(eula=True, extended_environment=True, mpi=True)
        self.assertEqual(str(p),
r'''# PGI compiler version 19.10
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        g++ \
        gcc \
        libnuma1 \
        openssh-client \
        perl \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -O /var/tmp/pgi-community-linux-x64-latest.tar.gz --referer https://www.pgroup.com/products/community.htm?utm_source=hpccm\&utm_medium=wgt\&utm_campaign=CE\&nvid=nv-int-14-39155 -P /var/tmp https://www.pgroup.com/support/downloader.php?file=pgi-community-linux-x64 && \
    mkdir -p /var/tmp/pgi && tar -x -f /var/tmp/pgi-community-linux-x64-latest.tar.gz -C /var/tmp/pgi -z && \
    cd /var/tmp/pgi && PGI_ACCEPT_EULA=accept PGI_INSTALL_DIR=/opt/pgi PGI_INSTALL_MPI=true PGI_INSTALL_NVIDIA=true PGI_MPI_GPU_SUPPORT=true PGI_SILENT=true ./install && \
    echo "variable LIBRARY_PATH is environment(LIBRARY_PATH);" >> /opt/pgi/linux86-64/19.10/bin/siterc && \
    echo "variable library_path is default(\$if(\$LIBRARY_PATH,\$foreach(ll,\$replace(\$LIBRARY_PATH,":",), -L\$ll)));" >> /opt/pgi/linux86-64/19.10/bin/siterc && \
    echo "append LDLIBARGS=\$library_path;" >> /opt/pgi/linux86-64/19.10/bin/siterc && \
    ln -sf /usr/lib/x86_64-linux-gnu/libnuma.so.1 /opt/pgi/linux86-64/19.10/lib/libnuma.so && \
    ln -sf /usr/lib/x86_64-linux-gnu/libnuma.so.1 /opt/pgi/linux86-64/19.10/lib/libnuma.so.1 && \
    rm -rf /var/tmp/pgi-community-linux-x64-latest.tar.gz /var/tmp/pgi
ENV CC=/opt/pgi/linux86-64/19.10/bin/pgcc \
    CPP="/opt/pgi/linux86-64/19.10/bin/pgcc -Mcpp" \
    CXX=/opt/pgi/linux86-64/19.10/bin/pgc++ \
    F77=/opt/pgi/linux86-64/19.10/bin/pgf77 \
    F90=/opt/pgi/linux86-64/19.10/bin/pgf90 \
    FC=/opt/pgi/linux86-64/19.10/bin/pgfortran \
    LD_LIBRARY_PATH=/opt/pgi/linux86-64/19.10/mpi/openmpi-3.1.3/lib:/opt/pgi/linux86-64/19.10/lib:$LD_LIBRARY_PATH \
    MODULEPATH=/opt/pgi/modulefiles:$MODULEPATH \
    PATH=/opt/pgi/linux86-64/19.10/mpi/openmpi-3.1.3/bin:/opt/pgi/linux86-64/19.10/bin:$PATH \
    PGI_OPTL_INCLUDE_DIRS=/opt/pgi/linux86-64/19.10/mpi/openmpi-3.1.3/include \
    PGI_OPTL_LIB_DIRS=/opt/pgi/linux86-64/19.10/mpi/openmpi-3.1.3/lib''')

    @ppc64le
    @centos
    @docker
    def test_ppc64le(self):
        """Default PGI building block on ppc64le"""
        p = pgi(eula=True)
        self.assertEqual(str(p),
r'''# PGI compiler version 19.10
RUN yum install -y \
        gcc \
        gcc-c++ \
        numactl-libs \
        perl \
        wget && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -O /var/tmp/pgi-community-linux-openpower-latest.tar.gz --referer https://www.pgroup.com/products/community.htm?utm_source=hpccm\&utm_medium=wgt\&utm_campaign=CE\&nvid=nv-int-14-39155 -P /var/tmp https://www.pgroup.com/support/downloader.php?file=pgi-community-linux-openpower && \
    mkdir -p /var/tmp/pgi && tar -x -f /var/tmp/pgi-community-linux-openpower-latest.tar.gz -C /var/tmp/pgi -z && \
    cd /var/tmp/pgi && PGI_ACCEPT_EULA=accept PGI_INSTALL_DIR=/opt/pgi PGI_INSTALL_MPI=false PGI_INSTALL_NVIDIA=true PGI_MPI_GPU_SUPPORT=false PGI_SILENT=true ./install && \
    echo "variable LIBRARY_PATH is environment(LIBRARY_PATH);" >> /opt/pgi/linuxpower/19.10/bin/siterc && \
    echo "variable library_path is default(\$if(\$LIBRARY_PATH,\$foreach(ll,\$replace(\$LIBRARY_PATH,":",), -L\$ll)));" >> /opt/pgi/linuxpower/19.10/bin/siterc && \
    echo "append LDLIBARGS=\$library_path;" >> /opt/pgi/linuxpower/19.10/bin/siterc && \
    ln -sf /usr/lib64/libnuma.so.1 /opt/pgi/linuxpower/19.10/lib/libnuma.so && \
    ln -sf /usr/lib64/libnuma.so.1 /opt/pgi/linuxpower/19.10/lib/libnuma.so.1 && \
    rm -rf /var/tmp/pgi-community-linux-openpower-latest.tar.gz /var/tmp/pgi
ENV LD_LIBRARY_PATH=/opt/pgi/linuxpower/19.10/lib:$LD_LIBRARY_PATH \
    PATH=/opt/pgi/linuxpower/19.10/bin:$PATH''')

    @x86_64
    @ubuntu
    @docker
    def test_runtime_ubuntu(self):
        """Runtime"""
        p = pgi()
        r = p.runtime()
        self.assertEqual(r,
r'''# PGI compiler
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libnuma1 && \
    rm -rf /var/lib/apt/lists/*
COPY --from=0 /opt/pgi/linux86-64-llvm/19.10/REDIST/*.so* /opt/pgi/linux86-64/19.10/lib/
RUN ln -sf /usr/lib/x86_64-linux-gnu/libnuma.so.1 /opt/pgi/linux86-64/19.10/lib/libnuma.so && \
    ln -sf /usr/lib/x86_64-linux-gnu/libnuma.so.1 /opt/pgi/linux86-64/19.10/lib/libnuma.so.1
ENV LD_LIBRARY_PATH=/opt/pgi/linux86-64/19.10/lib:$LD_LIBRARY_PATH''')

    @x86_64
    @centos
    @docker
    def test_runtime_centos(self):
        """Runtime"""
        p = pgi()
        r = p.runtime()
        self.assertEqual(r,
r'''# PGI compiler
RUN yum install -y \
        numactl-libs && \
    rm -rf /var/cache/yum/*
COPY --from=0 /opt/pgi/linux86-64-llvm/19.10/REDIST/*.so* /opt/pgi/linux86-64/19.10/lib/
RUN ln -sf /usr/lib64/libnuma.so.1 /opt/pgi/linux86-64/19.10/lib/libnuma.so && \
    ln -sf /usr/lib64/libnuma.so.1 /opt/pgi/linux86-64/19.10/lib/libnuma.so.1
ENV LD_LIBRARY_PATH=/opt/pgi/linux86-64/19.10/lib:$LD_LIBRARY_PATH''')

    @x86_64
    @centos
    @docker
    def test_runtime_mpi_centos(self):
        """Runtime"""
        p = pgi(mpi=True)
        r = p.runtime()
        self.assertEqual(r,
r'''# PGI compiler
RUN yum install -y \
        numactl-libs \
        openssh-clients && \
    rm -rf /var/cache/yum/*
COPY --from=0 /opt/pgi/linux86-64-llvm/19.10/REDIST/*.so* /opt/pgi/linux86-64/19.10/lib/
COPY --from=0 /opt/pgi/linux86-64/19.10/mpi/openmpi-3.1.3 /opt/pgi/linux86-64/19.10/mpi/openmpi-3.1.3
RUN ln -sf /usr/lib64/libnuma.so.1 /opt/pgi/linux86-64/19.10/lib/libnuma.so && \
    ln -sf /usr/lib64/libnuma.so.1 /opt/pgi/linux86-64/19.10/lib/libnuma.so.1
ENV LD_LIBRARY_PATH=/opt/pgi/linux86-64/19.10/mpi/openmpi-3.1.3/lib:/opt/pgi/linux86-64/19.10/lib:$LD_LIBRARY_PATH \
    PATH=/opt/pgi/linux86-64/19.10/mpi/openmpi-3.1.3/bin:$PATH''')

    def test_toolchain(self):
        """Toolchain"""
        p = pgi()
        tc = p.toolchain
        self.assertEqual(tc.CC, 'pgcc')
        self.assertEqual(tc.CXX, 'pgc++')
        self.assertEqual(tc.FC, 'pgfortran')
        self.assertEqual(tc.F77, 'pgfortran')
        self.assertEqual(tc.F90, 'pgfortran')
