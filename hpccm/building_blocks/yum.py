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

"""yum building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from distutils.version import StrictVersion
import logging # pylint: disable=unused-import
import posixpath

import hpccm.config

from hpccm.building_blocks.base import bb_base
from hpccm.common import cpu_arch, linux_distro
from hpccm.primitives.shell import shell

class yum(bb_base):
    """The `yum` building block specifies the set of operating system
    packages to install.  This building block should only be used on
    images that use the Red Hat package manager (e.g., CentOS).

    In most cases, the [`packages` building block](#packages) should
    be used instead of `yum`.

    # Parameters

    download: Boolean flag to specify whether to download the rpm
    packages instead of installing them.  The default is False.

    download_directory: The deb package download location. This
    parameter is ignored if `download` is False. The default value is
    `/var/tmp/yum_download`.

    epel: - Boolean flag to specify whether to enable the Extra
    Packages for Enterprise Linux (EPEL) repository.  The default is
    False.

    extract: Location where the downloaded packages should be
    extracted. Note, this extracts and does not install the packages,
    i.e., the package manager is bypassed. After the downloaded
    packages are extracted they are deleted. This parameter is ignored
    if `download` is False. If empty, then the downloaded packages are
    not extracted. The default value is an empty string.

    keys: A list of GPG keys to import.  The default is an empty list.

    ospackages: A list of packages to install.  The default is an
    empty list.

    powertools: Boolean flag to specify whether to enable the
    PowerTools repository.  The default is False.  This parameter is
    only recognized if the distribution version is 8.x.

    release_stream: Boolean flag to specify whether to enable the [CentOS release stream](https://wiki.centos.org/Manuals/ReleaseNotes/CentOSStream)
    repository.  The default is False.  This parameter is only
    recognized if the distribution version is 8.x.

    repositories: A list of yum repositories to add.  The default is
    an empty list.

    scl: - Boolean flag to specify whether to enable the Software
    Collections (SCL) repository.  The default is False.  This
    parameter is only recognized if the distribution version is 7.x.

    yum4: Boolean flag to specify whether `yum4` should be used
    instead of `yum`.  The default is False.  This parameter is only
    recognized if the distribution version is 7.x.

    # Examples

    ```python
    yum(ospackages=['make', 'wget'])
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(yum, self).__init__()

        self.__commands = []
        self.__download = kwargs.get('download', False)
        self.__download_args = kwargs.get('download_args', '')
        self.__download_directory = kwargs.get('download_directory',
                                               '/var/tmp/yum_download')
        self.__epel = kwargs.get('epel', False)
        self.__extra_opts = kwargs.get('extra_opts', [])
        self.__extract = kwargs.get('extract', None)
        self.__keys = kwargs.get('keys', [])
        self.__opts = ['-y']
        self.ospackages = kwargs.get('ospackages', [])
        self.__powertools = kwargs.get('powertools', False)
        self.__release_stream = kwargs.get('release_stream', False)
        self.__repositories = kwargs.get('repositories', [])
        self.__scl = kwargs.get('scl', False)
        self.__yum4 = kwargs.get('yum4', False)

        if hpccm.config.g_linux_distro != linux_distro.CENTOS: # pragma: no cover
            logging.warning('Using yum on a non-RHEL based Linux distribution')

        # Set the CPU architecture specific parameters
        self.__cpu_arch()

        # Construct the series of commands that form the building
        # block
        self.__setup()

        # Fill in container instructions
        self.__instructions()

    def __instructions(self):
        """Fill in container instructions"""
        self += shell(chdir=False, commands=self.__commands)

    def __cpu_arch(self):
        """Based on the CPU architecture, set values accordingly.  A user
        specified value overrides any defaults."""

        if hpccm.config.g_cpu_arch == cpu_arch.X86_64:
            if not self.__download_args:
                self.__download_args = '-x \*i?86 --archlist=x86_64'

    def __setup(self):
        """Construct the series of commands to execute"""

        if self.__extra_opts:
            self.__download_args += ' ' + ' '.join(self.__extra_opts)
            self.__opts.extend(self.__extra_opts)

        # Use yum version 4 is requested.  yum 4 is the default on
        # CentOS 8.
        yum = 'yum'
        if self.__yum4 and hpccm.config.g_linux_version < StrictVersion('8.0'):
            self.__commands.append('yum install -y nextgen-yum4')
            yum = 'yum4'

        if self.__keys:
            self.__commands.append('rpm --import {}'.format(
                ' '.join(self.__keys)))

        if self.__repositories:
            # Need yum-config-manager
            if hpccm.config.g_linux_version >= StrictVersion('8.0'):
                # CentOS 8
                self.__commands.append('yum install -y dnf-utils')
            else:
                # CentOS 7
                self.__commands.append('yum install -y yum-utils')

            for repo in self.__repositories:
                self.__commands.append(
                    'yum-config-manager --add-repo {}'.format(repo))

        if self.__epel:
            # This needs to be a discrete, preliminary step so that
            # packages from EPEL are available to be installed.
            self.__commands.append('yum install -y epel-release')

        if (self.__powertools and
            hpccm.config.g_linux_version >= StrictVersion('8.0')):
            # This needs to be a discrete, preliminary step so that
            # packages from PowerTools are available to be installed.
            if not self.__repositories:
                # dnf-utils will be installed above if repositories are
                # enabled
                self.__commands.append('yum install -y dnf-utils')
            self.__commands.append('yum-config-manager --set-enabled PowerTools')

        if (self.__release_stream and
            hpccm.config.g_linux_version >= StrictVersion('8.0')):
            # This needs to be a discrete, preliminary step so that
            # packages from release stream are available to be installed.
            self.__commands.append('yum install -y centos-release-stream')

        if (self.__scl and
            hpccm.config.g_linux_version < StrictVersion('8.0')):
            # This needs to be a discrete, preliminary step so that
            # packages from SCL are available to be installed.
            self.__commands.append('yum install -y centos-release-scl')

        if self.ospackages:
            packages = []
            for pkg in sorted(self.ospackages):
                packages.append('        {}'.format(pkg))

            if self.__download:
                # Download packages

                # Need yumdownloader
                self.__commands.append('yum install -y yum-utils')

                self.__commands.append('mkdir -p {0}'.format(
                    self.__download_directory))

                download = 'yumdownloader --destdir={0} {1} \\\n'.format(
                    self.__download_directory, self.__download_args)
                download = download + ' \\\n'.join(packages)
                self.__commands.append(download)

                if self.__extract:
                    # Extract the packages to a prefix - not a "real"
                    # package manager install
                    self.__commands.append('mkdir -p {0} && cd {0}'.format(
                        self.__extract))

                    regex = posixpath.join(
                        self.__download_directory,
                        '(' + '|'.join(sorted(self.ospackages)) + ').*rpm')
                    self.__commands.append('find {0} -regextype posix-extended -type f -regex "{1}" -exec sh -c "rpm2cpio {{}} | cpio -idm" \;'.format(self.__download_directory, regex))

                    # Cleanup downloaded packages
                    self.__commands.append(
                        'rm -rf {}'.format(self.__download_directory))
            else:
                # Install packages
                install = '{0} install {1} \\\n'.format(yum,
                                                        ' '.join(self.__opts))
                install = install + ' \\\n'.join(packages)
                self.__commands.append(install)

        if self.__epel or self.ospackages:
            self.__commands.append('rm -rf /var/cache/yum/*')
