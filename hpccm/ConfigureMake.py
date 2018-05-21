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

import logging # pylint: disable=unused-import

from hpccm.toolchain import toolchain

class ConfigureMake(object):
    """Documentation TBD"""

    def __init__(self, **kwargs):
        """Documentation TBD"""

        #super(ConfigureMake, self).__init__()

        self.configure_opts = kwargs.get('opts', [])
        self.parallel = kwargs.get('parallel', 4)
        self.prefix = kwargs.get('prefix', '/usr/local')

        # Some components complain if some compiler variables are
        # enabled, e.g., MVAPICH2 with F90, so provide a way for the
        # caller to disable any of the compiler variables.
        self.toolchain_control = kwargs.get('toolchain_control',
                                            {'CC': True, 'CXX': True,
                                             'F77': True, 'F90': True,
                                             'FC': True})

    def build_step(self):
        """Documentation TBD"""
        return 'make -j{0:d}'.format(self.parallel)

    def check_step(self):
        """Documentation TBD"""
        return 'make -j{0:d} check'.format(self.parallel)

    def configure_step(self, directory=None, toolchain=None):
        """Documentation TBD"""

        change_directory = ''
        if directory:
            change_directory = 'cd {} && '.format(directory)

        prefix = []
        if toolchain:
            if toolchain.CC and self.toolchain_control.get('CC'):
                prefix.append('CC={}'.format(toolchain.CC))

            if toolchain.CXX and self.toolchain_control.get('CXX'):
                prefix.append('CXX={}'.format(toolchain.CXX))

            if toolchain.F77 and self.toolchain_control.get('F77'):
                prefix.append('F77={}'.format(toolchain.F77))

            if toolchain.F90 and self.toolchain_control.get('F90'):
                prefix.append('F90={}'.format(toolchain.F90))

            if toolchain.FC and self.toolchain_control.get('FC'):
                prefix.append('FC={}'.format(toolchain.FC))

        configure_prefix = ' '.join(prefix)

        opts = ' '.join(self.configure_opts)
        if self.prefix:
            opts = '--prefix={0:s} {1}'.format(self.prefix, opts)

        cmd = '{0} {1} ./configure {2}'.format(change_directory, configure_prefix, opts)

        return cmd.strip() # trim whitespace

    def install_step(self):
        """Documentation TBD"""
        return 'make -j{0:d} install'.format(self.parallel)
