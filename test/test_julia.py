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

"""Test cases for the julia module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import aarch64, centos, docker, ubuntu, x86_64

from hpccm.building_blocks.julia import julia

class Test_julia(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @x86_64
    @ubuntu
    @docker
    def test_defaults_ubuntu(self):
        """Default julia building block"""
        j = julia()
        self.assertEqual(str(j),
r'''# Julia version 1.3.1
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        tar \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://julialang-s3.julialang.org/bin/linux/x64/1.3/julia-1.3.1-linux-x86_64.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/julia-1.3.1-linux-x86_64.tar.gz -C /var/tmp -z && \
    cp -a /var/tmp/julia-1.3.1 /usr/local/julia && \
    rm -rf /var/tmp/julia-1.3.1-linux-x86_64.tar.gz /var/tmp/julia-1.3.1
ENV LD_LIBRARY_PATH=/usr/local/julia/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/julia/bin:$PATH''')

    @aarch64
    @ubuntu
    @docker
    def test_aarch64(self):
        """aarch64"""
        j = julia()
        self.assertEqual(str(j),
r'''# Julia version 1.3.1
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        tar \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://julialang-s3.julialang.org/bin/linux/aarch64/1.3/julia-1.3.1-linux-aarch64.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/julia-1.3.1-linux-aarch64.tar.gz -C /var/tmp -z && \
    cp -a /var/tmp/julia-1.3.1 /usr/local/julia && \
    rm -rf /var/tmp/julia-1.3.1-linux-aarch64.tar.gz /var/tmp/julia-1.3.1
ENV LD_LIBRARY_PATH=/usr/local/julia/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/julia/bin:$PATH''')

    @x86_64
    @ubuntu
    @docker
    def test_depot_history_packages(self):
        """depot, history, and packages options"""
        j = julia(depot='~/.julia-ngc', history='/tmp/julia_history.jl',
                  packages=['CUDAnative', 'CuArrays'],
                  version='1.2.0')
        self.assertEqual(str(j),
r'''# Julia version 1.2.0
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        tar \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://julialang-s3.julialang.org/bin/linux/x64/1.2/julia-1.2.0-linux-x86_64.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/julia-1.2.0-linux-x86_64.tar.gz -C /var/tmp -z && \
    cp -a /var/tmp/julia-1.2.0 /usr/local/julia && \
    JULIA_DEPOT_PATH=/usr/local/julia/share/julia /usr/local/julia/bin/julia -e 'using Pkg; Pkg.add([PackageSpec(name="CUDAnative"), PackageSpec(name="CuArrays")])' && \
    echo "DEPOT_PATH[1] = \"~/.julia-ngc\"" >> /usr/local/julia/etc/julia/startup.jl && \
    rm -rf /var/tmp/julia-1.2.0-linux-x86_64.tar.gz /var/tmp/julia-1.2.0
ENV JULIA_HISTORY=/tmp/julia_history.jl \
    LD_LIBRARY_PATH=/usr/local/julia/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/julia/bin:$PATH''')

    @x86_64
    @ubuntu
    @docker
    def test_cuda_ldconfig(self):
        """cuda and ldconfig options"""
        j = julia(cuda=True, ldconfig=True, version='1.2.0')
        self.assertEqual(str(j),
r'''# Julia version 1.2.0
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        tar \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://julialang-s3.julialang.org/bin/linux/x64/1.2/julia-1.2.0-linux-x86_64.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/julia-1.2.0-linux-x86_64.tar.gz -C /var/tmp -z && \
    cp -a /var/tmp/julia-1.2.0 /usr/local/julia && \
    JULIA_DEPOT_PATH=/usr/local/julia/share/julia /usr/local/julia/bin/julia -e 'using Pkg; Pkg.add([PackageSpec(name="CUDAapi"), PackageSpec(name="CUDAdrv"), PackageSpec(name="CUDAnative"), PackageSpec(name="CuArrays")])' && \
    echo "/usr/local/julia/lib" >> /etc/ld.so.conf.d/hpccm.conf && ldconfig && \
    rm -rf /var/tmp/julia-1.2.0-linux-x86_64.tar.gz /var/tmp/julia-1.2.0
ENV PATH=/usr/local/julia/bin:$PATH''')

    @x86_64
    @ubuntu
    @docker
    def test_runtime(self):
        """runtime"""
        j = julia()
        r = j.runtime()
        self.assertEqual(str(j), str(r))
