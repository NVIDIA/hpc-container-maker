# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
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

"""DOCA OFED building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from packaging.version import Version
import posixpath

import hpccm.config
import hpccm.templates.annotate

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.packages import packages
from hpccm.common import cpu_arch, linux_distro
from hpccm.primitives.comment import comment
from hpccm.primitives.label import label

class doca_ofed(bb_base, hpccm.templates.annotate, hpccm.templates.rm,
                hpccm.templates.tar, hpccm.templates.wget):
    """The `doca_ofed` building block downloads and installs the [NVIDIA
    DOCA Software Framework](https://developer.nvidia.com/networking/doca).

    # Parameters

    annotate: Boolean flag to specify whether to include annotations
    (labels).  The default is False.

    archlabel: The CPU architecture label assigned by Mellanox to the
    package repository.  The default value is `x86_64` for x86_64
    processors and `arm64-sbsa` for aarch64 processors.

    oslabel: The Linux distribution label assigned by Mellanox to the
    package repository.  For Ubuntu, the default value is
    `ubuntuXX.04` where `XX` is derived from the base image.  For
    RHEL-base Linux distributions, the default value is `rhelX`.

    ospackages: List of OS packages to install prior to installing
    DOCA OFED.  The default values are `ca-certificates`, `gnupg`, and
    `wget`.

    packages: List of packages to install from DOCA.  For
    Ubuntu, the default values are `ibverbs-providers`,
    `ibverbs-utils` `libibmad-dev`, `libibmad5`, `libibumad3`,
    `libibumad-dev`, `libibverbs-dev` `libibverbs1`, `librdmacm-dev`,
    and `librdmacm1`.  For RHEL-based Linux distributions, the default
    values are `libibumad`, `libibverbs`, `libibverbs-utils`,
    `librdmacm`, `rdma-core`, and `rdma-core-devel`.

    version: The version of DOCA OFED to download.  The default value
    is `3.2.0`.

    # Examples

    ```python
    doca_ofed(version='3.2.0')
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(doca_ofed, self).__init__(**kwargs)

        self.__archlabel = kwargs.get('archlabel', '') # Filled in by __cpu_arch
        self.__extra_opts = []
        self.__key = 'https://linux.mellanox.com/public/repo/doca/GPG-KEY-Mellanox.pub'
        self.__oslabel = kwargs.get('oslabel', '') # Filled in by __distro
        self.__ospackages = kwargs.get('ospackages',
                                       ['ca-certificates', 'gnupg', 'wget'])
        self.__packages = kwargs.get('packages', []) # Filled in by __distro
        self.__version = kwargs.get('version', '3.2.0')

        # Add annotation
        self.add_annotation('version', self.__version)

        # Set the CPU architecture specific parameters
        self.__cpu_arch()

        # Set the Linux distribution specific parameters
        self.__distro()

        # Fill in container instructions
        self.__instructions()

    def __instructions(self):
        """Fill in container instructions"""

        self += comment('DOCA OFED version {}'.format(self.__version))

        self += packages(ospackages=self.__ospackages)

        self += packages(
            apt_keys=[self.__key],
            apt_repositories=['deb [signed-by=/usr/share/keyrings/{3}] https://linux.mellanox.com/public/repo/doca/{0}/{1}/{2}/ ./'.format(self.__version, self.__oslabel, self.__archlabel, posixpath.basename(self.__key).replace('.pub', '.gpg')) if self.__key else None],
            extra_opts=self.__extra_opts,
            ospackages=self.__packages,
            yum_keys=[self.__key] if self.__key else None,
            yum_repositories=['https://linux.mellanox.com/public/repo/doca/{0}/{1}/{2}'.format(self.__version, self.__oslabel, self.__archlabel)])

        self += label(metadata=self.annotate_step())

    def __cpu_arch(self):
        """Based on the CPU architecture, set values accordingly.  A user
           specified value overrides any defaults."""

        if not self.__archlabel:
            if hpccm.config.g_cpu_arch == cpu_arch.AARCH64:
                self.__archlabel = 'arm64-sbsa'
            elif hpccm.config.g_cpu_arch == cpu_arch.X86_64:
                self.__archlabel = 'x86_64'
            else: # pragma: no cover
                raise RuntimeError('Unknown CPU architecture')

    def __distro(self):
        """Based on the Linux distribution, set values accordingly.  A user
           specified value overrides any defaults."""

        if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
            if not self.__oslabel:
                if hpccm.config.g_linux_version >= Version('24.0'):
                    self.__oslabel = 'ubuntu24.04'
                elif hpccm.config.g_linux_version >= Version('22.0'):
                    self.__oslabel = 'ubuntu22.04'
                else:
                    self.__oslabel = 'ubuntu20.04'

            if not self.__packages:
                self.__packages = ['libibverbs1', 'libibverbs-dev',
                                   'ibverbs-providers', 'ibverbs-utils',
                                   'libibmad5',  'libibmad-dev',
                                   'libibumad3', 'libibumad-dev',
                                   'librdmacm-dev', 'librdmacm1']

        elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
            if not self.__oslabel:
                if hpccm.config.g_linux_version >= Version('10.0'):
                    self.__oslabel = 'rhel10'
                    # The DOCA OFED GPG key is rejected by the Rockylinux 10
                    # security policy as insecure.  Do not check the
                    # package signatures.
                    self.__key = None
                    self.__extra_opts = ['--nogpgcheck']
                elif hpccm.config.g_linux_version >= Version('9.0'):
                    self.__oslabel = 'rhel9'
                else:
                    self.__oslabel = 'rhel8'

            if not self.__packages:
                    self.__packages = ['libibverbs', 'libibverbs-utils',
                                       'libibumad', 'librdmacm',
                                       'rdma-core', 'rdma-core-devel']

        else: # pragma: no cover
            raise RuntimeError('Unknown Linux distribution')

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples

        ```python
        d = doca_ofed(...)
        Stage0 += d
        Stage1 += d.runtime()
        ```
        """

        return str(self)
