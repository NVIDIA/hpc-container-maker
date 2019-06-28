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

from helpers import centos, docker, ubuntu

from hpccm.building_blocks.julia import julia

class Test_julia(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @ubuntu
    @docker
    def test_defaults_ubuntu(self):
        """Default julia building block"""
        j = julia()
        self.assertEqual(str(j),
r'''# Julia version 1.1.0
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        tar \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://julialang-s3.julialang.org/bin/linux/x64/1.1/julia-1.1.0-linux-x86_64.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/julia-1.1.0-linux-x86_64.tar.gz -C /var/tmp -z && \
    cp -a /var/tmp/julia-1.1.0 /usr/local/julia && \
    rm -rf /var/tmp/julia-1.1.0-linux-x86_64.tar.gz /var/tmp/julia-1.1.0
ENV LD_LIBRARY_PATH=/usr/local/julia/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/julia/bin:$PATH''')

    @ubuntu
    @docker
    def test_depot_packages(self):
        """depot and packages options"""
        j = julia(depot='~/.julia-ngc', packages=['CUDAnative', 'CuArrays'])
        self.assertEqual(str(j),
r'''# Julia version 1.1.0
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        tar \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://julialang-s3.julialang.org/bin/linux/x64/1.1/julia-1.1.0-linux-x86_64.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/julia-1.1.0-linux-x86_64.tar.gz -C /var/tmp -z && \
    cp -a /var/tmp/julia-1.1.0 /usr/local/julia && \
    JULIA_DEPOT_PATH=~/.julia-ngc /usr/local/julia/bin/julia -e 'using Pkg; Pkg.add([PackageSpec(name="CUDAnative"), PackageSpec(name="CuArrays")])' && \
    rm -rf /var/tmp/julia-1.1.0-linux-x86_64.tar.gz /var/tmp/julia-1.1.0
ENV JULIA_DEPOT_PATH=~/.julia-ngc \
    LD_LIBRARY_PATH=/usr/local/julia/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/julia/bin:$PATH''')

    @ubuntu
    @docker
    def test_cuda_ldconfig(self):
        """cuda and ldconfig options"""
        j = julia(cuda=True, ldconfig=True)
        self.assertEqual(str(j),
r'''# Julia version 1.1.0
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        tar \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://julialang-s3.julialang.org/bin/linux/x64/1.1/julia-1.1.0-linux-x86_64.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/julia-1.1.0-linux-x86_64.tar.gz -C /var/tmp -z && \
    cp -a /var/tmp/julia-1.1.0 /usr/local/julia && \
    /usr/local/julia/bin/julia -e 'using Pkg; Pkg.add([PackageSpec(name="CUDAnative"), PackageSpec(name="CuArrays"), PackageSpec(name="GPUArrays")])' && \
    echo "/usr/local/julia/lib" >> /etc/ld.so.conf.d/hpccm.conf && ldconfig && \
    rm -rf /var/tmp/julia-1.1.0-linux-x86_64.tar.gz /var/tmp/julia-1.1.0
ENV PATH=/usr/local/julia/bin:$PATH''')

    @ubuntu
    @docker
    def test_runtime(self):
        """runtime"""
        j = julia()
        r = j.runtime()
        self.assertEqual(str(j), str(r))
