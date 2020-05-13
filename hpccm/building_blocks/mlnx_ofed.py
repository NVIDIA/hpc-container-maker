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

"""Mellanox OFED building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from distutils.version import LooseVersion, StrictVersion
import posixpath

import hpccm.config
import hpccm.templates.annotate
import hpccm.templates.rm
import hpccm.templates.tar
import hpccm.templates.wget

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.packages import packages
from hpccm.common import cpu_arch, linux_distro
from hpccm.primitives.comment import comment
from hpccm.primitives.copy import copy
from hpccm.primitives.label import label
from hpccm.primitives.shell import shell

class mlnx_ofed(bb_base, hpccm.templates.annotate, hpccm.templates.rm,
                hpccm.templates.tar, hpccm.templates.wget):
    """The `mlnx_ofed` building block downloads and installs the [Mellanox
    OpenFabrics Enterprise Distribution for
    Linux](http://www.mellanox.com/page/products_dyn?product_family=26).

    # Parameters

    annotate: Boolean flag to specify whether to include annotations
    (labels).  The default is False.

    oslabel: The Linux distribution label assigned by Mellanox to the
    tarball.  For Ubuntu, the default value is `ubuntu16.04`.  For
    RHEL-based Linux distributions, the default value is `rhel7.2` for
    x86_64 processors and `rhel7.6alternate` for aarch64 processors.

    ospackages: List of OS packages to install prior to installing
    OFED.  For Ubuntu, the default values are `findutils`,
    `libnl-3-200`, `libnl-route-3-200`, `libnuma1`, and `wget`.  For
    RHEL-based 7.x distributions, the default values are `findutils`,
    `libnl`, `libnl3`, `numactl-libs`, and `wget`.  For RHEL-based 8.x
    distributions, the default values are `findutils`, `libnl3`,
    `numactl-libs`, and `wget`.

    packages: List of packages to install from Mellanox OFED.  For
    version 5.0 and later on Ubuntu, `ibverbs-providers`,
    `ibverbs-utils` `libibmad-dev`, `libibmad5`, `libibumad3`,
    `libibumad-dev`, `libibverbs-dev` `libibverbs1`, `librdmacm-dev`,
    and `librdmacm1`. For earlier versions on Ubuntu, the default
    values are `libibverbs1`, `libibverbs-dev`, `libibmad`,
    `libibmad-devel`, `libibumad`, `libibumad-devel`, `libmlx4-1`,
    `libmlx4-dev`, `libmlx5-1`, `libmlx5-dev`, `librdmacm1`,
    `librdmacm-dev`, and `ibverbs-utils`.  For version 5.0 and later
    on RHEL-based Linux distributions, the default values are
    `libibumad`, `libibverbs`, `libibverbs-utils`, `librdmacm`,
    `rdma-core`, and `rdma-core-devel`. For earlier versions on
    RHEL-based Linux distributions, the default values are
    `libibverbs`, `libibverbs-devel`, `libibverbs-utils`, `libibmad`,
    `libibmad-devel`, `libibumad`, `libibumad-devel`, `libmlx4`,
    `libmlx4-devel`, `libmlx5`, `libmlx5-devel`, `librdmacm`, and
    `librdmacm-devel`.

    prefix: The top level install location.  Instead of installing the
    packages via the package manager, they will be extracted to this
    location.  This option is useful if multiple versions of Mellanox
    OFED need to be installed.  The environment must be manually
    configured to recognize the Mellanox OFED location, e.g., in the
    container entry point.  The default value is empty, i.e., install
    via the package manager to the standard system locations.

    version: The version of Mellanox OFED to download.  The default
    value is `5.0-2.1.8.0`.

    # Examples

    ```python
    mlnx_ofed(version='4.2-1.0.0.0')
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(mlnx_ofed, self).__init__(**kwargs)

        self.__deppackages = [] # Filled in by __distro()
        self.__key = 'https://www.mellanox.com/downloads/ofed/RPM-GPG-KEY-Mellanox'
        self.__oslabel = kwargs.get('oslabel', '')
        self.__ospackages = kwargs.get('ospackages',
                                       ['ca-certificates', 'gnupg', 'wget'])
        self.__packages = kwargs.get('packages', [])
        self.__prefix = kwargs.get('prefix', None)
        self.__symlink = kwargs.get('symlink', False)
        self.__version = kwargs.get('version', '5.0-2.1.8.0')

        # Add annotation
        self.add_annotation('version', self.__version)

        # Set the Linux distribution specific parameters
        self.__distro()

        # Fill in container instructions
        self.__instructions()

    def __instructions(self):
        """Fill in container instructions"""

        self += comment('Mellanox OFED version {}'.format(self.__version))

        if self.__prefix:
            self += packages(ospackages=self.__deppackages + self.__ospackages)
        else:
            self += packages(ospackages=self.__ospackages)

        self += packages(
            apt_keys=[self.__key],
            apt_repositories=['https://linux.mellanox.com/public/repo/mlnx_ofed/{0}/{1}/mellanox_mlnx_ofed.list'.format(self.__version, self.__oslabel)],
            download=bool(self.__prefix),
            extract=self.__prefix,
            ospackages=self.__packages,
            yum_keys=[self.__key],
            yum_repositories=['https://linux.mellanox.com/public/repo/mlnx_ofed/{0}/{1}/mellanox_mlnx_ofed.repo'.format(self.__version, self.__oslabel)])

        if self.__prefix:
            commands = []
            if self.__symlink:
                commands.append('mkdir -p {0} && cd {0}'.format(
                    posixpath.join(self.__prefix, 'lib')))
                # Prune the symlink directory itself and any debug
                # libraries
                commands.append('find .. -path ../lib -prune -o -name "*valgrind*" -prune -o -name "lib*.so*" -exec ln -s {} \;')
                commands.append('cd {0} && ln -s usr/bin bin && ln -s usr/include include'.format(
                    self.__prefix))

            # Suppress warnings from libibverbs
            commands.append('mkdir -p /etc/libibverbs.d')

            self += shell(commands=commands)

        self += label(metadata=self.annotate_step())

    def __distro(self):
        """Based on the Linux distribution, set values accordingly.  A user
           specified value overrides any defaults."""

        if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
            self.__deppackages = ['libnl-3-200', 'libnl-route-3-200',
                                 'libnuma1']

            if not self.__oslabel:
                if hpccm.config.g_linux_version >= StrictVersion('18.0'):
                    self.__oslabel = 'ubuntu18.04'
                else:
                    self.__oslabel = 'ubuntu16.04'

            if not self.__packages:
                if LooseVersion(self.__version) >= LooseVersion('5.0'):
                    # Uses UPSTREAM libs
                    self.__packages = ['libibverbs1', 'libibverbs-dev',
                                       'ibverbs-providers', 'ibverbs-utils',
                                       'libibmad5',  'libibmad-dev',
                                       'libibumad3', 'libibumad-dev',
                                       'librdmacm-dev', 'librdmacm1']
                else:
                    # Uses MLNX_OFED libs
                    self.__packages = ['libibverbs1', 'libibverbs-dev',
                                       'ibverbs-utils',
                                       'libibmad',  'libibmad-devel',
                                       'libibumad', 'libibumad-devel',
                                       'libmlx4-1', 'libmlx4-dev',
                                       'libmlx5-1', 'libmlx5-dev',
                                       'librdmacm-dev', 'librdmacm1']

        elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
            if hpccm.config.g_linux_version >= StrictVersion('8.0'):
                self.__deppackages = ['libnl3', 'numactl-libs']
            else:
                self.__deppackages = ['libnl', 'libnl3', 'numactl-libs']

            if not self.__oslabel:
                if hpccm.config.g_linux_version >= StrictVersion('8.0'):
                    self.__oslabel = 'rhel8.0'
                else:
                    if hpccm.config.g_cpu_arch == cpu_arch.AARCH64:
                        self.__oslabel = 'rhel7.6alternate'
                    else:
                        self.__oslabel = 'rhel7.2'

            if not self.__packages:
                if LooseVersion(self.__version) >= LooseVersion('5.0'):
                    # Uses UPSTREAM libs
                    self.__packages = ['libibverbs', 'libibverbs-utils',
                                       'libibumad', 'librdmacm',
                                       'rdma-core', 'rdma-core-devel']
                else:
                    # Uses MLNX_OFED libs
                    self.__packages = ['libibverbs', 'libibverbs-devel',
                                       'libibverbs-utils',
                                       'libibmad', 'libibmad-devel',
                                       'libibumad', 'libibumad-devel',
                                       'libmlx4', 'libmlx4-devel',
                                       'libmlx5', 'libmlx5-devel',
                                       'librdmacm-devel', 'librdmacm']

        else: # pragma: no cover
            raise RuntimeError('Unknown Linux distribution')

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples

        ```python
        m = mlnx_ofed(...)
        Stage0 += m
        Stage1 += m.runtime()
        ```
        """
        if self.__prefix:
            instructions = []
            instructions.append(comment('Mellanox OFED version {}'.format(
                self.__version)))

            if self.__deppackages:
                instructions.append(packages(ospackages=self.__deppackages))

            # Suppress warnings from libibverbs
            instructions.append(shell(commands=['mkdir -p /etc/libibverbs.d']))

            instructions.append(copy(_from=_from, dest=self.__prefix,
                                     src=self.__prefix))
            return '\n'.join(str(x) for x in instructions)
        else:
            return str(self)
