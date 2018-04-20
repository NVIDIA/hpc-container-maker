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

"""MVAPICH2 building block"""

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

class mvapich2(ConfigureMake, tar, wget):
    """MVAPICH2 building block"""

    def __init__(self, **kwargs):
        """Initialize building block"""

        # Trouble getting MRO with kwargs working correctly, so just call
        # the parent class constructors manually for now.
        #super(mvapich2, self).__init__(**kwargs)
        ConfigureMake.__init__(self, **kwargs)
        tar.__init__(self, **kwargs)
        wget.__init__(self, **kwargs)

        self.baseurl = kwargs.get('baseurl',
                                  'http://mvapich.cse.ohio-state.edu/download/mvapich/mv2')
        self.__check = kwargs.get('check', False)
        self.configure_opts = kwargs.get('configure_opts', ['--disable-mcast'])
        self.cuda = kwargs.get('cuda', True)
        self.directory = kwargs.get('directory', '')
        self.ospackages = kwargs.get('ospackages',
                                     ['byacc', 'file', 'openssh-client',
                                      'wget'])
        self.prefix = kwargs.get('prefix', '/usr/local/mvapich2')

        # MVAPICH2 does not accept F90
        self.toolchain_control = {'CC': True, 'CXX': True, 'F77': True,
                                  'F90': False, 'FC': True}
        self.version = kwargs.get('version', '2.3b')

        self.__commands = [] # Filled in by __setup()
        self.__environment_variables = {
            'PATH': '{}:$PATH'.format(os.path.join(self.prefix, 'bin')),
            'LD_LIBRARY_PATH':
            '{}:$LD_LIBRARY_PATH'.format(os.path.join(self.prefix, 'lib'))}

        # Input toolchain, i.e., what to use when building
        self.__toolchain = kwargs.get('toolchain', toolchain())
        self.__wd = '/tmp' # working directory

        # Output toolchain
        self.toolchain = toolchain(CC='mpicc', CXX='mpicxx', F77='mpif77',
                                   F90='mpif90', FC='mpifort')

    def cleanup_step(self, items=None):
        """Cleanup temporary files"""

        if not items: # pragma: no cover
            logging.warning('items are not defined')
            return ''

        return 'rm -rf {}'.format(' '.join(items))

    def __setup(self):
        """Construct the series of shell commands, i.e., fill in
           self.__commands"""

        tarball = 'mvapich2-{}.tar.gz'.format(self.version)
        url = '{0}/{1}'.format(self.baseurl, tarball)

        # CUDA
        if self.cuda:
            cuda_home = "/usr/local/cuda"
            if self.__toolchain.CUDA_HOME:
                cuda_home = self.__toolchain.CUDA_HOME

            self.configure_opts.append('--with-cuda={}'.format(cuda_home))

            # One half of a workaround for using the MPI compiler
            # wrappers during the build stage.  The driver will not be
            # available, yet libmpi.so depends on libnvidia-ml.so.1.
            # Need to use the stub libraries.  See
            # https://github.com/NVIDIA/nvidia-docker/issues/374.
            self.__commands.append('ln -s {} {}'.format(
                os.path.join(cuda_home, 'lib64', 'stubs', 'nvidia-ml.so'),
                os.path.join(cuda_home, 'lib64', 'stubs', 'nvidia-ml.so.1')))
        else:
            self.configure_opts.append('--without-cuda')

        if self.directory:
            # Use source from local build context
            self.__commands.append(self.configure_step(
                directory=os.path.join(self.__wd, self.directory),
                toolchain=self.__toolchain))
        else:
            # Download source from web
            self.__commands.append(self.download_step(url=url,
                                                      directory=self.__wd))
            self.__commands.append(self.untar_step(
                tarball=os.path.join(self.__wd, tarball), directory=self.__wd))
            self.__commands.append(self.configure_step(
                directory=os.path.join(self.__wd,
                                       'mvapich2-{}'.format(self.version)),
                toolchain=self.__toolchain))

        self.__commands.append(self.build_step())

        if self.__check:
            self.__commands.append(self.check_step())

        self.__commands.append(self.install_step())

        if self.directory:
            # Using source from local build context, cleanup directory
            self.__commands.append(self.cleanup_step(
                items=[os.path.join(self.__wd, self.directory)]))
        else:
            # Using downloaded source, cleanup tarball and directory
            self.__commands.append(self.cleanup_step(
                items=[os.path.join(self.__wd, tarball),
                       os.path.join(self.__wd,
                                    'mvapich2-{}'.format(self.version))]))

    def runtime(self, _from='0'):
        """Install the runtime from a full build in a previous stage"""
        instructions = []
        instructions.append(comment('MVAPICH2'))
        # TODO: move the definition of runtime ospackages
        instructions.append(apt_get(ospackages=['openssh-client']))
        instructions.append(copy(_from=_from, src=self.prefix,
                                 dest=self.prefix))
        instructions.append(environment(
            variables=self.__environment_variables))
        return instructions

    def toString(self, ctype):
        """Building block container specification"""

        self.__setup()

        instructions = []
        if self.directory:
            instructions.append(comment('MVAPICH2').toString(ctype))
        else:
            instructions.append(comment(
                'MVAPICH2 version {}'.format(self.version)).toString(ctype))
        instructions.append(apt_get(
            ospackages=self.ospackages).toString(ctype))
        if self.directory:
            # Use source from local build context
            instructions.append(
                copy(src=self.directory,
                     dest=os.path.join(self.__wd,
                                       self.directory)).toString(ctype))
        instructions.append(shell(commands=self.__commands).toString(ctype))
        instructions.append(environment(
            variables=self.__environment_variables).toString(ctype))

        # Second half of the workaround for the MPI compiler wrappers.
        # Hijack the profiling hooks to inject the CUDA stub
        # directory and stub driver.
        if self.cuda:
            cuda_home = '/usr/local/cuda'
            if self.__toolchain.CUDA_HOME:
                cuda_home = self.__toolchain.CUDA_HOME

            postlib = '"-L{} -lnvidia-ml"'.format(
                os.path.join(cuda_home, 'lib64', 'stubs'))
            instructions.append(
                comment('Hijack the profiling library hooks ' +
                        'to inject the stub driver in the compiler ' +
                        'wrappers').toString(ctype))
            instructions.append(environment(variables={
                'PROFILE_POSTLIB': postlib}).toString(ctype))

        return '\n'.join(instructions)
