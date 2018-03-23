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
# pylint: disable=too-many-instance-attributes

"""Documentation TBD"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import os

from .apt_get import apt_get
from .comment import comment
from .ConfigureMake import ConfigureMake
from .copy import copy
from .environment import environment
from .shell import shell
from .tar import tar
from .toolchain import toolchain
from .wget import wget

class fftw(ConfigureMake, tar, wget):
    """Documentation TBD"""

    def __init__(self, **kwargs):
        """Documentation TBD"""

        # Trouble getting MRO with kwargs working correctly, so just call
        # the parent class constructors manually for now.
        #super(fftw, self).__init__(**kwargs)
        ConfigureMake.__init__(self, **kwargs)
        tar.__init__(self, **kwargs)
        wget.__init__(self, **kwargs)

        self.configure_opts = kwargs.get('configure_opts',
                                         ['--enable-shared', '--enable-openmp',
                                          '--enable-threads', '--enable-sse2'])
        self.prefix = kwargs.get('prefix', '/usr/local/fftw')

        self.__baseurl = kwargs.get('baseurl', 'ftp://ftp.fftw.org/pub/fftw')
        self.__check = kwargs.get('check', False)
        self.__directory = kwargs.get('directory', '')
        self.__ospackages = kwargs.get('ospackages', ['file', 'make', 'wget'])
        self.__toolchain = kwargs.get('toolchain', toolchain())
        self.__version = kwargs.get('version', '3.3.7')

        self.__commands = [] # Filled in by __setup()
        self.__environment_variables = {
            'LD_LIBRARY_PATH':
            '{}:$LD_LIBRARY_PATH'.format(os.path.join(self.prefix, 'lib'))}
        self.__wd = '/tmp' # working directory

    def cleanup_step(self, items=None):
        """Documentation TBD"""

        if not items:
            logging.warning('items are not defined')
            return ''

        return 'rm -rf {}'.format(' '.join(items))

    def __setup(self):
        """Documentation TBD"""

        tarball = 'fftw-{}.tar.gz'.format(self.__version)
        url = '{0}/{1}'.format(self.__baseurl, tarball)

        if self.__directory:
            # Use source from local build context
            self.__commands.append(self.configure_step(
                directory=os.path.join(self.__wd, self.__directory),
                toolchain=self.__toolchain))
        else:
            # Download source from web
            self.__commands.append(self.download_step(url=url,
                                                      directory=self.__wd))
            self.__commands.append(self.untar_step(
                tarball=os.path.join(self.__wd, tarball), directory=self.__wd))
            self.__commands.append(self.configure_step(
                directory=os.path.join(self.__wd,
                                       'fftw-{}'.format(self.__version)),
                toolchain=self.__toolchain))

        self.__commands.append(self.build_step())

        # Check the build
        if self.__check:
            # PGI compiler needs a larger stack size 
            self.__commands.append('ulimit -s unlimited')
            self.__commands.append(self.check_step())

        self.__commands.append(self.install_step())

        if self.__directory:
            # Using source from local build context, cleanup directory
            self.__commands.append(self.cleanup_step(
                items=[os.path.join(self.__wd, self.__directory)]))
        else:
            # Using downloaded source, cleanup tarball and directory
            self.__commands.append(self.cleanup_step(
                items=[os.path.join(self.__wd, tarball),
                       os.path.join(self.__wd,
                                    'fftw-{}'.format(self.__version))]))

    def runtime(self, _from='0'):
        """Documentation TBD"""
        instructions = []
        instructions.append(comment('FFTW'))
        instructions.append(copy(_from=_from, src=self.prefix,
                                 dest=self.prefix))
        instructions.append(environment(
            variables=self.__environment_variables))
        return instructions

    def toString(self, ctype):
        """Documentation TBD"""

        self.__setup()

        instructions = []
        if self.__directory:
            instructions.append(comment('FFTW').toString(ctype))
        else:
            instructions.append(comment(
                'FFTW version {}'.format(self.__version)).toString(ctype))
        instructions.append(apt_get(
            ospackages=self.__ospackages).toString(ctype))
        if self.__directory:
            # Use source from local build context
            instructions.append(
                copy(src=self.__directory,
                     dest=os.path.join(self.__wd,
                                       self.__directory)).toString(ctype))
        instructions.append(shell(commands=self.__commands).toString(ctype))
        instructions.append(environment(
            variables=self.__environment_variables).toString(ctype))

        return '\n'.join(instructions)
