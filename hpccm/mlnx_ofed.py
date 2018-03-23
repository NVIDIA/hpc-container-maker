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

"""Documentation TBD"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import os

from .apt_get import apt_get
from .comment import comment
from .shell import shell
from .tar import tar
from .wget import wget

class mlnx_ofed(tar, wget):
    """Documentation TBD"""

    def __init__(self, **kwargs):
        """Documentation TBD"""

        # Trouble getting MRO with kwargs working correctly, so just call
        # the parent class constructors manually for now.
        #super(mlnx_ofed, self).__init__(**kwargs)
        tar.__init__(self, **kwargs)
        wget.__init__(self, **kwargs)

        self.__baseurl = kwargs.get('baseurl',
                                    'http://content.mellanox.com/ofed')
        self.__ospackages = kwargs.get('ospackages',
                                       ['libnl-3-200', 'libnl-route-3-200',
                                        'libnuma1', 'wget'])
        self.__packages = kwargs.get('packages',
                                     ['libibverbs1', 'libibverbs-dev',
                                      'libmlx5-1', 'ibverbs-utils'])
        self.__version = kwargs.get('version', '3.4-1.0.0.0')

        self.__commands = []
        self.__wd = '/tmp'

    def __cleanup_step(self, items=None):
        """Documentation TBD"""

        if not items:
            logging.warning('items are not defined')
            return ''

        return 'rm -rf {}'.format(' '.join(items))

    def __setup(self):
        """Documentation TBD"""

        # Check to see if the setup has already been performed
        if self.__commands:
            return

        # This is Ubuntu 16.04 specific.  This should be generic.
        prefix = 'MLNX_OFED_LINUX-{}-ubuntu16.04-x86_64'.format(self.__version)
        tarball = '{}.tgz'.format(prefix)
        url = '{0}/MLNX_OFED-{1}/{2}'.format(self.__baseurl, self.__version,
                                             tarball)

        # Download and unpackage
        self.__commands.append(self.download_step(url=url,
                                                  directory=self.__wd))
        self.__commands.append(self.untar_step(
            tarball=os.path.join(self.__wd, tarball), directory=self.__wd))

        # Install packages, order could matter
        for p in self.__packages:
            self.__commands.append('dpkg --install {}'.format(
                os.path.join(self.__wd, prefix, 'DEBS',
                             '{}_*_amd64.deb'.format(p))))

        # Cleanup
        self.__commands.append(self.__cleanup_step(
            items=[os.path.join(self.__wd, tarball),
                   os.path.join(self.__wd, prefix)]))

    def runtime(self, _from='0'):
        """Documentation TBD"""
        return self

    def toString(self, ctype):
        """Documentation TBD"""

        self.__setup()

        instructions = []
        instructions.append(comment(
            'Mellanox OFED version {}'.format(self.__version)).toString(ctype))
        instructions.append(apt_get(
            ospackages=self.__ospackages).toString(ctype))
        instructions.append(shell(commands=self.__commands).toString(ctype))

        return '\n'.join(instructions)
