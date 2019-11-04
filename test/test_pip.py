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

"""Test cases for the pip module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import centos, centos8, docker, ubuntu

from hpccm.building_blocks.pip import pip

class Test_pip(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @ubuntu
    @docker
    def test_defaults_ubuntu(self):
        """Default pip building block"""
        p = pip(packages=['hpccm'])
        self.assertEqual(str(p),
r'''# pip
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        python-pip \
        python-setuptools \
        python-wheel && \
    rm -rf /var/lib/apt/lists/*
RUN pip install hpccm''')

    @centos
    @docker
    def test_defaults_centos(self):
        """Default pip building block"""
        p = pip(packages=['hpccm'])
        self.assertEqual(str(p),
r'''# pip
RUN yum install -y epel-release && \
    yum install -y \
        python2-pip && \
    rm -rf /var/cache/yum/*
RUN pip install hpccm''')

    @centos8
    @docker
    def test_alternatives_centos8(self):
        """Default pip building block"""
        p = pip(packages=['hpccm'], alternatives=True)
        self.assertEqual(str(p),
r'''# pip
RUN yum install -y \
        python2-pip && \
    rm -rf /var/cache/yum/*
RUN alternatives --set python /usr/bin/python2 && \
    alternatives --install /usr/bin/pip pip /usr/bin/pip2 30
RUN pip install hpccm''')

    @ubuntu
    @docker
    def test_pip3_ubuntu(self):
        """pip3 w/ pip building block"""
        p = pip(packages=['hpccm'], pip='pip3')
        self.assertEqual(str(p),
r'''# pip
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        python3-pip \
        python3-setuptools \
        python3-wheel && \
    rm -rf /var/lib/apt/lists/*
RUN pip3 install hpccm''')

    @centos
    @docker
    def test_pip3_centos(self):
        """pip3 w/ pip building block"""
        p = pip(packages=['hpccm'], pip='pip3')
        self.assertEqual(str(p),
r'''# pip
RUN yum install -y \
        python3-pip && \
    rm -rf /var/cache/yum/*
RUN pip3 install hpccm''')

    @ubuntu
    @docker
    def test_no_ospackages(self):
        """empty ospackages option"""
        p = pip(ospackages=[], packages=['hpccm'])
        self.assertEqual(str(p),
r'''# pip
RUN pip install hpccm''')

    @ubuntu
    @docker
    def test_ospackages(self):
        """specify ospackages option"""
        p = pip(ospackages=['foo'], packages=['hpccm'])
        self.assertEqual(str(p),
r'''# pip
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        foo && \
    rm -rf /var/lib/apt/lists/*
RUN pip install hpccm''')

    @ubuntu
    @docker
    def test_requirements(self):
        """specify requirements options"""
        p = pip(requirements='foo/requirements.txt')
        self.assertEqual(str(p),
r'''# pip
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        python-pip \
        python-setuptools \
        python-wheel && \
    rm -rf /var/lib/apt/lists/*
COPY foo/requirements.txt /var/tmp/requirements.txt
RUN pip install -r /var/tmp/requirements.txt && \
    rm -rf /var/tmp/requirements.txt''')

    @ubuntu
    @docker
    def test_upgrade(self):
        """upgrade option"""
        p = pip(packages=['hpccm'], upgrade=True)
        self.assertEqual(str(p),
r'''# pip
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        python-pip \
        python-setuptools \
        python-wheel && \
    rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip && \
    pip install hpccm''')
