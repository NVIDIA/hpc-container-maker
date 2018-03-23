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

from enum import Enum

from .apt_get import apt_get
from .comment import comment
from .copy import copy
from .environment import environment
from .shell import shell
from .tar import tar
from .toolchain import toolchain
from .wget import wget

class pgi_edition(Enum):
    """Documentation TBD"""
    COMMUNITY = 1
    PROFESSIONAL = 2

class pgi(tar, wget):
    """Documentation TBD"""

    def __init__(self, **kwargs):
        """Documentation TBD"""

        # Trouble getting MRO with kwargs working correctly, so just call
        # the parent class constructors manually for now.
        #super(pgi, self).__init__(**kwargs)
        tar.__init__(self, **kwargs)
        wget.__init__(self, **kwargs)

        self.edition = pgi_edition.COMMUNITY
        # The version is fragile since the latest version is
        # automatically downloaded, which may not match this default.
        # This will need to be updated to 2018 once the community
        # version is updated.
        self.version = kwargs.get('version', '17.10')

        self.__commands = [] # Filled in by __setup()
        basepath = '/opt/pgi/linux86-64/{}'.format(self.version)
        self.__environment_variables = {
            'PATH': '{}:$PATH'.format(os.path.join(basepath, 'bin')),
            'LD_LIBRARY_PATH': '{}:$LD_LIBRARY_PATH'.format(
                os.path.join(basepath, 'lib'))}
        self.__ospackages = kwargs.get('ospackages', ['wget'])
        self.__referer = 'http://www.pgroup.com/products/community.htm'
        self.__url = 'http://www.pgroup.com/support/downloader.php?file=pgi-community-linux-x64'

        self.toolchain = toolchain(
            CC=os.path.join(basepath, 'bin', 'pgcc'),
            CXX=os.path.join(basepath, 'bin', 'pgc++'),
            F77=os.path.join(basepath, 'bin', 'pgfortran'),
            F90=os.path.join(basepath, 'bin', 'pgfortran'),
            FC=os.path.join(basepath, 'bin', 'pgfortran'))

    def cleanup_step(self, items=None):
        """Documentation TBD"""

        if not items:
            logging.warning('items are not defined')
            return ''

        return 'rm -rf {}'.format(' '.join(items))

    def __setup(self):
        """Documentation TBD"""

        # The URL would normally result in a downloaded file with the
        # name 'downloader.php?file=pgi-community-linux-x64'.  Also,
        # the version downloaded cannot be controlled, it will always
        # be the 'latest'.  Use a synthetic tarball filename.
        tarball = 'pgi-community-linux-x64-latest.tar.gz'

        # Use /tmp/pgi as the working directory
        wd = '/tmp/pgi'

        self.__commands.append(self.download_step(
            url=self.__url, outfile=os.path.join(wd, tarball),
            referer=self.__referer, directory=wd))
        self.__commands.append(self.untar_step(
            tarball=os.path.join(wd, tarball), directory=wd))
        self.__commands.append('cd {} && PGI_SILENT=true PGI_ACCEPT_EULA=accept ./install'.format(wd))
        self.__commands.append(self.cleanup_step(
            items=[os.path.join(wd, tarball), wd]))

    def runtime(self, _from='0'):
        """Documentation TBD"""
        basepath = '/opt/pgi/linux86-64/{}'.format(self.version)

        instructions = []
        instructions.append(comment('PGI compiler'))
        instructions.append(apt_get(ospackages=self.__ospackages))
        instructions.append(copy(_from=_from,
                                 src=os.path.join(basepath, 'REDIST', '*.so'),
                                 dest=os.path.join(basepath, 'lib', '')))
        instructions.append(environment(
            variables={'LD_LIBRARY_PATH': '{}:$LD_LIBRARY_PATH'.format(
                os.path.join(basepath, 'lib'))}))
        return instructions

    def toString(self, ctype):
        """Documentation TBD"""

        self.__setup()

        instructions = []
        instructions.append(comment(
            'PGI compiler version {}'.format(self.version)).toString(ctype))
        instructions.append(apt_get(
            ospackages=self.__ospackages).toString(ctype))
        instructions.append(shell(commands=self.__commands).toString(ctype))
        instructions.append(environment(
            variables=self.__environment_variables).toString(ctype))

        return '\n'.join(instructions)
