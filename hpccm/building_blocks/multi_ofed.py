# Copyright (c) 2019, NVIDIA CORPORATION.  All rights reserved.
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

"""'multi' OFED building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from distutils.version import StrictVersion
import posixpath

import hpccm.config
import hpccm.templates.annotate

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.mlnx_ofed import mlnx_ofed
from hpccm.building_blocks.ofed import ofed
from hpccm.building_blocks.packages import packages
from hpccm.common import linux_distro
from hpccm.primitives.comment import comment
from hpccm.primitives.copy import copy
from hpccm.primitives.label import label
from hpccm.primitives.shell import shell

class multi_ofed(bb_base, hpccm.templates.annotate):
    """The `multi_ofed` building block downloads and installs multiple
    versions of the OpenFabrics Enterprise Distribution (OFED). Please
    refer to the [`mlnx_ofed`](#mlnx_ofed) and [`ofed`](#ofed)
    building blocks for more information.

    # Parameters

    annotate: Boolean flag to specify whether to include annotations
    (labels).  The default is False.

    inbox: Boolean flag to specify whether to install the 'inbox' OFED
    distributed by the Linux distribution.  The default is True.

    mlnx_oslabel: The Linux distribution label assigned by Mellanox to
    the tarball. Please see the corresponding
    [`mlnx_ofed`](#mlnx_ofed) parameter for more information.

    mlnx_packages: List of packages to install from Mellanox
    OFED. Please see the corresponding [`mlnx_ofed`](#mlnx_ofed)
    parameter for more information.

    mlnx_versions: A list of [Mellanox OpenFabrics Enterprise Distribution for Linux](http://www.mellanox.com/page/products_dyn?product_family=26)
    versions to install.  The default values are `3.4-2.0.0.0`,
    `4.0-2.0.0.1`, `4.1-1.0.2.0`, `4.2-1.2.0.0`, `4.3-1.0.1.0`,
    `4.4-1.0.0.0`, `4.5-1.0.1.0`, `4.6-1.0.1.1`, `4.7-3.2.9.0`, and
    `5.0-2.1.8.0`.

    ospackages: List of OS packages to install prior to installing
    OFED.  For Ubuntu, the default values are `libnl-3-200`,
    `libnl-route-3-200`, and `libnuma1`.  For RHEL-based Linux
    distributions, the default values are `libnl`, `libnl3`, and
    `numactl-libs`.

    prefix: The top level install location.  The OFED packages will be
    extracted to this location as subdirectories named for the
    respective Mellanox OFED version, or `inbox` for the 'inbox'
    OFED. The environment must be manually configured to recognize the
    desired OFED location, e.g., in the container entry point. The
    default value is `/usr/local/ofed`.

    # Examples

    ```python
    multi_ofed(inbox=True, mlnx_versions=['4.5-1.0.1.0', '4.6-1.0.1.1'],
               prefix='/usr/local/ofed')
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(multi_ofed, self).__init__(**kwargs)

        self.__inbox = kwargs.get('inbox', True)
        self.__mlnx_oslabel = kwargs.get('mlnx_oslabel', '')
        self.__mlnx_packages = kwargs.get('mlnx_packages', [])
        self.__mlnx_versions = kwargs.get('mlnx_versions',
                                          ['3.4-2.0.0.0', '4.0-2.0.0.1',
                                           '4.1-1.0.2.0', '4.2-1.2.0.0',
                                           '4.3-1.0.1.0', '4.4-1.0.0.0',
                                           '4.5-1.0.1.0', '4.6-1.0.1.1',
                                           '4.7-3.2.9.0', '5.0-2.1.8.0'])
        self.__ospackages = kwargs.get('ospackages', [])
        self.__prefix = kwargs.get('prefix', '/usr/local/ofed')
        self.__symlink = kwargs.get('symlink', False)

        self.__commands = []

        # Set the Linux distribution specific parameters
        self.__distro()

        # Fill in container instructions
        self.__instructions()

    def __distro(self):
        if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
            if not self.__ospackages:
                self.__ospackages = ['libnl-3-200', 'libnl-route-3-200',
                                     'libnuma1']
        elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
            if not self.__ospackages:
                if hpccm.config.g_linux_version >= StrictVersion('8.0'):
                    self.__ospackages = ['libnl3', 'numactl-libs']
                else:
                    self.__ospackages = ['libnl', 'libnl3', 'numactl-libs']
        else: # pragma: no cover
            raise RuntimeError('Unknown Linux distribution')

    def __instructions(self):
        """Fill in container instructions"""

        # Mellanox OFED
        for version in self.__mlnx_versions:
            self += mlnx_ofed(annotate=False,
                              oslabel=self.__mlnx_oslabel,
                              packages=self.__mlnx_packages,
                              prefix=posixpath.join(self.__prefix, version),
                              symlink=self.__symlink,
                              version=version)

        # Inbox OFED
        if self.__inbox:
            self += ofed(prefix=posixpath.join(self.__prefix, 'inbox'),
                         symlink=self.__symlink)
            self += shell(commands=['ln -s {0} {1}'.format(
                posixpath.join(self.__prefix, 'inbox'),
                posixpath.join(self.__prefix, '5.0-0'))])

        # Annotations
        self.add_annotation('mlnx_versions', ', '.join(self.__mlnx_versions))
        self.add_annotation('inbox', self.__inbox)
        self += label(metadata=self.annotate_step())

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.
        """

        instructions = []
        instructions.append(comment('OFED'))

        if self.__ospackages:
            instructions.append(packages(ospackages=self.__ospackages))

        # Suppress warnings from libibverbs
        instructions.append(shell(commands=['mkdir -p /etc/libibverbs.d']))

        instructions.append(copy(_from=_from, dest=self.__prefix,
                                 src=self.__prefix))
        return '\n'.join(str(x) for x in instructions)
