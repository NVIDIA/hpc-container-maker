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

# pylint: disable=invalid-name, too-few-public-methods

"""Test cases for the apt_get module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import docker, ubuntu

from hpccm.building_blocks.apt_get import apt_get

class Test_apt_get(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @ubuntu
    @docker
    def test_basic(self):
        """Basic apt_get"""
        a = apt_get(ospackages=['gcc', 'g++', 'gfortran'])
        self.assertEqual(str(a),
r'''RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        g++ \
        gcc \
        gfortran && \
    rm -rf /var/lib/apt/lists/*''')

    @ubuntu
    @docker
    def test_add_repo(self):
        """Add repo and key"""
        a = apt_get(keys=['https://www.example.com/key.pub'],
                    ospackages=['example'],
                    repositories=['deb http://www.example.com all main'])
        self.assertEqual(str(a),
r'''RUN wget -qO - https://www.example.com/key.pub | apt-key add - && \
    echo "deb http://www.example.com all main" >> /etc/apt/sources.list.d/hpccm.list && \
    apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        example && \
    rm -rf /var/lib/apt/lists/*''')

    @ubuntu
    @docker
    def test_download(self):
        """Download parameter"""
        a = apt_get(download=True, download_directory='/tmp/download',
                    ospackages=['libibverbs1'])
        self.assertEqual(str(a),
r'''RUN apt-get update -y && \
    mkdir -m 777 -p /tmp/download && cd /tmp/download && \
    DEBIAN_FRONTEND=noninteractive apt-get download -y --no-install-recommends \
        libibverbs1 && \
    rm -rf /var/lib/apt/lists/*''')

    @ubuntu
    @docker
    def test_extract(self):
        """Extract parameter"""
        a = apt_get(download=True, extract='/usr/local/ofed',
                    ospackages=['libibverbs1'])
        self.assertEqual(str(a),
r'''RUN apt-get update -y && \
    mkdir -m 777 -p /var/tmp/apt_get_download && cd /var/tmp/apt_get_download && \
    DEBIAN_FRONTEND=noninteractive apt-get download -y --no-install-recommends \
        libibverbs1 && \
    mkdir -p /usr/local/ofed && \
    find /var/tmp/apt_get_download -regextype posix-extended -type f -regex "/var/tmp/apt_get_download/(libibverbs1).*deb" -exec dpkg --extract {} /usr/local/ofed \; && \
    rm -rf /var/tmp/apt_get_download && \
    rm -rf /var/lib/apt/lists/*''')
