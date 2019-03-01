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

"""ConfigureMake template"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function
from six.moves import shlex_quote

import logging # pylint: disable=unused-import

import hpccm.base_object

from hpccm.toolchain import toolchain

class ConfigureMake(hpccm.base_object):
    """Template for autotools configure / make / make install workflow"""

    def __init__(self, **kwargs):
        """Initialize ConfigureMake template"""

        super(ConfigureMake, self).__init__(**kwargs)

        self.configure_opts = kwargs.get('opts', [])
        self.parallel = kwargs.get('parallel', '$(nproc)')
        self.prefix = kwargs.get('prefix', '/usr/local')

        # Some components complain if some compiler variables are
        # enabled, e.g., MVAPICH2 with F90, so provide a way for the
        # caller to disable any of the compiler variables.
        self.toolchain_control = kwargs.get('toolchain_control',
                                            {'CC': True, 'CXX': True,
                                             'F77': True, 'F90': True,
                                             'FC': True})

    def build_step(self, parallel=None):
        """Generate make command line string"""
        if not parallel:
            parallel = self.parallel
        return 'make -j{}'.format(parallel)

    def check_step(self, parallel=None):
        """Generate make check command line string"""
        if not parallel:
            parallel = self.parallel
        return 'make -j{} check'.format(parallel)

    def configure_step(self, directory=None, environment=[], opts=[],
                       toolchain=None):
        """Generate configure command line string"""

        change_directory = ''
        if directory:
            change_directory = 'cd {} && '.format(directory)

        e = []
        e.extend(environment)
        if toolchain:
            if toolchain.CC and self.toolchain_control.get('CC'):
                e.append('CC={}'.format(toolchain.CC))

            if toolchain.CFLAGS:
                e.append('CFLAGS={}'.format(shlex_quote(
                    toolchain.CFLAGS)))

            if toolchain.CPPFLAGS:
                e.append('CPPFLAGS={}'.format(shlex_quote(
                    toolchain.CPPFLAGS)))

            if toolchain.CXX and self.toolchain_control.get('CXX'):
                e.append('CXX={}'.format(toolchain.CXX))

            if toolchain.CXXFLAGS:
                e.append('CXXFLAGS={}'.format(shlex_quote(
                    toolchain.CXXFLAGS)))

            if toolchain.F77 and self.toolchain_control.get('F77'):
                e.append('F77={}'.format(toolchain.F77))

            if toolchain.F90 and self.toolchain_control.get('F90'):
                e.append('F90={}'.format(toolchain.F90))

            if toolchain.FC and self.toolchain_control.get('FC'):
                e.append('FC={}'.format(toolchain.FC))

            if toolchain.FCFLAGS:
                e.append('FCFLAGS={}'.format(shlex_quote(
                    toolchain.FCFLAGS)))

            if toolchain.FFLAGS:
                e.append('FFLAGS={}'.format(shlex_quote(
                    toolchain.FFLAGS)))

            if toolchain.FLIBS:
                e.append('FLIBS={}'.format(shlex_quote(
                    toolchain.FLIBS)))

            if toolchain.LD_LIBRARY_PATH:
                e.append('LD_LIBRARY_PATH={}'.format(shlex_quote(
                    toolchain.LD_LIBRARY_PATH)))

            if toolchain.LDFLAGS:
                e.append('LDFLAGS={}'.format(shlex_quote(
                    toolchain.LDFLAGS)))

            if toolchain.LIBS:
                e.append('LIBS={}'.format(shlex_quote(
                    toolchain.LIBS)))

        configure_env = ' '.join(e)

        if not opts and self.configure_opts:
            opts = self.configure_opts
        configure_opts = ' '.join(opts)
        if self.prefix:
            configure_opts = '--prefix={0:s} {1}'.format(self.prefix,
                                                         configure_opts)

        cmd = '{0} {1} ./configure {2}'.format(change_directory,
                                               configure_env, configure_opts)

        return cmd.strip() # trim whitespace

    def install_step(self, parallel=None):
        """Generate make install command line string"""
        if not parallel:
            parallel = self.parallel
        return 'make -j{} install'.format(parallel)
