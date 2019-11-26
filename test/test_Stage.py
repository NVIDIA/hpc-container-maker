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

"""Test cases for the Stage module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import centos, docker, singularity32

from hpccm.building_blocks import boost
from hpccm.building_blocks import gnu
from hpccm.primitives.baseimage import baseimage
from hpccm.primitives.shell import shell
from hpccm.Stage import Stage

class Test_Stage(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    def test_value(self):
        """Single layer"""
        s = Stage()
        self.assertFalse(len(s))
        s += 1
        self.assertTrue(len(s))

    def test_list(self):
        """List of layers"""
        s = Stage()
        self.assertEqual(len(s), 0)
        s += [1, 2]
        self.assertEqual(len(s), 2)

    @docker
    def test_baseimage(self):
        """Base image specification"""
        s = Stage()
        s.name = 'bar'
        s.baseimage('foo')
        self.assertEqual(str(s), 'FROM foo AS bar')

    @docker
    def test_baseimage_first(self):
        """Base image is always first"""
        s = Stage()
        s += shell(commands=['abc'])
        s.name = 'bar'
        s.baseimage('foo')
        self.assertEqual(str(s), 'FROM foo AS bar\n\nRUN abc')

    @centos
    @docker
    def test_runtime(self):
        """Runtime from a previous stage"""
        s0 = Stage()
        s0 += gnu()
        s0 += shell(commands=['gcc -o hello hello.c'])
        s1 = Stage()
        s1 += s0.runtime()
        self.assertEqual(str(s1),
r'''# GNU compiler runtime
RUN yum install -y \
        libgfortran \
        libgomp && \
    rm -rf /var/cache/yum/*''')

    @centos
    @docker
    def test_runtime_exclude(self):
        """Runtime from a previous stage with exclude"""
        s0 = Stage()
        s0 += gnu()
        s0 += boost()
        s1 = Stage()
        s1 += s0.runtime(exclude=['boost'])
        self.assertEqual(str(s1),
r'''# GNU compiler runtime
RUN yum install -y \
        libgfortran \
        libgomp && \
    rm -rf /var/cache/yum/*''')

    @docker
    def test_multistage_noas_docker(self):
        """Multistage naming"""
        s0 = Stage()
        s0 += baseimage(image='centos:7')
        s0 += boost()
        s1 = Stage()
        s1 += s0.runtime()
        self.assertEqual(str(s1),
r'''# Boost
COPY --from=0 /usr/local/boost /usr/local/boost
ENV LD_LIBRARY_PATH=/usr/local/boost/lib:$LD_LIBRARY_PATH''')

    @singularity32
    def test_multistage_noas_singularity(self):
        """Multistage naming"""
        s0 = Stage()
        s0 += baseimage(image='centos:7')
        s0 += boost()
        s1 = Stage()
        s1 += s0.runtime()
        self.assertEqual(str(s1),
r'''# Boost
%files from 0
    /usr/local/boost /usr/local/boost
%environment
    export LD_LIBRARY_PATH=/usr/local/boost/lib:$LD_LIBRARY_PATH
%post
    export LD_LIBRARY_PATH=/usr/local/boost/lib:$LD_LIBRARY_PATH''')

    @docker
    def test_multistage_as_docker(self):
        """Multistage naming"""
        s0 = Stage()
        s0 += baseimage(image='centos:7', _as='devel')
        s0 += boost()
        s1 = Stage()
        s1 += s0.runtime()
        self.assertEqual(str(s1),
r'''# Boost
COPY --from=devel /usr/local/boost /usr/local/boost
ENV LD_LIBRARY_PATH=/usr/local/boost/lib:$LD_LIBRARY_PATH''')

    @singularity32
    def test_multistage_as_singularity(self):
        """Multistage naming"""
        s0 = Stage()
        s0 += baseimage(image='centos:7', _as='devel')
        s0 += boost()
        s1 = Stage()
        s1 += s0.runtime()
        self.assertEqual(str(s1),
r'''# Boost
%files from devel
    /usr/local/boost /usr/local/boost
%environment
    export LD_LIBRARY_PATH=/usr/local/boost/lib:$LD_LIBRARY_PATH
%post
    export LD_LIBRARY_PATH=/usr/local/boost/lib:$LD_LIBRARY_PATH''')

    @docker
    def test_multistage_as_override_docker(self):
        """Multistage naming"""
        s0 = Stage()
        s0 += baseimage(image='centos:7', _as='devel')
        s0 += boost()
        s1 = Stage()
        s1 += s0.runtime(_from='build')
        self.assertEqual(str(s1),
r'''# Boost
COPY --from=build /usr/local/boost /usr/local/boost
ENV LD_LIBRARY_PATH=/usr/local/boost/lib:$LD_LIBRARY_PATH''')

    @singularity32
    def test_multistage_as_override_singularity(self):
        """Multistage naming"""
        s0 = Stage()
        s0 += baseimage(image='centos:7', _as='devel')
        s0 += boost()
        s1 = Stage()
        s1 += s0.runtime(_from='build')
        self.assertEqual(str(s1),
r'''# Boost
%files from build
    /usr/local/boost /usr/local/boost
%environment
    export LD_LIBRARY_PATH=/usr/local/boost/lib:$LD_LIBRARY_PATH
%post
    export LD_LIBRARY_PATH=/usr/local/boost/lib:$LD_LIBRARY_PATH''')
