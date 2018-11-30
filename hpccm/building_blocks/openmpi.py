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

"""OpenMPI building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import os
import re
from six import string_types

import hpccm.config

from hpccm.building_blocks.packages import packages
from hpccm.common import linux_distro
from hpccm.primitives.comment import comment
from hpccm.primitives.copy import copy
from hpccm.primitives.environment import environment
from hpccm.primitives.shell import shell
from hpccm.templates.ConfigureMake import ConfigureMake
from hpccm.templates.rm import rm
from hpccm.templates.tar import tar
from hpccm.templates.wget import wget
from hpccm.toolchain import toolchain

class openmpi(ConfigureMake, rm, tar, wget):
    """The `openmpi` building block configures, builds, and installs the
    [OpenMPI](https://www.open-mpi.org) component.  Depending on the
    parameters, the source will be downloaded from the web (default)
    or copied from a source directory in the local build context.

    As a side effect, this building block modifies `PATH` and
    `LD_LIBRARY_PATH` to include the OpenMPI build.

    As a side effect, a toolchain is created containing the MPI
    compiler wrappers.  The tool can be passed to other operations
    that want to build using the MPI compiler wrappers.

    # Parameters

    check: Boolean flag to specify whether the `make check` step
    should be performed.  The default is False.

    configure_opts: List of options to pass to `configure`.  The
    default values are `--disable-getpwuid` and
    `--enable-orterun-prefix-by-default`.

    cuda: Boolean flag to control whether a CUDA aware build is
    performed.  If True, adds `--with-cuda` to the list of `configure`
    options, otherwise adds `--without-cuda`.  If the toolchain
    specifies `CUDA_HOME`, then that path is used.  The default value
    is True.

    directory: Path to the unpackaged source directory relative to the
    local build context.  The default value is empty.  If this is
    defined, the source in the local build context will be used rather
    than downloading the source from the web.

    infiniband: Boolean flag to control whether InfiniBand
    capabilities are included.  If True, adds `--with-verbs` to the
    list of `configure` options, otherwise adds `--without-verbs`.
    The default value is True.

    ospackages: List of OS packages to install prior to configuring
    and building.  For Ubuntu, the default values are `bzip2`, `file`,
    `hwloc`, `libnuma-dev`, `make`, `openssh-client`, `perl`, `tar`,
    and `wget`.  For RHEL-based Linux distributions, the default
    values are `bzip2`, `file`, `hwloc`, `make`, `numactl-devl`,
    `openssh-clients`, `perl`, `tar`, and `wget`.

    prefix: The top level install location.  The default value is
    `/usr/local/openmpi`.

    toolchain: The toolchain object.  This should be used if
    non-default compilers or other toolchain options are needed.  The
    default is empty.

    ucx: Flag to control whether UCX is used by the build.  If True,
    adds `--with-ucx` to the list of `configure` options.  If a
    string, uses the value of the string as the UCX path, e.g.,
    `--with-ucx=/path/to/ucx`.  If False, adds `--without-ucx` to the
    list of `configure` options.  The default is False.

    version: The version of OpenMPI source to download.  This
    value is ignored if `directory` is set.  The default value is
    `3.1.2`.

    # Examples

    ```python
    openmpi(cuda=False, infiniband=False, prefix='/opt/openmpi/2.1.2',
        version='2.1.2')
    ```

    ```python
    openmpi(directory='sources/openmpi-3.0.0')
    ```

    ```python
    p = pgi(eula=True)
    openmpi(toolchain=p.toolchain)
    ```

    ```python
    openmpi(configure_opts=['--disable-getpwuid', '--with-slurm'],
            ospackages=['file', 'hwloc', 'libslurm-dev'])
    ```
    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        # Trouble getting MRO with kwargs working correctly, so just call
        # the parent class constructors manually for now.
        #super(openmpi, self).__init__(**kwargs)
        ConfigureMake.__init__(self, **kwargs)
        rm.__init__(self, **kwargs)
        tar.__init__(self, **kwargs)
        wget.__init__(self, **kwargs)

        self.baseurl = kwargs.get('baseurl',
                                  'https://www.open-mpi.org/software/ompi')
        self.__check = kwargs.get('check', False)
        self.configure_opts = kwargs.get('configure_opts',
                                         ['--disable-getpwuid',
                                          '--enable-orterun-prefix-by-default'])
        self.cuda = kwargs.get('cuda', True)
        self.directory = kwargs.get('directory', '')
        self.infiniband = kwargs.get('infiniband', True)
        self.__ospackages = kwargs.get('ospackages', [])
        self.prefix = kwargs.get('prefix', '/usr/local/openmpi')
        self.__runtime_ospackages = [] # Filled in by __distro()

        # Input toolchain, i.e., what to use when building
        self.__toolchain = kwargs.get('toolchain', toolchain())
        self.version = kwargs.get('version', '3.1.2')
        self.__ucx = kwargs.get('ucx', False)

        self.__commands = [] # Filled in by __setup()
        self.__environment_variables = {
            'PATH': '{}:$PATH'.format(os.path.join(self.prefix, 'bin')),
            'LD_LIBRARY_PATH':
            '{}:$LD_LIBRARY_PATH'.format(os.path.join(self.prefix, 'lib'))}
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
            instructions.append(comment('OpenMPI'))
        else:
            instructions.append(comment(
                'OpenMPI version {}'.format(self.version)))
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
                self.__ospackages = ['bzip2', 'file', 'hwloc', 'libnuma-dev',
                                     'make', 'openssh-client', 'perl',
                                     'tar', 'wget']
            self.__runtime_ospackages = ['hwloc', 'openssh-client']
        elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
            if not self.__ospackages:
                self.__ospackages = ['bzip2', 'file', 'hwloc', 'make',
                                     'numactl-devel', 'openssh-clients',
                                     'perl', 'tar', 'wget']
            self.__runtime_ospackages = ['hwloc', 'openssh-clients']
        else: # pragma: no cover
            raise RuntimeError('Unknown Linux distribution')

    def __setup(self):

        """Construct the series of shell commands, i.e., fill in
           self.__commands"""

        build_environment = []

        # The download URL has the format contains vMAJOR.MINOR in the
        # path and the tarball contains MAJOR.MINOR.REVISION, so pull
        # apart the full version to get the MAJOR and MINOR components.
        match = re.match(r'(?P<major>\d+)\.(?P<minor>\d+)', self.version)
        major_minor = 'v{0}.{1}'.format(match.groupdict()['major'],
                                        match.groupdict()['minor'])
        tarball = 'openmpi-{}.tar.bz2'.format(self.version)
        url = '{0}/{1}/downloads/{2}'.format(self.baseurl, major_minor,
                                             tarball)

        # CUDA
        if self.cuda:
            if self.__toolchain.CUDA_HOME:
                self.configure_opts.append(
                    '--with-cuda={}'.format(self.__toolchain.CUDA_HOME))
            else:
                self.configure_opts.append('--with-cuda')
        else:
            self.configure_opts.append('--without-cuda')

        # InfiniBand
        if self.infiniband:
            self.configure_opts.append('--with-verbs')
        else:
            self.configure_opts.append('--without-verbs')

        # UCX
        if self.__ucx:
            if isinstance(self.__ucx, string_types):
                # Use specified path
                self.configure_opts.append('--with-ucx={}'.format(self.__ucx))
            else:
                self.configure_opts.append('--with-ucx')

            # If UCX was built with CUDA support, it is linked with
            # libcuda.so.1, which is not available during the
            # build stage.  Assume that if OpenMPI is built with
            # CUDA support, then UCX was as well...
            if self.cuda:
                cuda_home = "/usr/local/cuda"
                if self.__toolchain.CUDA_HOME:
                    cuda_home = self.__toolchain.CUDA_HOME
                self.__commands.append('ln -s {0} {1}'.format(
                    os.path.join(cuda_home, 'lib64', 'stubs', 'libcuda.so'),
                    os.path.join(cuda_home, 'lib64', 'stubs', 'libcuda.so.1')))
                if not self.__toolchain.LD_LIBRARY_PATH:
                    build_environment.append('LD_LIBRARY_PATH="{}:$LD_LIBRARY_PATH"'.format(os.path.join(cuda_home, 'lib64', 'stubs')))

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
                                       'openmpi-{}'.format(self.version)),
                environment=build_environment,
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
                                    'openmpi-{}'.format(self.version))]))

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples
        ```python
        o = openmpi(...)
        Stage0 += o
        Stage1 += o.runtime()
        ```
        """
        instructions = []
        instructions.append(comment('OpenMPI'))
        instructions.append(packages(ospackages=self.__runtime_ospackages))
        instructions.append(copy(_from=_from, src=self.prefix,
                                 dest=self.prefix))
        instructions.append(environment(
            variables=self.__environment_variables))
        return '\n'.join(str(x) for x in instructions)
