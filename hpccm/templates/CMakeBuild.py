
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

"""Documentation TBD"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function
from six.moves import shlex_quote

import logging  # pylint: disable=unused-import
import os


class CMakeBuild(object):
    """Documentation TBD"""

    def __init__(self, **kwargs):
        """Documentation TBD"""

        #super(ConfigureMake, self).__init__()
        self.__build_directory = None

        # Some components complain if some compiler variables are
        # enabled, e.g., MVAPICH2 with F90, so provide a way for the
        # caller to disable any of the compiler variables.
        self.toolchain_control = kwargs.get('toolchain_control',
                                            {'CC': True, 'CXX': True,
                                             'F77': True, 'F90': True,
                                             'FC': True})

    def build_step(self, target='all', parallel='$(nproc)'):
        """Documentation TBD"""
        return 'cmake --build {0} --target {1} -- -j{2}'.format(
            self.__build_directory, target, parallel)

    def configure_step(self, directory=None, build_directory='build',
                       toolchain=None, opts=None):
        """Documentation TBD"""

        if not directory:
            raise ValueError("directory has to be given in CMakeBuild "
                             "configure_step!")
        if not os.path.isabs(directory):
            raise ValueError("directory given in CMakeBuild configure_step"
                             "has to be an absolute path!")

        if not os.path.isabs(build_directory):
            build_directory = os.path.join(directory, build_directory)

        self.__build_directory = build_directory

        change_directory = "mkdir -p {0} && cd {0} && ".format(
            self.__build_directory)

        prefix = []
        if toolchain:
            if toolchain.CC and self.toolchain_control.get('CC'):
                prefix.append('CC={}'.format(toolchain.CC))

            if toolchain.CFLAGS:
                prefix.append('CFLAGS={}'.format(shlex_quote(
                    toolchain.CFLAGS)))

            if toolchain.CPPFLAGS:
                prefix.append('CPPFLAGS={}'.format(shlex_quote(
                    toolchain.CPPFLAGS)))

            if toolchain.CXX and self.toolchain_control.get('CXX'):
                prefix.append('CXX={}'.format(toolchain.CXX))

            if toolchain.CXXFLAGS:
                prefix.append('CXXFLAGS={}'.format(shlex_quote(
                    toolchain.CXXFLAGS)))

            if toolchain.F77 and self.toolchain_control.get('F77'):
                prefix.append('F77={}'.format(toolchain.F77))

            if toolchain.F90 and self.toolchain_control.get('F90'):
                prefix.append('F90={}'.format(toolchain.F90))

            if toolchain.FC and self.toolchain_control.get('FC'):
                prefix.append('FC={}'.format(toolchain.FC))

            if toolchain.FCFLAGS:
                prefix.append('FCFLAGS={}'.format(shlex_quote(
                    toolchain.FCFLAGS)))

            if toolchain.FFLAGS:
                prefix.append('FFLAGS={}'.format(shlex_quote(
                    toolchain.FFLAGS)))

            if toolchain.FLIBS:
                prefix.append('FLIBS={}'.format(shlex_quote(
                    toolchain.FLIBS)))

            if toolchain.LD_LIBRARY_PATH:
                prefix.append('LD_LIBRARY_PATH={}'.format(shlex_quote(
                    toolchain.LD_LIBRARY_PATH)))

            if toolchain.LDFLAGS:
                prefix.append('LDFLAGS={}'.format(shlex_quote(
                    toolchain.LDFLAGS)))

            if toolchain.LIBS:
                prefix.append('LIBS={}'.format(shlex_quote(
                    toolchain.LIBS)))

        configure_prefix = ' '.join(prefix)
        if configure_prefix != '':
            configure_prefix += ' '
        
        configure_opts = ''
        if opts:
            configure_opts = ' '.join(opts)
            configure_opts += ' '

        cmd = '{0}{1}cmake {2}{3}'.format(
            change_directory, configure_prefix, configure_opts, directory)

        return cmd.strip()  # trim whitespace
