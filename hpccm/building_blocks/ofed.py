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

"""OFED building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from distutils.version import StrictVersion
import posixpath

import hpccm.config

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.packages import packages
from hpccm.common import cpu_arch, linux_distro
from hpccm.primitives.comment import comment
from hpccm.primitives.copy import copy
from hpccm.primitives.shell import shell

class ofed(bb_base):
    """The `ofed` building block installs the OpenFabrics Enterprise
    Distribution packages that are part of the Linux distribution.

    For Ubuntu 16.04, the following packages are installed:
    `dapl2-utils`, `ibutils`, `ibverbs-utils`, `infiniband-diags`,
    `libdapl2`, `libdapl-dev`, `libibcm1`, `libibcm-dev`, `libibmad5`,
    `libibmad-dev`, `libibverbs1`, `libibverbs-dev`, `libmlx4-1`,
    `libmlx4-dev`, `libmlx5-1`, `libmlx5-dev`, `librdmacm1`,
    `librdmacm-dev`, and `rdmacm-utils`.  For Ubuntu 16.04 and aarch64
    processors, the `dapl2-utils`, `libdapl2`, `libdapl-dev`,
    `libibcm1` and `libibcm-dev` packages are not installed because
    they are not available.  For Ubuntu 16.04 and ppc64le processors,
    the `libibcm1` and `libibcm-dev` packages are not installed
    because they are not available.

    For Ubuntu 18.04, the following packages are installed:
    `dapl2-utils`, `ibutils`, `ibverbs-providers`, `ibverbs-utils`,
    `infiniband-diags`, `libdapl2`, `libdapl-dev`, `libibmad5`,
    `libibmad-dev`, `libibverbs1`, `libibverbs-dev`, `librdmacm1`,
    `librdmacm-dev`, and `rdmacm-utils`.

    For RHEL-based 7.x distributions, the following packages are
    installed: `dapl`, `dapl-devel`, `ibutils`, `libibcm`, `libibmad`,
    `libibmad-devel`, `libmlx5`, `libibumad`, `libibverbs`,
    `libibverbs-utils`, `librdmacm`, `rdma-core`, and
    `rdma-core-devel`.

    For RHEL-based 8.x distributions, the following packages are
    installed: `libibmad`, `libibmad-devel`, `libmlx5`, `libibumad`,
    `libibverbs`, `libibverbs-utils`, `librdmacm`, `rdma-core`, and
    `rdma-core-devel`.

    # Parameters

    prefix: The top level install location. Install of installing the
    packages via the package manager, they will be extracted to this
    location. This option is useful if multiple versions of OFED need
    to be installed. The environment must be manually configured to
    recognize the OFED location, e.g., in the container entry
    point. The default value is empty, i.e., install via the package
    manager to the standard system locations.

    # Examples

    ```python
    ofed()
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(ofed, self).__init__(**kwargs)

        self.__deppackages = []  # Filled in by __distro()
        self.__extra_opts = []   # Filled in by __distro()
        self.__ospackages = []   # Filled in by __distro()
        self.__powertools = False # enable the CentOS PowerTools repo
        self.__prefix = kwargs.get('prefix', None)
        self.__symlink = kwargs.get('symlink', False)
        self.__wd = '/var/tmp'

        # Set the Linux distribution specific parameters
        self.__distro()

        # Fill in container instructions
        self.__instructions()

    def __distro(self):
        """Based on the Linux distribution, set values accordingly.  A user
           specified value overrides any defaults."""

        if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
            self.__deppackages = ['libnl-3-200', 'libnl-route-3-200',
                                 'libnuma1']

            if hpccm.config.g_linux_version >= StrictVersion('18.0'):
                # Give priority to packages from the Ubuntu repositories over
                # vendor repositories
                self.__extra_opts = ['-t bionic']

                self.__ospackages= ['dapl2-utils', 'ibutils',
                                    'ibverbs-providers', 'ibverbs-utils',
                                    'infiniband-diags',
                                    'libdapl2', 'libdapl-dev',
                                    'libibmad5', 'libibmad-dev',
                                    'libibverbs1', 'libibverbs-dev',
                                    'librdmacm1', 'librdmacm-dev',
                                    'rdmacm-utils']
            else:
                # Give priority to packages from the Ubuntu repositories over
                # vendor repositories
                self.__extra_opts = ['-t xenial']

                self.__ospackages = ['dapl2-utils', 'ibutils', 'ibverbs-utils',
                                     'infiniband-diags',
                                     'libdapl2', 'libdapl-dev',
                                     'libibcm1', 'libibcm-dev',
                                     'libibmad5', 'libibmad-dev',
                                     'libibverbs1', 'libibverbs-dev',
                                     'libmlx4-1', 'libmlx4-dev',
                                     'libmlx5-1', 'libmlx5-dev',
                                     'librdmacm1', 'librdmacm-dev',
                                     'rdmacm-utils']

                if hpccm.config.g_cpu_arch == cpu_arch.AARCH64:
                    # Ubuntu 16.04 for ARM is missing these packages
                    for missing in ['dapl2-utils', 'libdapl2', 'libdapl-dev',
                                    'libibcm1', 'libibcm-dev']:
                        if missing in self.__ospackages:
                            self.__ospackages.remove(missing)
                elif hpccm.config.g_cpu_arch == cpu_arch.PPC64LE:
                    # Ubuntu 16.04 for Power is missing these packages
                    for missing in ['libibcm1', 'libibcm-dev']:
                        if missing in self.__ospackages:
                            self.__ospackages.remove(missing)
        elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
            self.__extra_opts = [r'--disablerepo=mlnx\*']

            if hpccm.config.g_linux_version >= StrictVersion('8.0'):
                self.__deppackages = ['libnl3', 'numactl-libs']
                self.__ospackages = ['libibmad', 'libibmad-devel',
                                     'libibumad', 'libibverbs',
                                     'libibverbs-utils', 'libmlx5',
                                     'librdmacm',
                                     'rdma-core', 'rdma-core-devel']
                self.__powertools = True
            else:
                self.__deppackages = ['libnl', 'libnl3', 'numactl-libs']
                self.__ospackages = ['dapl', 'dapl-devel', 'ibutils',
                                     'libibcm', 'libibmad', 'libibmad-devel',
                                     'libmlx5', 'libibumad', 'libibverbs',
                                     'libibverbs-utils', 'librdmacm',
                                     'rdma-core', 'rdma-core-devel']
        else: # pragma: no cover
            raise RuntimeError('Unknown Linux distribution')

    def __instructions(self):
        """Fill in container instructions"""
        self += comment('OFED')
        if self.__prefix:
            commands = []

            # Extract to a prefix - not a "real" package manager install
            self += packages(ospackages=self.__deppackages)
            self += packages(download=True, extra_opts=self.__extra_opts,
                             extract=self.__prefix,
                             ospackages=self.__ospackages,
                             powertools=self.__powertools)

            # library symlinks
            if self.__symlink:
                self.__deppackages.append('findutils')

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
        else:
            # Install packages using package manager
            self += packages(extra_opts=self.__extra_opts,
                             ospackages=self.__ospackages,
                             powertools=self.__powertools)

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples

        ```python
        o = ofed(...)
        Stage0 += o
        Stage1 += o.runtime()
        ```
        """
        if self.__prefix:
            instructions = []
            instructions.append(comment('OFED'))

            if self.__deppackages:
                instructions.append(packages(ospackages=self.__deppackages))

            # Suppress warnings from libibverbs
            instructions.append(shell(commands=['mkdir -p /etc/libibverbs.d']))

            instructions.append(copy(_from=_from, dest=self.__prefix,
                                     src=self.__prefix))
            return '\n'.join(str(x) for x in instructions)
        else:
            return str(self)
