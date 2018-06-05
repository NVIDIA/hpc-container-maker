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

"""MKL building block"""

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
from hpccm.yum import yum

class mkl(wget):
    """MKL building block"""

    def __init__(self, **kwargs):
        """Initialize building block"""

        # Trouble getting MRO with kwargs working correctly, so just call
        # the parent class constructors manually for now.
        #super(mkl, self).__init__(**kwargs)
        wget.__init__(self, **kwargs)

        # By setting this value to True, you agree to the
        # corresponding Intel End User License Agreement
        # (https://software.intel.com/en-us/articles/end-user-license-agreement)
        self.__eula = kwargs.get('eula', False)

        self.__mklvars = kwargs.get('mklvars', True)
        self.__ospackages = kwargs.get('ospackages', [])
        self.version = kwargs.get('version', '2018.3-051')

        self.__bashrc = ''      # Filled in by __distro()

        # Set the Linux distribution specific parameters
        self.__distro()

    def __str__(self):
        """String representation of the building block"""

        instructions = []
        instructions.append(comment('MKL version {}'.format(self.version)))

        if self.__ospackages:
            instructions.append(packages(ospackages=self.__ospackages))

        if not self.__eula:
            raise RuntimeError('Intel EULA was not accepted.  To accept, see the documentation for this building block')

        instructions.append(packages(
            apt_keys=['https://apt.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS-2019.PUB'],
            apt_repositories=['deb https://apt.repos.intel.com/mkl all main'],
            ospackages=['intel-mkl-64bit-{}'.format(self.version)],
            yum_keys=['https://yum.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS-2019.PUB'],
            yum_repositories=['https://yum.repos.intel.com/mkl/setup/intel-mkl.repo']))

        # Set the environment
        if self.__mklvars:
            # Source the mklvars environment script when starting the
            # container, but the variables not be available for any
            # subsequent build steps.
            instructions.append(shell(commands=['echo "source /opt/intel/mkl/bin/mklvars.sh intel64" >> {}'.format(self.__bashrc)]))
        else:
            # Set the environment so that it will be available to
            # subsequent build steps and when starting the container,
            # but this may miss some things relative to the mklvars
            # environment script.
            instructions.append(environment(variables={
                'CPATH': '/opt/intel/mkl/include:$CPATH',
                'LD_LIBRARY_PATH': '/opt/intel/mkl/lib/intel64:/opt/intel/lib/intel64:$LD_LIBRARY_PATH',
                'LIBRARY_PATH': '/opt/intel/mkl/lib/intel64:/opt/intel/lib/intel64:$LIBRARY_PATH',
                'MKLROOT': '/opt/intel/mkl'}))

        return '\n'.join(str(x) for x in instructions)

    def __distro(self):
        """Based on the Linux distribution, set values accordingly.  A user
        specified value overrides any defaults."""

        if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
            if not self.__ospackages:
                self.__ospackages = ['apt-transport-https', 'ca-certificates',
                                     'wget']

            self.__bashrc = '/etc/bash.bashrc'

        elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
            if not self.__ospackages:
                self.__ospackages = []

            self.__bashrc = '/etc/bashrc'

        else: # pragma: no cover
            raise RuntimeError('Unknown Linux distribution')

    def runtime(self, _from='0'):
        """Install the runtime from a full build in a previous stage.  In this
           case thre is no difference between the runtime and the full
           build."""
        return self
