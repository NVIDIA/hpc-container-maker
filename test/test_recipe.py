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

"""Test cases for the recipe module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import os
import unittest

from hpccm.common import container_type
from hpccm.recipe import recipe

class Test_recipe(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    def test_no_arguments(self):
        """No arguments"""

        with self.assertRaises(TypeError):
            recipe()

    def test_bad_recipe(self):
        """Bad (invalid) recipe file"""
        path = os.path.dirname(__file__)
        rf = os.path.join(path, 'bad_recipe.py')
        with self.assertRaises(SystemExit):
            recipe(rf)

    def test_raise_exceptions(self):
        """Bad (invalid) recipe file with raise exceptions enabled"""
        path = os.path.dirname(__file__)
        rf = os.path.join(path, 'bad_recipe.py')
        with self.assertRaises(SyntaxError):
            recipe(rf, raise_exceptions=True)

    def test_basic_example(self):
        """Basic example"""
        path = os.path.dirname(__file__)
        rf = os.path.join(path, '..', 'recipes', 'examples', 'basic.py')
        r = recipe(rf)
        self.assertEqual(r.strip(),
r'''FROM ubuntu:16.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        g++ \
        gcc \
        gfortran && \
    rm -rf /var/lib/apt/lists/*''')

    def test_basic_example_singularity(self):
        """ctype option"""
        path = os.path.dirname(__file__)
        rf = os.path.join(path, '..', 'recipes', 'examples', 'basic.py')
        r = recipe(rf, ctype=container_type.SINGULARITY)
        self.assertEqual(r.strip(),
r'''BootStrap: docker
From: ubuntu:16.04
%post
    . /.singularity.d/env/10-docker*.sh

%post
    apt-get update -y
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        g++ \
        gcc \
        gfortran
    rm -rf /var/lib/apt/lists/*''')

    def test_multistage_example_singlestage(self):
        """Single_stage option"""
        path = os.path.dirname(__file__)
        rf = os.path.join(path, '..', 'recipes', 'examples', 'multistage.py')
        r = recipe(rf, single_stage=True)
        self.assertEqual(r.strip(),
r'''FROM nvidia/cuda:9.0-devel-ubuntu16.04 AS devel

# GNU compiler
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        g++ \
        gcc \
        gfortran && \
    rm -rf /var/lib/apt/lists/*

# FFTW version 3.3.8
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        file \
        make \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp ftp://ftp.fftw.org/pub/fftw/fftw-3.3.8.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/fftw-3.3.8.tar.gz -C /var/tmp -z && \
    cd /var/tmp/fftw-3.3.8 &&   ./configure --prefix=/usr/local/fftw --enable-openmp --enable-shared --enable-sse2 --enable-threads && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/fftw-3.3.8 /var/tmp/fftw-3.3.8.tar.gz
ENV LD_LIBRARY_PATH=/usr/local/fftw/lib:$LD_LIBRARY_PATH''')

    def test_multistage_example_singularity26(self):
        """Multi-stage recipe with Singularity container type"""
        path = os.path.dirname(__file__)
        rf = os.path.join(path, '..', 'recipes', 'examples', 'multistage.py')
        r = recipe(rf, ctype=container_type.SINGULARITY,
                   singularity_version='2.6')
        self.assertEqual(r.strip(),
r'''BootStrap: docker
From: nvidia/cuda:9.0-devel-ubuntu16.04
%post
    . /.singularity.d/env/10-docker*.sh

# GNU compiler
%post
    apt-get update -y
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        g++ \
        gcc \
        gfortran
    rm -rf /var/lib/apt/lists/*

# FFTW version 3.3.8
%post
    apt-get update -y
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        file \
        make \
        wget
    rm -rf /var/lib/apt/lists/*
%post
    cd /
    mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp ftp://ftp.fftw.org/pub/fftw/fftw-3.3.8.tar.gz
    mkdir -p /var/tmp && tar -x -f /var/tmp/fftw-3.3.8.tar.gz -C /var/tmp -z
    cd /var/tmp/fftw-3.3.8 &&   ./configure --prefix=/usr/local/fftw --enable-openmp --enable-shared --enable-sse2 --enable-threads
    make -j$(nproc)
    make -j$(nproc) install
    rm -rf /var/tmp/fftw-3.3.8 /var/tmp/fftw-3.3.8.tar.gz
%environment
    export LD_LIBRARY_PATH=/usr/local/fftw/lib:$LD_LIBRARY_PATH
%post
    export LD_LIBRARY_PATH=/usr/local/fftw/lib:$LD_LIBRARY_PATH''')

    def test_multistage_example_singularity32(self):
        """Multi-stage recipe with Singularity container type"""
        path = os.path.dirname(__file__)
        rf = os.path.join(path, '..', 'recipes', 'examples', 'multistage.py')
        r = recipe(rf, ctype=container_type.SINGULARITY,
                   singularity_version='3.2')
        self.maxDiff = None
        self.assertEqual(r.strip(),
r'''# NOTE: this definition file depends on features only available in
# Singularity 3.2 and later.
BootStrap: docker
From: nvidia/cuda:9.0-devel-ubuntu16.04
Stage: devel
%post
    . /.singularity.d/env/10-docker*.sh

# GNU compiler
%post
    apt-get update -y
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        g++ \
        gcc \
        gfortran
    rm -rf /var/lib/apt/lists/*

# FFTW version 3.3.8
%post
    apt-get update -y
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        file \
        make \
        wget
    rm -rf /var/lib/apt/lists/*
%post
    cd /
    mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp ftp://ftp.fftw.org/pub/fftw/fftw-3.3.8.tar.gz
    mkdir -p /var/tmp && tar -x -f /var/tmp/fftw-3.3.8.tar.gz -C /var/tmp -z
    cd /var/tmp/fftw-3.3.8 &&   ./configure --prefix=/usr/local/fftw --enable-openmp --enable-shared --enable-sse2 --enable-threads
    make -j$(nproc)
    make -j$(nproc) install
    rm -rf /var/tmp/fftw-3.3.8 /var/tmp/fftw-3.3.8.tar.gz
%environment
    export LD_LIBRARY_PATH=/usr/local/fftw/lib:$LD_LIBRARY_PATH
%post
    export LD_LIBRARY_PATH=/usr/local/fftw/lib:$LD_LIBRARY_PATH

BootStrap: docker
From: nvidia/cuda:9.0-runtime-ubuntu16.04
%post
    . /.singularity.d/env/10-docker*.sh

# GNU compiler runtime
%post
    apt-get update -y
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libgfortran3 \
        libgomp1
    rm -rf /var/lib/apt/lists/*

# FFTW
%files from devel
    /usr/local/fftw /usr/local/fftw
%environment
    export LD_LIBRARY_PATH=/usr/local/fftw/lib:$LD_LIBRARY_PATH
%post
    export LD_LIBRARY_PATH=/usr/local/fftw/lib:$LD_LIBRARY_PATH''')

    def test_userarg_example(self):
        """userarg option"""
        path = os.path.dirname(__file__)
        rf = os.path.join(path, '..', 'recipes', 'examples', 'userargs.py')
        r = recipe(rf, userarg={'cuda': '9.0', 'ompi': '2.1.2'})
        self.assertEqual(r.strip(),
r'''FROM nvidia/cuda:9.0-devel-ubuntu16.04

# OpenMPI version 2.1.2
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        bzip2 \
        file \
        hwloc \
        libnuma-dev \
        make \
        openssh-client \
        perl \
        tar \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://www.open-mpi.org/software/ompi/v2.1/downloads/openmpi-2.1.2.tar.bz2 && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/openmpi-2.1.2.tar.bz2 -C /var/tmp -j && \
    cd /var/tmp/openmpi-2.1.2 &&   ./configure --prefix=/usr/local/openmpi --disable-getpwuid --enable-orterun-prefix-by-default --with-cuda --without-verbs && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/openmpi-2.1.2 /var/tmp/openmpi-2.1.2.tar.bz2
ENV LD_LIBRARY_PATH=/usr/local/openmpi/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/openmpi/bin:$PATH''')

    def test_include(self):
        """recipe include"""
        path = os.path.dirname(__file__)
        rf = os.path.join(path, 'include3.py')
        r = recipe(rf)
        self.assertEqual(r.strip(),
r'''FROM ubuntu:16.04

# GNU compiler
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        g++ \
        gcc \
        gfortran && \
    rm -rf /var/lib/apt/lists/*''')
