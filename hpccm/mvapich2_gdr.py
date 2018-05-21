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
# pylint: disable=too-many-instance-attributes

"""MVAPICH2-GDR building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import os
import re

import hpccm.config

from hpccm.comment import comment
from hpccm.common import linux_distro
from hpccm.copy import copy
from hpccm.environment import environment
from hpccm.packages import packages
from hpccm.shell import shell
from hpccm.toolchain import toolchain
from hpccm.wget import wget

class mvapich2_gdr(wget):
    """MVAPICH2-GDR building block"""

    def __init__(self, **kwargs):
        """Initialize building block"""

        # Trouble getting MRO with kwargs working correctly, so just call
        # the parent class constructors manually for now.
        #super(mvapich2_gdr, self).__init__(**kwargs)
        wget.__init__(self, **kwargs)

        self.__baseurl = kwargs.get('baseurl',
                                    'http://mvapich.cse.ohio-state.edu/download/mvapich/gdr')
        self.__cuda_version = kwargs.get('cuda_version', '9.0')
        self.__gnu = kwargs.get('gnu', True)
        self.__gnu_version = '4.8.5'
        self.__mofed_version = kwargs.get('mlnx_ofed_version', '3.4')
        self.__ospackages = kwargs.get('ospackages', [])
        self.__package = kwargs.get('package', '')
        self.__pgi = kwargs.get('pgi', False)
        self.__pgi_version = '17.10'
        self.version = kwargs.get('version', '2.3a')
        self.__wd = '/tmp' # working directory

        # Output toolchain
        self.toolchain = toolchain(CC='mpicc', CXX='mpicxx', F77='mpif77',
                                   F90='mpif90', FC='mpifort')

        # Validate compiler choice
        if self.__gnu and self.__pgi:
            logging.warning('Multiple compilers selected, using PGI')
            self.__gnu = False
        elif not self.__gnu and not self.__pgi:
            logging.warning('No compiler selected, using GNU')
            self.__gnu = True

        self.__commands = []              # Filled in by __setup()
        self.__environment_variables = {} # Filled in by __setup()
        self.__install_path = ''          # Filled in by __setup()

        self.__installer = ''             # Filled in by __distro()
        self.__package_template = ''      # Filled in by __distro()

        # Set the Linux distribution specific parameters
        self.__distro()

        # Construct the series of steps to execute
        self.__setup()

    def __str__(self):
        """String representation of the building block"""

        instructions = []
        if self.__package:
            instructions.append(comment('MVAPICH2-GDR'))
        else:
            instructions.append(comment(
                'MVAPICH2-GDR version {}'.format(self.version)))

        instructions.append(packages(ospackages=self.__ospackages))

        if self.__package:
            # Use source from local build context
            instructions.append(copy(src=self.__package,
                                     dest=os.path.join(self.__wd,
                                                       self.__package)))

        instructions.append(shell(commands=self.__commands))
        instructions.append(environment(
            variables=self.__environment_variables))

        return '\n'.join(str(x) for x in instructions)

    def cleanup_step(self, items=None):
        """Cleanup temporary files"""

        if not items: # pragma: no cover
            logging.warning('items are not defined')
            return ''

        return 'rm -rf {}'.format(' '.join(items))

    def __distro(self):
        """Based on the Linux distribution, set values accordingly.  A user
        specified value overrides any defaults."""

        if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
            if not self.__ospackages:
                self.__ospackages = ['openssh-client', 'wget']
            self.__runtime_ospackages = ['openssh-client']

            self.__installer = 'dpkg --install'

            self.__package_template = 'mvapich2-gdr-mcast.{0}.{1}.{2}_{3}-1.el7.centos_amd64.deb'
        elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
            if not self.__ospackages:
                self.__ospackages = ['openssh-clients', 'perl', 'wget']
            self.__runtime_ospackages = ['openssh-clients']

            # The RPM has dependencies on some CUDA libraries that are
            # present, but not in the RPM database.  Use --nodeps as a
            # workaround.
            self.__installer = 'rpm --install --nodeps'

            self.__package_template = 'mvapich2-gdr-mcast.{0}.{1}.{2}-{3}-1.el7.centos.x86_64.rpm'
        else: # pragma: no cover
            raise RuntimeError('Unknown Linux distribution')

    def __setup(self):
        """Construct the series of shell commands and environment variables,
           i.e., fill in self.__commands and self.__environment_variables"""

        if self.__package:
            # Install a package from the local build context
            package = self.__package

            # Deduce version strings from package name
            match = re.search(r'(?P<cuda>cuda\d+\.\d+)\.(?P<mofed>mofed\d+\.\d+)\.(?P<compiler>(gnu\d+\.\d+\.\d+)|(pgi\d+\.\d+))', package)
            cuda_string = match.groupdict()['cuda']
            mofed_string = match.groupdict()['mofed']
            compiler_string = match.groupdict()['compiler']
        else:
            # Download a package

            # Build the version strings based on the specified options
            if self.__gnu:
                compiler_string = 'gnu{}'.format(self.__gnu_version)
            elif self.__pgi:
                compiler_string = 'pgi{}'.format(self.__pgi_version)
            else:
                logging.error('Unknown compiler')
                compiler_string = 'unknown'

            cuda_string = 'cuda{}'.format(self.__cuda_version)
            mofed_string = 'mofed{}'.format(self.__mofed_version)

            # Package filename
            package = self.__package_template.format(
                cuda_string, mofed_string, compiler_string, self.version)

            # Download source from web
            url = '{0}/{1}/{2}/{3}'.format(self.__baseurl, self.version,
                                           mofed_string, package)
            self.__commands.append(self.download_step(url=url,
                                                      directory=self.__wd))

        # Install the package
        self.__commands.append('{0} {1}'.format(
            self.__installer, os.path.join(self.__wd, package)))

        # Workaround for bad path in the MPI compiler wrappers
        self.__commands.append('(test -f /usr/bin/bash || ln -s /bin/bash /usr/bin/bash)')

        # Workaround for using compiler wrappers in the build stage
        cuda_home = '/usr/local/cuda'
        self.__commands.append('ln -s {0} {1}'.format(
            os.path.join(cuda_home, 'lib64', 'stubs', 'nvidia-ml.so'),
            os.path.join(cuda_home, 'lib64', 'stubs', 'nvidia-ml.so.1')))

        # Cleanup
        self.__commands.append(self.cleanup_step(
            items=[os.path.join(self.__wd, package)]))

        # Setup environment variables
        self.__install_path = os.path.join('/opt', 'mvapich2', 'gdr',
                                           self.version, 'mcast', 'no-openacc',
                                           cuda_string, mofed_string,
                                           'mpirun', compiler_string)
        self.__environment_variables = {
            'LD_LIBRARY_PATH':
            '{}:$LD_LIBRARY_PATH'.format(os.path.join(self.__install_path,
                                                      'lib64')),
            'MV2_USE_GPUDIRECT': 0,
            'MV2_USE_GPUDIRECT_GDRCOPY': 0,
            'PATH': '{}:$PATH'.format(os.path.join(self.__install_path,
                                                   'bin')),
            # Workaround for using compiler wrappers in the build stage
            'PROFILE_POSTLIB': '"-L{} -lnvidia-ml"'.format(
                '/usr/local/cuda/lib64/stubs')}

    def runtime(self, _from='0'):
        """Install the runtime from a full build in a previous stage"""
        instructions = []
        instructions.append(comment('MVAPICH2-GDR'))
        instructions.append(packages(ospackages=self.__runtime_ospackages))
        instructions.append(copy(src=self.__install_path,
                                 dest=self.__install_path, _from=_from))
        # No need to workaround compiler wrapper issue for the runtime.
        # Copy the dictionary so not to modify the original.
        vars = dict(self.__environment_variables)
        del vars['PROFILE_POSTLIB']
        instructions.append(environment(variables=vars))
        return instructions
