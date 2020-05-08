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

"""Test cases for the slurm_pmi2 module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import centos, docker, ubuntu, x86_64

from hpccm.building_blocks.slurm_pmi2 import slurm_pmi2

class Test_slurm_pmi2(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @x86_64
    @ubuntu
    @docker
    def test_defaults_ubuntu(self):
        """Default slurm_pmi2 building block"""
        p = slurm_pmi2()
        self.assertEqual(str(p),
r'''# SLURM PMI2 version 19.05.5
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        bzip2 \
        file \
        make \
        perl \
        tar \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://download.schedmd.com/slurm/slurm-19.05.5.tar.bz2 && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/slurm-19.05.5.tar.bz2 -C /var/tmp -j && \
    cd /var/tmp/slurm-19.05.5 &&   ./configure --prefix=/usr/local/slurm-pmi2 && \
    cd /var/tmp/slurm-19.05.5 && \
    make -C contribs/pmi2 install && \
    rm -rf /var/tmp/slurm-19.05.5 /var/tmp/slurm-19.05.5.tar.bz2''')

    @x86_64
    @ubuntu
    @docker
    def test_ldconfig(self):
        """ldconfig option"""
        p = slurm_pmi2(ldconfig=True, version='19.05.4')
        self.assertEqual(str(p),
r'''# SLURM PMI2 version 19.05.4
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        bzip2 \
        file \
        make \
        perl \
        tar \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://download.schedmd.com/slurm/slurm-19.05.4.tar.bz2 && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/slurm-19.05.4.tar.bz2 -C /var/tmp -j && \
    cd /var/tmp/slurm-19.05.4 &&   ./configure --prefix=/usr/local/slurm-pmi2 && \
    cd /var/tmp/slurm-19.05.4 && \
    make -C contribs/pmi2 install && \
    echo "/usr/local/slurm-pmi2/lib" >> /etc/ld.so.conf.d/hpccm.conf && ldconfig && \
    rm -rf /var/tmp/slurm-19.05.4 /var/tmp/slurm-19.05.4.tar.bz2''')

    @x86_64
    @ubuntu
    @docker
    def test_runtime(self):
        """Runtime"""
        p = slurm_pmi2()
        r = p.runtime()
        self.assertEqual(r,
r'''# SLURM PMI2
COPY --from=0 /usr/local/slurm-pmi2 /usr/local/slurm-pmi2''')
