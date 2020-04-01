# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
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

"""NVIDIA Nsight Systems building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from distutils.version import StrictVersion

import hpccm.config

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.packages import packages
from hpccm.common import cpu_arch, linux_distro
from hpccm.primitives.comment import comment

class nsight_systems(bb_base):
    """The `nsight_systems` building block downloads and installs the
    [NVIDIA Nsight Systems
    profiler]](https://developer.nvidia.com/nsight-systems).

    # Parameters

    cli: Boolean flag to specify whether the command line only (CLI)
    package should be installed.  The default is True.

    version: The version of Nsight Systems to install.  The default
    value is `2020.2.1`.

    # Examples

    ```python
    nsight_systems(version='2020.2.1')
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(nsight_systems, self).__init__(**kwargs)

        self.__arch_key_label = ''   # Filled in __cpu_arch
        self.__arch_repo_label = ''  # Filled in __cpu_arch
        self.__cli = kwargs.get('cli', True)
        self.__distro_label = ''     # Filled in by __distro
        self.__ospackages = kwargs.get('ospackages', [])
        self.__version = kwargs.get('version', '2020.2.1')

        # Set the CPU architecture specific parameters
        self.__cpu_arch()

        # Set the Linux distribution specific parameters
        self.__distro()

        # Fill in container instructions
        self.__instructions()

    def __instructions(self):
        """Fill in container instructions"""

        self += comment('NVIDIA Nsight Systems {}'.format(self.__version))

        if self.__ospackages:
            self += packages(ospackages=self.__ospackages)

        if self.__cli:
            package = 'nsight-systems-cli-{}'.format(self.__version)
        else:
            package = 'nsight-systems-{}'.format(self.__version)

        self += packages(
            apt_keys=['https://developer.download.nvidia.com/compute/cuda/repos/{0}/{1}/7fa2af80.pub'.format(self.__distro_label, self.__arch_key_label)],
            apt_repositories=['deb https://developer.download.nvidia.com/devtools/repo-deb/{}/ /'.format(self.__arch_repo_label)],
            ospackages=[package],
            yum_keys=['https://developer.download.nvidia.com/compute/cuda/repos/{0}/{1}/7fa2af80.pub'.format(self.__distro_label, self.__arch_key_label)],
            yum_repositories=['https://developer.download.nvidia.com/devtools/repo-rpm/{}'.format(self.__arch_repo_label)])

    def __cpu_arch(self):
        """Based on the CPU architecture, set values accordingly.  A user
        specified value overrides any defaults."""

        if hpccm.config.g_cpu_arch == cpu_arch.AARCH64:
            self.__arch_repo_label = 'arm64'
            self.__arch_key_label = 'x86_64' # https://developer.nvidia.com/cuda-toolkit/arm
        elif hpccm.config.g_cpu_arch == cpu_arch.PPC64LE:
            self.__arch_repo_label = 'ppc64'
            if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
                self.__arch_key_label = 'ppc64el'
            else:
                self.__arch_key_label = 'ppc64le'
        elif hpccm.config.g_cpu_arch == cpu_arch.X86_64:
            self.__arch_repo_label = 'x86_64'
            self.__arch_key_label = 'x86_64'
        else: # pragma: no cover
            raise RuntimeError('Unknown CPU architecture')

    def __distro(self):
        """Based on the Linux distribution, set values accordingly.  A user
        specified value overrides any defaults."""

        if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
            if not self.__ospackages:
                self.__ospackages = ['apt-transport-https', 'ca-certificates',
                                     'gnupg', 'wget']

            if hpccm.config.g_linux_version >= StrictVersion('18.0'):
                self.__distro_label = 'ubuntu1804'
            else:
                self.__distro_label = 'ubuntu1604'

        elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
            if hpccm.config.g_linux_version >= StrictVersion('8.0'):
                self.__distro_label = 'rhel8'
            else:
                self.__distro_label = 'rhel7'

        else: # pragma: no cover
            raise RuntimeError('Unknown Linux distribution')
