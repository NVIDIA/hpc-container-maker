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
from six import string_types
from six.moves import shlex_quote

import copy

import hpccm.base_object

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

        # Process --disable, --enable, --with, and --without options
        self.__opts = []
        for k in kwargs:
            # handles both --with and --without
            if (k.startswith('disable') or k.startswith('enable') or
                k.startswith('with')) and kwargs.get(k):
                opt = '--{}'.format(k.replace('_', '-'))

                if isinstance(kwargs.get(k), string_types):
                    self.__opts.append('{0}={1}'.format(opt, kwargs.get(k)))
                else:
                    self.__opts.append(opt)

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

    def configure_step(self, build_directory=None, directory=None,
                       environment=[], opts=[], toolchain=None):
        """Generate configure command line string"""

        change_directory = ''
        src_directory = '.'
        if directory:
            if build_directory:
                src_directory = directory
                change_directory = 'mkdir -p {0} && cd {0} && '.format(
                    build_directory)
            else:
                change_directory = 'cd {} && '.format(directory)

        e = copy.copy(environment)
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

        # Build set of configuration command line options
        optlist = []
        if not opts:
            if self.configure_opts:
                optlist.extend(self.configure_opts)
            if self.__opts:
                optlist.extend(self.__opts)
        else:
            optlist = opts

        # Remove duplicates and sort options
        configure_opts = ' '.join(sorted(list(set(optlist))))

        # Prefix is always the first option
        if self.prefix:
            configure_opts = '--prefix={0:s} {1}'.format(self.prefix,
                                                         configure_opts)

        cmd = '{0} {1} {3}/configure {2}'.format(change_directory,
                                       configure_env, configure_opts,
                                       src_directory)

        # Add an annotation if the caller inherits from the annotate template
        if callable(getattr(self, 'add_annotation', None)):
            self.add_annotation('configure', '{1} {3}/configure {2}'.format(
                change_directory, configure_env, configure_opts,
                src_directory).strip())

        return cmd.strip() # trim whitespace

    def install_step(self, parallel=None):
        """Generate make install command line string"""
        if not parallel:
            parallel = self.parallel
        return 'make -j{} install'.format(parallel)
