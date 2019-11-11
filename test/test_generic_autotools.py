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

"""Test cases for the generic_autotools module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import centos, docker, ubuntu

from hpccm.building_blocks.generic_autotools import generic_autotools
from hpccm.toolchain import toolchain

class Test_generic_autotools(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @ubuntu
    @docker
    def test_defaults_ubuntu(self):
        """Default generic_autotools building block"""
        g = generic_autotools(
            directory='tcl8.6.9/unix',
            prefix='/usr/local/tcl',
            url='https://prdownloads.sourceforge.net/tcl/tcl8.6.9-src.tar.gz')
        self.assertEqual(str(g),
r'''# https://prdownloads.sourceforge.net/tcl/tcl8.6.9-src.tar.gz
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://prdownloads.sourceforge.net/tcl/tcl8.6.9-src.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/tcl8.6.9-src.tar.gz -C /var/tmp -z && \
    cd /var/tmp/tcl8.6.9/unix &&   ./configure --prefix=/usr/local/tcl && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/tcl8.6.9-src.tar.gz /var/tmp/tcl8.6.9/unix''')

    @ubuntu
    @docker
    def test_no_url(self):
        """missing url"""
        with self.assertRaises(RuntimeError):
            g = generic_autotools()

    @ubuntu
    @docker
    def test_invalid_package(self):
        """invalid package url"""
        with self.assertRaises(RuntimeError):
            g = generic_autotools(url='https://foo/bar.sh')

    @ubuntu
    @docker
    def test_pre_and_post(self):
        """Preconfigure and postinstall options"""
        g = generic_autotools(
            directory='tcl8.6.9/unix',
            postinstall=['echo "post"'],
            preconfigure=['echo "pre"'],
            prefix='/usr/local/tcl',
            url='https://prdownloads.sourceforge.net/tcl/tcl8.6.9-src.tar.gz')
        self.assertEqual(str(g),
r'''# https://prdownloads.sourceforge.net/tcl/tcl8.6.9-src.tar.gz
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://prdownloads.sourceforge.net/tcl/tcl8.6.9-src.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/tcl8.6.9-src.tar.gz -C /var/tmp -z && \
    cd /var/tmp/tcl8.6.9/unix && \
    echo "pre" && \
    cd /var/tmp/tcl8.6.9/unix &&   ./configure --prefix=/usr/local/tcl && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    cd /usr/local/tcl && \
    echo "post" && \
    rm -rf /var/tmp/tcl8.6.9-src.tar.gz /var/tmp/tcl8.6.9/unix''')

    @ubuntu
    @docker
    def test_configure_opts_check(self):
        """Configure options and check enabled"""
        g = generic_autotools(
            check=True,
            configure_opts=['--disable-getpwuid',
                            '--enable-orterun-prefix-by-default'],
            prefix='/usr/local/openmpi',
            url='https://www.open-mpi.org/software/ompi/v4.0/downloads/openmpi-4.0.1.tar.bz2')
        self.assertEqual(str(g),
r'''# https://www.open-mpi.org/software/ompi/v4.0/downloads/openmpi-4.0.1.tar.bz2
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://www.open-mpi.org/software/ompi/v4.0/downloads/openmpi-4.0.1.tar.bz2 && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/openmpi-4.0.1.tar.bz2 -C /var/tmp -j && \
    cd /var/tmp/openmpi-4.0.1 &&   ./configure --prefix=/usr/local/openmpi --disable-getpwuid --enable-orterun-prefix-by-default && \
    make -j$(nproc) && \
    make -j$(nproc) check && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/openmpi-4.0.1.tar.bz2 /var/tmp/openmpi-4.0.1''')

    @ubuntu
    @docker
    def test_environment_and_toolchain(self):
        """environment and toolchain"""
        tc = toolchain(CC='gcc', CXX='g++', FC='gfortran')
        g = generic_autotools(
            build_directory='/tmp/build',
            directory='/var/tmp/tcl8.6.9/unix',
            environment={'FOO': 'BAR'},
            prefix='/usr/local/tcl',
            toolchain=tc,
            url='https://prdownloads.sourceforge.net/tcl/tcl8.6.9-src.tar.gz')
        self.assertEqual(str(g),
r'''# https://prdownloads.sourceforge.net/tcl/tcl8.6.9-src.tar.gz
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://prdownloads.sourceforge.net/tcl/tcl8.6.9-src.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/tcl8.6.9-src.tar.gz -C /var/tmp -z && \
    mkdir -p /tmp/build && cd /tmp/build &&  FOO=BAR CC=gcc CXX=g++ FC=gfortran /var/tmp/tcl8.6.9/unix/configure --prefix=/usr/local/tcl && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/tcl8.6.9-src.tar.gz /var/tmp/tcl8.6.9/unix /tmp/build''')

    @ubuntu
    @docker
    def test_runtime(self):
        """Runtime"""
        g = generic_autotools(
            directory='tcl8.6.9/unix',
            prefix='/usr/local/tcl',
            url='https://prdownloads.sourceforge.net/tcl/tcl8.6.9-src.tar.gz')
        r = g.runtime()
        self.assertEqual(r,
r'''# https://prdownloads.sourceforge.net/tcl/tcl8.6.9-src.tar.gz
COPY --from=0 /usr/local/tcl /usr/local/tcl''')
