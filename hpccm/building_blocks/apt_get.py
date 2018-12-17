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

import hpccm.config

from hpccm.common import linux_distro
from hpccm.primitives.shell import shell

class apt_get(object):
    """The `apt_get` building block specifies the set of operating system
    packages to install.  This building block should only be used on
    images that use the Debian package manager (e.g., Ubuntu).

    In most cases, the [`packages` building block](#packages) should be
    used instead of `apt_get`.

    # Parameters

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

        #super(apt_get, self).__init__()

        self.__commands = []
        self.__keys = kwargs.get('keys', [])
        self.ospackages = kwargs.get('ospackages', [])
        self.__ppas = kwargs.get('ppas', [])
        self.__repositories = kwargs.get('repositories', [])

        if hpccm.config.g_linux_distro != linux_distro.UBUNTU: # pragma: no cover
            logging.warning('Using apt-get on a non-Ubuntu Linux distribution')

        # Construct the series of commands that form the building
        # block
        self.__setup()

    def __str__(self):
        """String representation of the building block"""
        return str(shell(chdir=False, commands=self.__commands))

    def __setup(self):
        """Construct the series of commands to execute"""

        if self.__keys:
            for key in self.__keys:
                self.__commands.append(
                    'wget -qO - {} | apt-key add -'.format(key))

        if self.__ppas:
            # Need to install apt-add-repository
            self.__commands.extend(['apt-get update -y',
                                    'DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends software-properties-common'])
            for ppa in self.__ppas:
                self.__commands.append('apt-add-repository {} -y'.format(ppa))

        if self.__repositories:
            for repo in self.__repositories:
                self.__commands.append(
                    'echo "{}" >> /etc/apt/sources.list.d/hpccm.list'.format(repo))

        if self.ospackages:
            self.__commands.append('apt-get update -y')

            install = 'DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \\\n'
            packages = []
            for pkg in self.ospackages:
                packages.append('        {}'.format(pkg))
            install = install + ' \\\n'.join(packages)
            self.__commands.append(install)

            self.__commands.append('rm -rf /var/lib/apt/lists/*')
