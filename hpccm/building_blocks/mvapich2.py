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

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import os
import re
from copy import copy as _copy

import hpccm.config

from hpccm.building_blocks.packages import packages
from hpccm.common import linux_distro
from hpccm.primitives.comment import comment
from hpccm.primitives.copy import copy
from hpccm.primitives.environment import environment
from hpccm.primitives.shell import shell
from hpccm.templates.ConfigureMake import ConfigureMake
from hpccm.templates.rm import rm
from hpccm.templates.sed import sed
from hpccm.templates.tar import tar
from hpccm.templates.wget import wget
from hpccm.toolchain import toolchain

class mvapich2(ConfigureMake, rm, sed, tar, wget):
    """The `mvapich2` building block configures, builds, and installs the
    [MVAPICH2](http://mvapich.cse.ohio-state.edu) component.
    Depending on the parameters, the source will be downloaded from
    the web (default) or copied from a source directory in the local
    build context.

    An InfiniBand building block ([OFED](#ofed) or [Mellanox
    OFED](#mlnx_ofed)) should be installed prior to this building
    block.

    As a side effect, this building block modifies `PATH` and
    `LD_LIBRARY_PATH` to include the MVAPICH2 build.

    As a side effect, a toolchain is created containing the MPI
    compiler wrappers.  The tool can be passed to other operations
    that want to build using the MPI compiler wrappers.

    # Parameters

    check: Boolean flag to specify whether the `make check` step
    should be performed.  The default is False.

    configure_opts: List of options to pass to `configure`.  The
    default values are `--disable-mcast`.

    cuda: Boolean flag to control whether a CUDA aware build is
    performed.  If True, adds `--enable-cuda --with-cuda` to the list
    of `configure` options, otherwise adds `--disable-cuda`.  If the
    toolchain specifies `CUDA_HOME`, then that path is used, otherwise
    `/usr/local/cuda` is used for the path.  The default value is
    True.

    directory: Path to the unpackaged source directory relative to
    the local build context.  The default value is empty.  If this is
    defined, the source in the local build context will be used rather
    than downloading the source from the web.

    gpu_arch: The GPU architecture to use.  Older versions of MVAPICH2
    (2.3b and previous) were hard-coded to use "sm_20".  This option
    has no effect on more recent MVAPICH2 versions.  The default value
    is to use the MVAPICH2 default.

    ospackages: List of OS packages to install prior to configuring
    and building.  For Ubuntu, the default values are `byacc`, `file`,
    `make`, `openssh-client`, and `wget`.  For RHEL-based Linux
    distributions, the default values are `byacc`, `file`, `make`,
    `openssh-clients`, and `wget`.

    prefix: The top level install location.  The default value is
    `/usr/local/mvapich2`.

    toolchain: The toolchain object.  This should be used if
    non-default compilers or other toolchain options are needed.  The
    default is empty.

    version: The version of MVAPICH2 source to download.  This value
    is ignored if `directory` is set.  The default value is `2.3`.

    # Examples

    ```python
    mvapich2(cuda=False, prefix='/opt/mvapich2/2.3a', version='2.3a')
    ```

    ```python
    mvapich2(directory='sources/mvapich2-2.3b')
    ```

    ```python
    p = pgi(eula=True)
    mvapich2(toolchain=p.toolchain)
    ```

    ```python
    mvapich2(configure_opts=['--disable-fortran', '--disable-mcast'])
    ```
    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        # Trouble getting MRO with kwargs working correctly, so just call
        # the parent class constructors manually for now.
        #super(mvapich2, self).__init__(**kwargs)
        ConfigureMake.__init__(self, **kwargs)
        rm.__init__(self, **kwargs)
        sed.__init__(self, **kwargs)
        tar.__init__(self, **kwargs)
        wget.__init__(self, **kwargs)

        self.__baseurl = kwargs.get('baseurl',
                                    'http://mvapich.cse.ohio-state.edu/download/mvapich/mv2')
        self.__check = kwargs.get('check', False)
        self.configure_opts = kwargs.get('configure_opts', ['--disable-mcast'])
        self.cuda = kwargs.get('cuda', True)
        self.directory = kwargs.get('directory', '')
        self.__gpu_arch = kwargs.get('gpu_arch', None)
        self.__ospackages = kwargs.get('ospackages', [])
        self.prefix = kwargs.get('prefix', '/usr/local/mvapich2')
        self.__runtime_ospackages = [] # Filled in by __distro()

        # MVAPICH2 does not accept F90
        self.toolchain_control = {'CC': True, 'CXX': True, 'F77': True,
                                  'F90': False, 'FC': True}
        self.version = kwargs.get('version', '2.3')

        self.__commands = []              # Filled in by __setup()
        self.__environment_variables = {} # Filled in by __setup()

        # Input toolchain, i.e., what to use when building
        self.__toolchain = kwargs.get('toolchain', toolchain())
        self.__wd = '/var/tmp' # working directory

        # Output toolchain
        self.toolchain = toolchain(CC='mpicc', CXX='mpicxx', F77='mpif77',
                                   F90='mpif90', FC='mpifort')

        # Set the Linux distribution specific parameters
        self.__distro()

        # Construct the series of steps to execute
        self.__setup()

    def __str__(self):
        """String representation of the building block"""

        instructions = []
        if self.directory:
            instructions.append(comment('MVAPICH2'))
        else:
            instructions.append(comment(
                'MVAPICH2 version {}'.format(self.version)))
        instructions.append(packages(ospackages=self.__ospackages))
        if self.directory:
            # Use source from local build context
            instructions.append(
                copy(src=self.directory,
                     dest=os.path.join(self.__wd, self.directory)))
        instructions.append(shell(commands=self.__commands))
        instructions.append(environment(
            variables=self.__environment_variables))

        return '\n'.join(str(x) for x in instructions)

    def __distro(self):
        """Based on the Linux distribution, set values accordingly.  A user
        specified value overrides any defaults."""

        if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
            if not self.__ospackages:
                self.__ospackages = ['byacc', 'file', 'make',
                                     'openssh-client', 'wget']
            self.__runtime_ospackages = ['openssh-client']
        elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
            if not self.__ospackages:
                self.__ospackages = ['byacc', 'file', 'make',
                                     'openssh-clients', 'wget']
            self.__runtime_ospackages = ['openssh-clients']
        else: # pragma: no cover
            raise RuntimeError('Unknown Linux distribution')

    def __set_gpu_arch(self, directory=None):
        """Older versions of MVAPICH2 (2.3b and previous) were hard-coded to
        use the "sm_20" GPU architecture.  Use the specified value
        instead."""

        if self.cuda and self.__gpu_arch and directory:
            self.__commands.append(
                self.sed_step(file=os.path.join(directory, 'Makefile.in'),
                              patterns=[r's/-arch sm_20/-arch {}/g'.format(self.__gpu_arch)]))

    def __setup(self):
        """Construct the series of shell commands, i.e., fill in
           self.__commands"""

        # Create a copy of the toolchain so that it can be modified
        # without impacting the original.
        toolchain = _copy(self.__toolchain)

        tarball = 'mvapich2-{}.tar.gz'.format(self.version)
        url = '{0}/{1}'.format(self.__baseurl, tarball)

        # CUDA
        if self.cuda:
            cuda_home = "/usr/local/cuda"
            if toolchain.CUDA_HOME:
                cuda_home = toolchain.CUDA_HOME

            # The PGI compiler needs some special handling for CUDA.
            # http://mvapich.cse.ohio-state.edu/static/media/mvapich/mvapich2-2.0-userguide.html#x1-120004.5
            if toolchain.CC and re.match('.*pgcc', toolchain.CC):
                self.configure_opts.append(
                    '--enable-cuda=basic --with-cuda={}'.format(cuda_home))

                if not toolchain.CFLAGS:
                    toolchain.CFLAGS = '-ta=tesla:nordc'

                if not toolchain.CPPFLAGS:
                    toolchain.CPPFLAGS = '-D__x86_64 -D__align__\(n\)=__attribute__\(\(aligned\(n\)\)\) -D__location__\(a\)=__annotate__\(a\) -DCUDARTAPI='

                if not toolchain.LD_LIBRARY_PATH:
                    toolchain.LD_LIBRARY_PATH = os.path.join(cuda_home,
                                                             'lib64', 'stubs') + ':$LD_LIBRARY_PATH'
            else:
                if not toolchain.LD_LIBRARY_PATH:
                    toolchain.LD_LIBRARY_PATH = os.path.join(cuda_home,
                                                             'lib64', 'stubs') + ':$LD_LIBRARY_PATH'
                self.configure_opts.append(
                    '--enable-cuda --with-cuda={}'.format(cuda_home))

            # Workaround for using compiler wrappers in the build stage
            self.__commands.append('ln -s {0} {1}'.format(
                os.path.join(cuda_home, 'lib64', 'stubs', 'libnvidia-ml.so'),
                os.path.join(cuda_home, 'lib64', 'stubs',
                             'libnvidia-ml.so.1')))
            self.__commands.append('ln -s {0} {1}'.format(
                os.path.join(cuda_home, 'lib64', 'stubs', 'libcuda.so'),
                os.path.join(cuda_home, 'lib64', 'stubs', 'libcuda.so.1')))

        else:
            self.configure_opts.append('--disable-cuda')

        if self.directory:
            # Use source from local build context
            self.__set_gpu_arch(
                directory=os.path.join(self.__wd, self.directory))
            self.__commands.append(self.configure_step(
                directory=os.path.join(self.__wd, self.directory),
                toolchain=toolchain))
        else:
            # Download source from web
            self.__commands.append(self.download_step(url=url,
                                                      directory=self.__wd))
            self.__commands.append(self.untar_step(
                tarball=os.path.join(self.__wd, tarball), directory=self.__wd))
            self.__set_gpu_arch(
                directory=os.path.join(self.__wd,
                                       'mvapich2-{}'.format(self.version)))

            self.__commands.append(self.configure_step(
                directory=os.path.join(self.__wd,
                                       'mvapich2-{}'.format(self.version)),
                toolchain=toolchain))


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

        # Setup environment variables
        self.__environment_variables = {
            'LD_LIBRARY_PATH':
            '{}:$LD_LIBRARY_PATH'.format(os.path.join(self.prefix, 'lib')),
            'PATH': '{}:$PATH'.format(os.path.join(self.prefix, 'bin'))}
        if self.cuda:
            # Workaround for using compiler wrappers in the build stage
            self.__environment_variables['PROFILE_POSTLIB'] = '"-L{} -lnvidia-ml -lcuda"'.format('/usr/local/cuda/lib64/stubs')

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples

        ```python
        m = mvapich2(...)
        Stage0 += m
        Stage1 += m.runtime()
        ```
        """
        instructions = []
        instructions.append(comment('MVAPICH2'))
        # TODO: move the definition of runtime ospackages
        instructions.append(packages(ospackages=self.__runtime_ospackages))
        instructions.append(copy(_from=_from, src=self.prefix,
                                 dest=self.prefix))
        # No need to workaround compiler wrapper issue for the runtime.
        # Copy the dictionary so not to modify the original.
        vars = dict(self.__environment_variables)
        if vars.get('PROFILE_POSTLIB'):
            del vars['PROFILE_POSTLIB']
        instructions.append(environment(variables=vars))
        return '\n'.join(str(x) for x in instructions)
