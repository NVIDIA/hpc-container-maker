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

"""Test cases for the conda module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import centos, docker, ppc64le, ubuntu, x86_64

from hpccm.building_blocks.conda import conda

class Test_conda(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @x86_64
    @ubuntu
    @docker
    def test_defaults_ubuntu(self):
        """Default conda building block"""
        c = conda(eula=True, packages=['numpy'])
        self.assertEqual(str(c),
r'''# Anaconda
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ca-certificates \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp http://repo.anaconda.com/miniconda/Miniconda3-4.7.12-Linux-x86_64.sh && \
    bash /var/tmp/Miniconda3-4.7.12-Linux-x86_64.sh -b -p /usr/local/anaconda && \
    /usr/local/anaconda/bin/conda init && \
    ln -s /usr/local/anaconda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    . /usr/local/anaconda/etc/profile.d/conda.sh && \
    conda activate base && \
    conda install -y numpy && \
    /usr/local/anaconda/bin/conda clean -afy && \
    rm -rf /var/tmp/Miniconda3-4.7.12-Linux-x86_64.sh''')

    @x86_64
    @centos
    @docker
    def test_defaults_centos(self):
        """Default conda building block"""
        c = conda(eula=True, packages=['numpy'])
        self.assertEqual(str(c),
r'''# Anaconda
RUN yum install -y \
        ca-certificates \
        wget && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp http://repo.anaconda.com/miniconda/Miniconda3-4.7.12-Linux-x86_64.sh && \
    bash /var/tmp/Miniconda3-4.7.12-Linux-x86_64.sh -b -p /usr/local/anaconda && \
    /usr/local/anaconda/bin/conda init && \
    ln -s /usr/local/anaconda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    . /usr/local/anaconda/etc/profile.d/conda.sh && \
    conda activate base && \
    conda install -y numpy && \
    /usr/local/anaconda/bin/conda clean -afy && \
    rm -rf /var/tmp/Miniconda3-4.7.12-Linux-x86_64.sh''')

    @ppc64le
    @ubuntu
    @docker
    def test_ppc64le(self):
        """ppc64le"""
        c = conda(eula=True)
        self.assertEqual(str(c),
r'''# Anaconda
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ca-certificates \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp http://repo.anaconda.com/miniconda/Miniconda3-4.7.12-Linux-ppc64le.sh && \
    bash /var/tmp/Miniconda3-4.7.12-Linux-ppc64le.sh -b -p /usr/local/anaconda && \
    /usr/local/anaconda/bin/conda init && \
    ln -s /usr/local/anaconda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    /usr/local/anaconda/bin/conda clean -afy && \
    rm -rf /var/tmp/Miniconda3-4.7.12-Linux-ppc64le.sh''')

    @x86_64
    @ubuntu
    @docker
    def test_channels(self):
        """channels"""
        c = conda(channels=['conda-forge', 'nvidia'], eula=True)
        self.assertEqual(str(c),
r'''# Anaconda
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ca-certificates \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp http://repo.anaconda.com/miniconda/Miniconda3-4.7.12-Linux-x86_64.sh && \
    bash /var/tmp/Miniconda3-4.7.12-Linux-x86_64.sh -b -p /usr/local/anaconda && \
    /usr/local/anaconda/bin/conda init && \
    ln -s /usr/local/anaconda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    . /usr/local/anaconda/etc/profile.d/conda.sh && \
    conda activate base && \
    conda config --add channels conda-forge --add channels nvidia && \
    /usr/local/anaconda/bin/conda clean -afy && \
    rm -rf /var/tmp/Miniconda3-4.7.12-Linux-x86_64.sh''')

    @x86_64
    @ubuntu
    @docker
    def test_environment(self):
        """environment"""
        c = conda(eula=True, environment='foo/environment.yml')
        self.assertEqual(str(c),
r'''# Anaconda
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ca-certificates \
        wget && \
    rm -rf /var/lib/apt/lists/*
COPY foo/environment.yml /var/tmp/environment.yml
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp http://repo.anaconda.com/miniconda/Miniconda3-4.7.12-Linux-x86_64.sh && \
    bash /var/tmp/Miniconda3-4.7.12-Linux-x86_64.sh -b -p /usr/local/anaconda && \
    /usr/local/anaconda/bin/conda init && \
    ln -s /usr/local/anaconda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    . /usr/local/anaconda/etc/profile.d/conda.sh && \
    conda activate base && \
    conda env update -f /var/tmp/environment.yml && \
    rm -rf /var/tmp/environment.yml && \
    /usr/local/anaconda/bin/conda clean -afy && \
    rm -rf /var/tmp/Miniconda3-4.7.12-Linux-x86_64.sh''')

    @x86_64
    @ubuntu
    @docker
    def test_python2(self):
        """python 2"""
        c = conda(eula=True, python2=True)
        self.assertEqual(str(c),
r'''# Anaconda
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ca-certificates \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp http://repo.anaconda.com/miniconda/Miniconda2-4.7.12-Linux-x86_64.sh && \
    bash /var/tmp/Miniconda2-4.7.12-Linux-x86_64.sh -b -p /usr/local/anaconda && \
    /usr/local/anaconda/bin/conda init && \
    ln -s /usr/local/anaconda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    /usr/local/anaconda/bin/conda clean -afy && \
    rm -rf /var/tmp/Miniconda2-4.7.12-Linux-x86_64.sh''')

    @x86_64
    @ubuntu
    @docker
    def test_runtime(self):
        """runtime"""
        c = conda(eula=True)
        r = c.runtime()
        self.assertEqual(r,
r'''# Anaconda
COPY --from=0 /usr/local/anaconda /usr/local/anaconda
RUN /usr/local/anaconda/bin/conda init && \
    ln -s /usr/local/anaconda/etc/profile.d/conda.sh /etc/profile.d/conda.sh''')
