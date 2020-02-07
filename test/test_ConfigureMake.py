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

"""Test cases for the ConfigureMake module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from hpccm.templates.ConfigureMake import ConfigureMake
from hpccm.toolchain import toolchain

class Test_ConfigureMake(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    def test_defaults(self):
        """Default values"""
        cm = ConfigureMake()

        # configure step
        configure = cm.configure_step()
        self.assertEqual(configure, './configure --prefix=/usr/local')

        # build step
        build = cm.build_step()
        self.assertEqual(build, 'make -j$(nproc)')

        # check step
        check = cm.check_step()
        self.assertEqual(check, 'make -j$(nproc) check')

        # install step
        install = cm.install_step()
        self.assertEqual(install, 'make -j$(nproc) install')

    def test_toolchain(self):
        """Toolchain specified"""
        cm = ConfigureMake()
        tc = toolchain(CC='mycc', CXX='mycxx', FC='myfc', F77='myf77',
                       F90='myf90', CFLAGS='-g -O3', CPPFLAGS='-DFOO -DBAR',
                       CXXFLAGS='-g -O3', FCFLAGS='-g -O3', FFLAGS='-g -O3',
                       FLIBS='-ldl',
                       LD_LIBRARY_PATH='/opt/mysw/lib:/opt/yoursw/lib',
                       LDFLAGS='-Wl,--start-group foo.o bar.o -Wl,--endgroup',
                       LIBS='-ldl -lpthread')

        configure = cm.configure_step(toolchain=tc)
        self.assertEqual(configure, '''CC=mycc CFLAGS='-g -O3' CPPFLAGS='-DFOO -DBAR' CXX=mycxx CXXFLAGS='-g -O3' F77=myf77 F90=myf90 FC=myfc FCFLAGS='-g -O3' FFLAGS='-g -O3' FLIBS=-ldl LD_LIBRARY_PATH=/opt/mysw/lib:/opt/yoursw/lib LDFLAGS='-Wl,--start-group foo.o bar.o -Wl,--endgroup' LIBS='-ldl -lpthread' ./configure --prefix=/usr/local''')

    def test_directory(self):
        """Source directory specified"""
        cm = ConfigureMake()

        configure = cm.configure_step(directory='/tmp/foo')
        # Note extra whitespace
        self.assertEqual(configure,
                         'cd /tmp/foo &&   ./configure --prefix=/usr/local')

    def test_build_directory(self):
        """Build directory specified"""
        cm = ConfigureMake()

        configure = cm.configure_step(build_directory='/tmp/build',
                                      directory='/tmp/src')
        # Note extra whitespace
        self.assertEqual(configure,
                         'mkdir -p /tmp/build && cd /tmp/build &&   /tmp/src/configure --prefix=/usr/local')

    def test_parallel(self):
        """Parallel count specified"""
        cm = ConfigureMake(parallel=7)

        # Function arguments override constructor
        build = cm.build_step(parallel=11)
        self.assertEqual(build, 'make -j11')

        # Use constructor arguments
        build = cm.build_step()
        self.assertEqual(build, 'make -j7')

    def test_prefix(self):
        """Prefix specified"""
        cm = ConfigureMake(prefix='/my/prefix')

        configure = cm.configure_step()
        self.assertEqual(configure, './configure --prefix=/my/prefix')

    def test_configure_opts(self):
        """Configure options specified"""
        cm = ConfigureMake(opts=['--with-foo', '--without-bar'])

        # Function arguments override constructor
        configure = cm.configure_step(opts=['--without-foo', '--with-bar'])
        self.assertEqual(configure, './configure --prefix=/usr/local --with-bar --without-foo')

        # Use constructor arguments
        configure = cm.configure_step()
        self.assertEqual(configure, './configure --prefix=/usr/local --with-foo --without-bar')

    def test_kwargs(self):
        """kwargs"""
        cm = ConfigureMake(disable_long_option=True, enable_foo=True,
                           with_foo=True, with_foo2='/usr',
                           without_bar=True, prefix=None)
        configure = cm.configure_step()
        self.assertEqual(configure, './configure --disable-long-option --enable-foo --with-foo --with-foo2=/usr --without-bar')
