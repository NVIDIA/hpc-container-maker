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

import logging # pylint: disable=unused-import

import hpccm.config

from hpccm.common import linux_distro
from hpccm.shell import shell

class yum(object):
    """yum building block"""

    def __init__(self, **kwargs):
        """Initialize building block"""

        #super(yum, self).__init__()

        self.__commands = []
        self.__epel = kwargs.get('epel', False)
        self.ospackages = kwargs.get('ospackages', [])

        if hpccm.config.g_linux_distro != linux_distro.CENTOS: # pragma: no cover
            logging.warning('Using yum on a non-RHEL based Linux distribution')

        # Construct the series of commands that form the building
        # block
        self.__setup()

    def __str__(self):
        """String representation of the building block"""
        return str(shell(commands=self.__commands))

    def __setup(self):
        """Construct the series of commands to execute"""

        if self.__epel:
            # This needs to be a discrete, preliminary step so that
            # packages from EPEL are available to be installed.
            self.__commands.append('yum install -y epel-release')

        if self.ospackages:
            install = 'yum install -y \\\n'
            packages = []
            for pkg in self.ospackages:
                packages.append('        {}'.format(pkg))
            install = install + ' \\\n'.join(packages)
            self.__commands.append(install)

        if self.__epel or self.ospackages:
            self.__commands.append('rm -rf /var/cache/yum/*')
