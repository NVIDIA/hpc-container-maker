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

"""Test cases for the generic_build module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import centos, docker, ubuntu

from hpccm.building_blocks.generic_build import generic_build
from hpccm.toolchain import toolchain

class Test_generic_build(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @ubuntu
    @docker
    def test_defaults_ubuntu(self):
        """Default generic_build building block"""
        g = generic_build(build=['make ARCH=sm_70'],
                          install=['cp stream /usr/local/bin/cuda-stream'],
                          repository='https://github.com/bcumming/cuda-stream')
        self.assertEqual(str(g),
r'''# https://github.com/bcumming/cuda-stream
RUN mkdir -p /var/tmp && cd /var/tmp && git clone --depth=1 https://github.com/bcumming/cuda-stream cuda-stream && cd - && \
    cd /var/tmp/cuda-stream && \
    make ARCH=sm_70 && \
    cd /var/tmp/cuda-stream && \
    cp stream /usr/local/bin/cuda-stream && \
    rm -rf /var/tmp/cuda-stream''')

    @ubuntu
    @docker
    def test_no_url(self):
        """missing url"""
        with self.assertRaises(RuntimeError):
            g = generic_build()

    @ubuntu
    @docker
    def test_both_repository_and_url(self):
        """both repository and url"""
        with self.assertRaises(RuntimeError):
            g = generic_build(repository='foo', url='bar')

    @ubuntu
    @docker
    def test_invalid_package(self):
        """invalid package url"""
        with self.assertRaises(RuntimeError):
            g = generic_build(url='https://foo/bar.sh')

    @ubuntu
    @docker
    def test_prefix_recursive(self):
        """prefix and recursive option"""
        g = generic_build(build=['make ARCH=sm_70'],
                          install=['cp stream /usr/local/cuda-stream/bin/cuda-stream'],
                          prefix='/usr/local/cuda-stream/bin',
                          recursive=True,
                          repository='https://github.com/bcumming/cuda-stream')
        self.assertEqual(str(g),
r'''# https://github.com/bcumming/cuda-stream
RUN mkdir -p /var/tmp && cd /var/tmp && git clone --depth=1 --recursive https://github.com/bcumming/cuda-stream cuda-stream && cd - && \
    cd /var/tmp/cuda-stream && \
    make ARCH=sm_70 && \
    mkdir -p /usr/local/cuda-stream/bin && \
    cd /var/tmp/cuda-stream && \
    cp stream /usr/local/cuda-stream/bin/cuda-stream && \
    rm -rf /var/tmp/cuda-stream''')

    @centos
    @docker
    def test_url(self):
        """url option"""
        g = generic_build(build=['make USE_OPENMP=1'],
                          directory='OpenBLAS-0.3.6',
                          install=['make install PREFIX=/usr/local/openblas'],
                          prefix='/usr/local/openblas',
                          url='https://github.com/xianyi/OpenBLAS/archive/v0.3.6.tar.gz')
        self.assertEqual(str(g),
r'''# https://github.com/xianyi/OpenBLAS/archive/v0.3.6.tar.gz
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/xianyi/OpenBLAS/archive/v0.3.6.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/v0.3.6.tar.gz -C /var/tmp -z && \
    cd /var/tmp/OpenBLAS-0.3.6 && \
    make USE_OPENMP=1 && \
    mkdir -p /usr/local/openblas && \
    cd /var/tmp/OpenBLAS-0.3.6 && \
    make install PREFIX=/usr/local/openblas && \
    rm -rf /var/tmp/OpenBLAS-0.3.6 /var/tmp/v0.3.6.tar.gz''')

    @centos
    @docker
    def test_package(self):
        """local package"""
        g = generic_build(build=['make USE_OPENMP=1'],
                          directory='OpenBLAS-0.3.6',
                          install=['make install PREFIX=/usr/local/openblas'],
                          package='openblas/v0.3.6.tar.gz',
                          prefix='/usr/local/openblas')
        self.assertEqual(str(g),
r'''# openblas/v0.3.6.tar.gz
COPY openblas/v0.3.6.tar.gz /var/tmp/v0.3.6.tar.gz
RUN mkdir -p /var/tmp && tar -x -f /var/tmp/v0.3.6.tar.gz -C /var/tmp -z && \
    cd /var/tmp/OpenBLAS-0.3.6 && \
    make USE_OPENMP=1 && \
    mkdir -p /usr/local/openblas && \
    cd /var/tmp/OpenBLAS-0.3.6 && \
    make install PREFIX=/usr/local/openblas && \
    rm -rf /var/tmp/OpenBLAS-0.3.6 /var/tmp/v0.3.6.tar.gz''')

    @centos
    @docker
    def test_environment_ldconfig_annotate(self):
        """ldconfig and environment options"""
        g = generic_build(annotate=True,
                          base_annotation='openblas',
                          branch='v0.3.6',
                          build=['make USE_OPENMP=1'],
                          devel_environment={'CPATH': '/usr/local/openblas/include:$CPATH'},
                          install=['make install PREFIX=/usr/local/openblas'],
                          ldconfig=True,
                          prefix='/usr/local/openblas',
                          repository='https://github.com/xianyi/OpenBLAS.git',
                          runtime_environment={'CPATH': '/usr/local/openblas/include:$CPATH'})
        self.assertEqual(str(g),
r'''# https://github.com/xianyi/OpenBLAS.git
RUN mkdir -p /var/tmp && cd /var/tmp && git clone --depth=1 --branch v0.3.6 https://github.com/xianyi/OpenBLAS.git OpenBLAS && cd - && \
    cd /var/tmp/OpenBLAS && \
    make USE_OPENMP=1 && \
    mkdir -p /usr/local/openblas && \
    cd /var/tmp/OpenBLAS && \
    make install PREFIX=/usr/local/openblas && \
    echo "/usr/local/openblas/lib" >> /etc/ld.so.conf.d/hpccm.conf && ldconfig && \
    rm -rf /var/tmp/OpenBLAS
ENV CPATH=/usr/local/openblas/include:$CPATH
LABEL hpccm.openblas.branch=v0.3.6 \
    hpccm.openblas.repository=https://github.com/xianyi/OpenBLAS.git''')

        r = g.runtime()
        self.assertEqual(r,
r'''# https://github.com/xianyi/OpenBLAS.git
COPY --from=0 /usr/local/openblas /usr/local/openblas
RUN echo "/usr/local/openblas/lib" >> /etc/ld.so.conf.d/hpccm.conf && ldconfig
ENV CPATH=/usr/local/openblas/include:$CPATH
LABEL hpccm.openblas.branch=v0.3.6 \
    hpccm.openblas.repository=https://github.com/xianyi/OpenBLAS.git''')

    @ubuntu
    @docker
    def test_runtime(self):
        """Runtime"""
        g = generic_build(build=['make ARCH=sm_70'],
                          install=['cp stream /usr/local/cuda-stream/bin/cuda-stream'],
                          prefix='/usr/local/cuda-stream/bin',
                          repository='https://github.com/bcumming/cuda-stream')
        r = g.runtime()
        self.assertEqual(r,
r'''# https://github.com/bcumming/cuda-stream
COPY --from=0 /usr/local/cuda-stream/bin /usr/local/cuda-stream/bin''')
