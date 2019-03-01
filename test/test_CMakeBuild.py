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

"""Test cases for the CMakeBuild module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from hpccm.templates.CMakeBuild import CMakeBuild
from hpccm.toolchain import toolchain

class Test_CMakeBuild(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    def test_defaults(self):
        """Default values"""
        cm = CMakeBuild()

        # configure step
        configure = cm.configure_step(directory='/tmp/src')
        self.assertEqual(configure, 'mkdir -p /tmp/src/build && cd /tmp/src/build && cmake -DCMAKE_INSTALL_PREFIX=/usr/local /tmp/src')

        # build step
        build = cm.build_step()
        self.assertEqual(build, 'cmake --build /tmp/src/build --target all -- -j$(nproc)')

        # build some target
        install = cm.build_step(target='foo')
        self.assertEqual(install, 'cmake --build /tmp/src/build --target foo -- -j$(nproc)')

    def test_toolchain(self):
        """Toolchain specified"""
        cm = CMakeBuild()
        tc = toolchain(CC='mycc', CXX='mycxx', FC='myfc', F77='myf77',
                       F90='myf90', CFLAGS='-g -O3', CPPFLAGS='-DFOO -DBAR',
                       CXXFLAGS='-g -O3', FCFLAGS='-g -O3', FFLAGS='-g -O3',
                       FLIBS='-ldl',
                       LD_LIBRARY_PATH='/opt/mysw/lib:/opt/yoursw/lib',
                       LDFLAGS='-Wl,--start-group foo.o bar.o -Wl,--endgroup',
                       LIBS='-ldl -lpthread')

        configure = cm.configure_step(directory='/tmp/src', toolchain=tc)
        self.assertEqual(configure,
                         '''mkdir -p /tmp/src/build && cd /tmp/src/build && CC=mycc CFLAGS='-g -O3' CPPFLAGS='-DFOO -DBAR' CXX=mycxx CXXFLAGS='-g -O3' F77=myf77 F90=myf90 FC=myfc FCFLAGS='-g -O3' FFLAGS='-g -O3' FLIBS=-ldl LD_LIBRARY_PATH=/opt/mysw/lib:/opt/yoursw/lib LDFLAGS='-Wl,--start-group foo.o bar.o -Wl,--endgroup' LIBS='-ldl -lpthread' cmake -DCMAKE_INSTALL_PREFIX=/usr/local /tmp/src''')

    def test_directory(self):
        """Build directory specified"""
        cm = CMakeBuild()

        # Relative build dir
        configure = cm.configure_step(directory='/tmp/src',
                                      build_directory='../build')
        self.assertEqual(configure,
                         'mkdir -p /tmp/src/../build && cd /tmp/src/../build && cmake -DCMAKE_INSTALL_PREFIX=/usr/local /tmp/src')
        
        # Absolute build dir
        configure = cm.configure_step(directory='/tmp/src',
                                      build_directory='/tmp/build')
        self.assertEqual(configure,
                         'mkdir -p /tmp/build && cd /tmp/build && cmake -DCMAKE_INSTALL_PREFIX=/usr/local /tmp/src')

        # No build directory
        configure = cm.configure_step()
        self.assertEqual(configure,
                         'cmake -DCMAKE_INSTALL_PREFIX=/usr/local ..')

    def test_parallel(self):
        """Parallel count specified"""
        cm = CMakeBuild(parallel=4)
        cm.configure_step(directory='/tmp/src')

        # Function arguments override constructor
        build = cm.build_step(parallel=7)
        self.assertEqual(build,
                         'cmake --build /tmp/src/build --target all -- -j7')

        # Use constructor arguments
        build = cm.build_step()
        self.assertEqual(build,
                         'cmake --build /tmp/src/build --target all -- -j4')

    def test_configure_opts(self):
        """Configure options specified"""
        cm = CMakeBuild(opts=['-DWITH_BAR=ON'], prefix='')

        # Function arguments override constructor
        configure = cm.configure_step(
            directory='/tmp/src',
            opts=['-DCMAKE_BUILD_TYPE=Debug', '-DWITH_FOO=ON']
        )
        self.assertEqual(configure,
                         'mkdir -p /tmp/src/build && cd /tmp/src/build && cmake -DCMAKE_BUILD_TYPE=Debug -DWITH_FOO=ON /tmp/src')

        # Use constructor arguments
        configure = cm.configure_step(directory='/tmp/src')
        self.assertEqual(configure,
                         'mkdir -p /tmp/src/build && cd /tmp/src/build && cmake -DWITH_BAR=ON /tmp/src')
