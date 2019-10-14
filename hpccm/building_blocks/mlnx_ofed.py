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
import posixpath

import hpccm.config
import hpccm.templates.rm
import hpccm.templates.tar
import hpccm.templates.wget

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.packages import packages
from hpccm.common import cpu_arch, linux_distro
from hpccm.primitives.comment import comment
from hpccm.primitives.copy import copy
from hpccm.primitives.shell import shell

class mlnx_ofed(bb_base, hpccm.templates.rm, hpccm.templates.tar,
                hpccm.templates.wget):
    """The `mlnx_ofed` building block downloads and installs the [Mellanox
    OpenFabrics Enterprise Distribution for
    Linux](http://www.mellanox.com/page/products_dyn?product_family=26).

    # Parameters

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
    Ubuntu, the default values are `libibverbs1`, `libibverbs-dev`,
    `libibmad`, `libibmad-devel`, `libibumad`, `libibumad-devel`,
    `libmlx4-1`, `libmlx4-dev`, `libmlx5-1`, `libmlx5-dev`,
    `librdmacm1`, `librdmacm-dev`, and `ibverbs-utils`.  For
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
    value is `4.6-1.0.1.1`.

    # Examples

    ```python
    mlnx_ofed(version='4.2-1.0.0.0')
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(mlnx_ofed, self).__init__(**kwargs)

        self.__arch_download = None # Filled in __cpu_arch()
        self.__arch_pkg = None # Filled in by __cpu_arch()
        self.__baseurl = kwargs.get('baseurl',
                                    'http://content.mellanox.com/ofed')
        self.__label = None  # Filled in by __setup()
        self.__oslabel = kwargs.get('oslabel', '')
        self.__ospackages = kwargs.get('ospackages', [])
        self.__packages = kwargs.get('packages', [])
        self.__prefix = kwargs.get('prefix', None)
        self.__symlink = kwargs.get('symlink', False)
        self.__version = kwargs.get('version', '4.6-1.0.1.1')

        self.__commands = []
        self.__wd = '/var/tmp'

        # Set the CPU architecture specific parameters
        self.__cpu_arch()

        # Set the Linux distribution specific parameters
        self.__distro()

        # Construct the series of steps to execute
        self.__setup()

        # Fill in container instructions
        self.__instructions()

    def __instructions(self):
        """Fill in container instructions"""

        self += comment('Mellanox OFED version {}'.format(self.__version))
        self += packages(ospackages=self.__ospackages)
        self += shell(commands=self.__commands)

    def __cpu_arch(self):
        """Based on the CPU architecture, set values accordingly.  A user
        specified value overrides any defaults."""

        if hpccm.config.g_cpu_arch == cpu_arch.AARCH64:
            self.__arch_download = 'aarch64'
            if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
                self.__arch_pkg = 'arm64'
            else:
                self.__arch_pkg = 'aarch64'
        elif hpccm.config.g_cpu_arch == cpu_arch.PPC64LE:
            self.__arch_download = 'ppc64le'
            if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
                self.__arch_pkg = 'ppc64el'
            else:
                self.__arch_pkg = 'ppc64le'
        elif hpccm.config.g_cpu_arch == cpu_arch.X86_64:
            self.__arch_download = 'x86_64'
            if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
                self.__arch_pkg = 'amd64'
            else:
                self.__arch_pkg = 'x86_64'
        else: # pragma: no cover
            raise RuntimeError('Unknown CPU architecture')

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
                self.__ospackages = ['findutils', 'libnl-3-200',
                                     'libnl-route-3-200', 'libnuma1', 'wget']
            if not self.__packages:
                self.__packages = ['libibverbs1', 'libibverbs-dev',
                                   'ibverbs-utils',
                                   'libibmad',  'libibmad-devel',
                                   'libibumad', 'libibumad-devel',
                                   'libmlx4-1', 'libmlx4-dev',
                                   'libmlx5-1', 'libmlx5-dev',
                                   'librdmacm-dev', 'librdmacm1']

            self.__label = 'MLNX_OFED_LINUX-{0}-{1}-{2}'.format(
                self.__version, self.__oslabel, self.__arch_download)

            self.__installer = 'dpkg --install'
            self.__extractor_template = 'dpkg --extract {0} {1}'

            self.__pkglist = '.*(' + '|'.join(sorted(self.__packages)) + ')_.*_{}.deb'.format(self.__arch_pkg)
        elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
            if not self.__oslabel:
                if hpccm.config.g_cpu_arch == cpu_arch.AARCH64:
                    self.__oslabel = 'rhel7.6alternate'
                else:
                    if hpccm.config.g_linux_version >= StrictVersion('8.0'):
                        self.__oslabel = 'rhel8.0'
                    else:
                        self.__oslabel = 'rhel7.2'
            if not self.__ospackages:
                self.__ospackages = ['findutils', 'libnl3', 'numactl-libs',
                                     'wget']
                if hpccm.config.g_linux_version < StrictVersion('8.0'):
                    self.__ospackages.append('libnl')
            if not self.__packages:
                self.__packages = ['libibverbs', 'libibverbs-devel',
                                   'libibverbs-utils',
                                   'libibmad', 'libibmad-devel',
                                   'libibumad', 'libibumad-devel',
                                   'libmlx4', 'libmlx4-devel',
                                   'libmlx5', 'libmlx5-devel',
                                   'librdmacm-devel', 'librdmacm']

            self.__label = 'MLNX_OFED_LINUX-{0}-{1}-{2}'.format(
                self.__version, self.__oslabel, self.__arch_download)

            self.__installer = 'rpm --install'
            self.__extractor_template = 'sh -c "rpm2cpio {0} | cpio -idm"'

            self.__pkglist = '.*(' + '|'.join(sorted(self.__packages)) + ')-[0-9].*{}.rpm'.format(self.__arch_pkg)
        else: # pragma: no cover
            raise RuntimeError('Unknown Linux distribution')

    def __setup(self):
        """Construct the series of shell commands, i.e., fill in
           self.__commands"""

        tarball = '{}.tgz'.format(self.__label)
        url = '{0}/MLNX_OFED-{1}/{2}'.format(self.__baseurl, self.__version,
                                             tarball)

        # Download and unpackage
        self.__commands.append(self.download_step(url=url,
                                                  directory=self.__wd))
        self.__commands.append(self.untar_step(
            tarball=posixpath.join(self.__wd, tarball), directory=self.__wd))

        # Install packages
        if self.__prefix:
            # Extract to a directory
            # Suppress warnings from libibverbs
            self.__commands.append('mkdir -p /etc/libibverbs.d')
            self.__commands.append('mkdir -p {0} && cd {0}'.format(
                self.__prefix))
            self.__commands.append('find {0} -regextype posix-extended -type f -regex "{1}" -not -path "*UPSTREAM*" -exec {2} \;'.format(
                posixpath.join(self.__wd, self.__label),
                self.__pkglist,
                self.__extractor_template.format('{}', self.__prefix)))

            # library symlinks
            if self.__symlink:
                self.__commands.append('mkdir -p {0} && cd {0}'.format(
                    posixpath.join(self.__prefix, 'lib')))
                # Prune the symlink directory itself and any debug
                # libraries
                self.__commands.append('find .. -path ../lib -prune -o -name "*valgrind*" -prune -o -name "lib*.so*" -exec ln -s {} \;')
                self.__commands.append('cd {0} && ln -s usr/bin bin && ln -s usr/include include'.format(
                    self.__prefix))
        else:
            # Install in the normal system locations

            # MLNX OFED version 4.7 and later split the packages into
            # several subdirectories.  Exclude the upstream packages.
            self.__commands.append('find {0} -regextype posix-extended -type f -regex "{1}" -not -path "*UPSTREAM*" -exec {2} {{}} +'.format(
                posixpath.join(self.__wd, self.__label),
                self.__pkglist, self.__installer))

        # Cleanup
        self.__commands.append(self.cleanup_step(
            items=[posixpath.join(self.__wd, tarball),
                   posixpath.join(self.__wd, self.__label)]))

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

            if self.__ospackages:
                instructions.append(packages(ospackages=self.__ospackages))

            # Suppress warnings from libibverbs
            instructions.append(shell(commands=['mkdir -p /etc/libibverbs.d']))

            instructions.append(copy(_from=_from, dest=self.__prefix,
                                     src=self.__prefix))
            return '\n'.join(str(x) for x in instructions)
        else:
            return str(self)
