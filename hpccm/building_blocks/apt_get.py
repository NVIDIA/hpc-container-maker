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

"""apt-get building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import os
import posixpath

import hpccm.config
import hpccm.templates.sed
import hpccm.templates.wget

from hpccm.building_blocks.base import bb_base
from hpccm.common import linux_distro
from hpccm.primitives.shell import shell

class apt_get(bb_base, hpccm.templates.sed, hpccm.templates.wget):
    """The `apt_get` building block specifies the set of operating system
    packages to install.  This building block should only be used on
    images that use the Debian package manager (e.g., Ubuntu).

    In most cases, the [`packages` building block](#packages) should be
    used instead of `apt_get`.

    # Parameters

    aptitude: Boolean flag to specify whether `aptitude` should be
    used instead of `apt-get`.  The default is False.

    download: Boolean flag to specify whether to download the deb
    packages instead of installing them.  The default is False.

    download_directory: The deb package download location. This
    parameter is ignored if `download` is False. The default value is
    `/var/tmp/apt_get_download`.

    extract: Location where the downloaded packages should be
    extracted. Note, this extracts and does not install the packages,
    i.e., the package manager is bypassed. After the downloaded
    packages are extracted they are deleted. This parameter is ignored
    if `download` is False. If empty, then the downloaded packages are
    not extracted. The default value is an empty string.

    keys: A list of GPG keys to add.  The default is an empty list.

    ospackages: A list of packages to install.  The default is an
    empty list.

    ppas: A list of personal package archives to add.  The default is
    an empty list.

    repositories: A list of apt repositories to add.  The default is
    an empty list.

    # Examples

    ```python
    apt_get(ospackages=['make', 'wget'])
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(apt_get, self).__init__()

        self.__aptitude = kwargs.get('aptitude', False)
        self.__commands = []
        self.__download = kwargs.get('download', False)
        self.__download_directory = kwargs.get('download_directory',
                                               '/var/tmp/apt_get_download')
        self.__extra_opts = kwargs.get('extra_opts', [])
        self.__extract = kwargs.get('extract', None)
        self.__keys = kwargs.get('keys', [])
        self.__opts = ['-y', '--no-install-recommends']
        self.ospackages = kwargs.get('ospackages', [])
        self.__ppas = kwargs.get('ppas', [])
        self.__repositories = kwargs.get('repositories', [])

        if hpccm.config.g_linux_distro != linux_distro.UBUNTU: # pragma: no cover
            logging.warning('Using apt-get on a non-Ubuntu Linux distribution')

        # Construct the series of commands that form the building
        # block
        self.__setup()

        # Fill in container instructions
        self.__instructions()

    def __instructions(self):
        """Fill in container instructions"""
        self += shell(chdir=False, commands=self.__commands)

    def __setup(self):
        """Construct the series of commands to execute"""

        if self.__extra_opts:
            self.__opts.extend(self.__extra_opts)

        apt_get_download = 'DEBIAN_FRONTEND=noninteractive apt-get download {}'.format(' '.join(self.__opts))
        apt_get_install = 'DEBIAN_FRONTEND=noninteractive apt-get install {}'.format(' '.join(self.__opts))

        if self.__keys:
            for key in self.__keys:
                self.__commands.append(
                    'wget -qO - {} | apt-key add -'.format(key))

        if self.__ppas:
            # Need to install apt-add-repository
            self.__commands.extend(['apt-get update -y',
                                    apt_get_install + ' software-properties-common'])
            for ppa in self.__ppas:
                self.__commands.append('apt-add-repository {} -y'.format(ppa))

        if self.__repositories:
            for repo in self.__repositories:
                if repo.startswith('http'):
                    # Repository is a URL to a repository configuration file
                    self.__commands.append(
                        self.download_step(directory='/etc/apt/sources.list.d',
                                           url=repo))
                else:
                    # Repository is a configuration string
                    self.__commands.append(
                        'echo "{}" >> /etc/apt/sources.list.d/hpccm.list'.format(repo))

        if self.ospackages:
            packages = []
            for pkg in sorted(self.ospackages):
                packages.append('        {}'.format(pkg))

            self.__commands.append('apt-get update -y')

            if self.__download:
                # Download packages
                # Assign mode 777 to work around warnings
                # Ubuntu 16: Can't drop privileges for downloading as file
                # Ubuntu 18: Download is performed unsandboxed as root as file
                self.__commands.append('mkdir -m 777 -p {0} && cd {0}'.format(
                    self.__download_directory))
                self.__commands.append(apt_get_download + ' \\\n' + ' \\\n'.join(packages))

                if self.__extract:
                    # Extract the packages to a prefix - not a "real"
                    # package manager install
                    self.__commands.append('mkdir -p {0}'.format(
                        self.__extract))

                    regex = posixpath.join(
                        self.__download_directory,
                        '(' + '|'.join(sorted(self.ospackages)) + ').*deb')
                    self.__commands.append('find {0} -regextype posix-extended -type f -regex "{1}" -exec dpkg --extract {{}} {2} \;'.format(self.__download_directory, regex, self.__extract))

                    # Cleanup downloaded packages
                    self.__commands.append(
                        'rm -rf {}'.format(self.__download_directory))

                # Cleanup repository file(s)
                for repo in self.__repositories:
                    if repo.startswith('http'):
                        # Repository is a URL to a repository
                        # configuration file
                        self.__commands.append(
                            'rm -f {}'.format(
                                posixpath.join('/etc/apt/sources.list.d',
                                               os.path.basename(repo))))
                    else:
                        # Repository is a configuration string
                        # Use '|' as separator to try to avoid conflicts or
                        # the need to escape the repo string.
                        self.__commands.append(
                            self.sed_step(
                                file='/etc/apt/sources.list.d/hpccm.list',
                                patterns=[r'\|^{}$|d'.format(repo)]))

            else:
                if self.__aptitude:
                    self.__commands.append(apt_get_install + ' aptitude')
                    install = 'aptitude install -y --without-recommends -o Aptitude::ProblemResolver::SolutionCost=\'100*canceled-actions,200*removals\' \\\n'
                    install = install + ' \\\n'.join(packages)
                    self.__commands.append(install)
                else:
                    self.__commands.append(apt_get_install + ' \\\n' + ' \\\n'.join(packages))

            self.__commands.append('rm -rf /var/lib/apt/lists/*')
