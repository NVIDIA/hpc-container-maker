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
import logging # pylint: disable=unused-import

import hpccm.config

from hpccm.building_blocks.packages import packages
from hpccm.common import linux_distro
from hpccm.primitives.comment import comment

class ofed(object):
    """The `ofed` building block installs the OpenFabrics Enterprise
    Distribution packages that are part of the Linux distribution.

    For Ubuntu 16.04, the following packages are installed:
    `dapl2-utils`, `ibutils`, `ibverbs-utils`, `infiniband-diags`,
    `libdapl-dev`, `libibcm-dev`, `libibmad5`, `libibmad-dev`,
    `libibverbs1`, `libibverbs-dev`, `libmlx4-1`, `libmlx4-dev`,
    `libmlx5-1`, `libmlx5-dev`, `librdmacm1`, `librdmacm-dev`,
    `opensm`, and `rdmacm-utils`.

    For Ubuntu 18.04, the following packages are installed:
    `dapl2-utils`, `ibutils`, `ibverbs-utils`, `infiniband-diags`,
    `libdapl-dev`, `libibmad5`, `libibmad-dev`, `libibverbs1`,
    `libibverbs-dev`, `librdmacm1`, `librdmacm-dev`, `opensm`, and
    `rdmacm-utils`.

    For RHEL-based Linux distributions, the following packages are
    installed: `dapl`, `dapl-devel`, `ibutils`, `libibcm`, `libibmad`,
    `libibmad-devel`, `libmlx5`, `libibumad`, `libibverbs`,
    `libibverbs-utils`, `librdmacm`, `opensm`, `rdma-core`, and
    `rdma-core-devel`.

    # Parameters

    None

    # Examples

    ```python
    ofed()
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        # Trouble getting MRO with kwargs working correctly, so just call
        # the parent class constructors manually for now.
        #super(ofed, self).__init__(**kwargs)

        if (hpccm.config.g_linux_distro == linux_distro.UBUNTU and
            hpccm.config.g_linux_version >= StrictVersion('18.0')):
            self.__ospackages_deb = ['dapl2-utils', 'ibutils', 'ibverbs-utils',
                                     'infiniband-diags', 'libdapl-dev',
                                     'libibmad5', 'libibmad-dev',
                                     'libibverbs1', 'libibverbs-dev',
                                     'librdmacm1', 'librdmacm-dev',
                                     'opensm', 'rdmacm-utils']
        else:
            self.__ospackages_deb = ['dapl2-utils', 'ibutils', 'ibverbs-utils',
                                     'infiniband-diags', 'libdapl-dev',
                                     'libibcm-dev',
                                     'libibmad5', 'libibmad-dev',
                                     'libibverbs1', 'libibverbs-dev',
                                     'libmlx4-1', 'libmlx4-dev',
                                     'libmlx5-1', 'libmlx5-dev',
                                     'librdmacm1', 'librdmacm-dev',
                                     'opensm', 'rdmacm-utils']

        self.__ospackages_rpm = ['dapl', 'dapl-devel', 'ibutils', 'libibcm',
                                 'libibmad', 'libibmad-devel', 'libmlx5',
                                 'libibumad', 'libibverbs', 'libibverbs-utils',
                                 'librdmacm', 'opensm', 'rdma-core',
                                 'rdma-core-devel']

    def __str__(self):
        """String representation of the building block"""
        instructions = []
        instructions.append(comment('OFED'))
        instructions.append(packages(apt=self.__ospackages_deb,
                                     yum=self.__ospackages_rpm))
        return '\n'.join(str(x) for x in instructions)

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
        return str(self)
