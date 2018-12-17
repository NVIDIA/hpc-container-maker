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

from distutils.version import StrictVersion
import logging # pylint: disable=unused-import
import os

import hpccm.config

from hpccm.building_blocks.packages import packages
from hpccm.common import linux_distro
from hpccm.primitives.comment import comment
from hpccm.primitives.shell import shell
from hpccm.templates.tar import tar
from hpccm.templates.wget import wget

class mlnx_ofed(tar, wget):
    """The `mlnx_ofed` building block downloads and installs the [Mellanox
    OpenFabrics Enterprise Distribution for
    Linux](http://www.mellanox.com/page/products_dyn?product_family=26).

    # Parameters

    oslabel: The Linux distribution label assigned by Mellanox to the
    tarball.  For Ubuntu, the default value is `ubuntu16.04`.  For
    RHEL-based Linux distributions, the default value is `rhel7.2`.

    ospackages: List of OS packages to install prior to installing
    OFED.  For Ubuntu, the default values are `libnl-3-200`,
    `libnl-route-3-200`, `libnuma1`, and `wget`.  For RHEL-based Linux
    distributions, the default values are `libnl`, `libnl3`,
    `numactl-libs`, and `wget`.

    packages: List of packages to install from Mellanox OFED.  For
    Ubuntu, the default values are `libibverbs1`, `libibverbs-dev`,
    `libibmad`, `libibmad-devel`, `libibumad`, `libibumad-devel`,
    `libmlx4-1`, `libmlx4-dev`, `libmlx5-1`, `libmlx5-dev`,
    `librdmacm1`, `librdmacm-dev`, and `ibverbs-utils`.  For
    RHEL-based Linux distributions, the default values are
    `libibverbs`, `libibverbs-devel`, `libibverbs-utils`, `libibmad`,
    `libibmad-devel`, `libibumad`, `libibumad-devel`, `libmlx4`,
    `libmlx4-devel`, `libmlx5`, `libmlx5-devel`, `librdmacm`, and
    `librdmacm-devel`.

    version: The version of Mellanox OFED to download.  The default
    value is `4.5-1.0.1.0`.

    # Examples

    ```python
    mlnx_ofed(version='4.2-1.0.0.0')
    ```
    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        # Trouble getting MRO with kwargs working correctly, so just call
        # the parent class constructors manually for now.
        #super(mlnx_ofed, self).__init__(**kwargs)
        tar.__init__(self, **kwargs)
        wget.__init__(self, **kwargs)

        self.__baseurl = kwargs.get('baseurl',
                                    'http://content.mellanox.com/ofed')
        self.__oslabel = kwargs.get('oslabel', '')
        self.__ospackages = kwargs.get('ospackages', [])
        self.__packages = kwargs.get('packages', [])
        self.__version = kwargs.get('version', '4.5-1.0.1.0')

        self.__commands = []
        self.__wd = '/var/tmp'

        # Set the Linux distribution specific parameters
        self.__distro()

        # Construct the series of steps to execute
        self.__setup()

    def __str__(self):
        """String representation of the building block"""

        instructions = []
        instructions.append(comment(
            'Mellanox OFED version {}'.format(self.__version)))
        instructions.append(packages(ospackages=self.__ospackages))
        instructions.append(shell(commands=self.__commands))

        return '\n'.join(str(x) for x in instructions)

    def __cleanup_step(self, items=None):
        """Cleanup temporary files"""

        if not items: # pragma: no cover
            logging.warning('items are not defined')
            return ''

        return 'rm -rf {}'.format(' '.join(items))

    def __distro(self):
        """Based on the Linux distribution, set values accordingly.  A user
           specified value overrides any defaults."""

        if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
            if not self.__oslabel:
                if hpccm.config.g_linux_version >= StrictVersion('18.0'):
                    self.__oslabel = 'ubuntu18.04'
                else:
                    self.__oslabel = 'ubuntu16.04'
            if not self.__ospackages:
                self.__ospackages = ['libnl-3-200', 'libnl-route-3-200',
                                     'libnuma1', 'wget']
            if not self.__packages:
                self.__packages = ['libibverbs1', 'libibverbs-dev',
                                   'ibverbs-utils',
                                   'libibmad',  'libibmad-devel',
                                   'libibumad', 'libibumad-devel',
                                   'libmlx4-1', 'libmlx4-dev',
                                   'libmlx5-1', 'libmlx5-dev',
                                   'librdmacm-dev', 'librdmacm1']

            self.__prefix = 'MLNX_OFED_LINUX-{0}-{1}-x86_64'.format(
                self.__version, self.__oslabel)

            self.__installer = 'dpkg --install'

            self.__pkglist = ' '.join('{}_*_amd64.deb'.format(
                os.path.join(self.__wd, self.__prefix, 'DEBS', x))
                                      for x in self.__packages)
        elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
            if not self.__oslabel:
                self.__oslabel = 'rhel7.2'
            if not self.__ospackages:
                self.__ospackages = ['libnl', 'libnl3', 'numactl-libs', 'wget']
            if not self.__packages:
                self.__packages = ['libibverbs', 'libibverbs-devel',
                                   'libibverbs-utils',
                                   'libibmad', 'libibmad-devel',
                                   'libibumad', 'libibumad-devel',
                                   'libmlx4', 'libmlx4-devel',
                                   'libmlx5', 'libmlx5-devel',
                                   'librdmacm-devel', 'librdmacm']

            self.__prefix = 'MLNX_OFED_LINUX-{0}-{1}-x86_64'.format(
                self.__version, self.__oslabel)

            self.__installer = 'rpm --install'

            self.__pkglist = ' '.join('{}-*.x86_64.rpm'.format(
                os.path.join(self.__wd, self.__prefix, 'RPMS', x))
                                      for x in self.__packages)
        else: # pragma: no cover
            raise RuntimeError('Unknown Linux distribution')

    def __setup(self):
        """Construct the series of shell commands, i.e., fill in
           self.__commands"""

        tarball = '{}.tgz'.format(self.__prefix)
        url = '{0}/MLNX_OFED-{1}/{2}'.format(self.__baseurl, self.__version,
                                             tarball)

        # Download and unpackage
        self.__commands.append(self.download_step(url=url,
                                                  directory=self.__wd))
        self.__commands.append(self.untar_step(
            tarball=os.path.join(self.__wd, tarball), directory=self.__wd))

        # Install packages
        self.__commands.append('{0} {1}'.format(self.__installer,
                                                self.__pkglist))

        # Cleanup
        self.__commands.append(self.__cleanup_step(
            items=[os.path.join(self.__wd, tarball),
                   os.path.join(self.__wd, self.__prefix)]))

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
        return str(self)
