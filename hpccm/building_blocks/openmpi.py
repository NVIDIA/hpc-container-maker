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

import posixpath
import re
from six import string_types

import hpccm.config
import hpccm.templates.ConfigureMake
import hpccm.templates.downloader
import hpccm.templates.envvars
import hpccm.templates.ldconfig
import hpccm.templates.rm

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.packages import packages
from hpccm.common import linux_distro
from hpccm.primitives.comment import comment
from hpccm.primitives.copy import copy
from hpccm.primitives.environment import environment
from hpccm.primitives.shell import shell
from hpccm.toolchain import toolchain

class openmpi(bb_base, hpccm.templates.ConfigureMake, hpccm.templates.envvars,
              hpccm.templates.downloader, hpccm.templates.ldconfig,
              hpccm.templates.rm):
    """The `openmpi` building block configures, builds, and installs the
    [OpenMPI](https://www.open-mpi.org) component.

    As a side effect, a toolchain is created containing the MPI
    compiler wrappers.  The tool can be passed to other operations
    that want to build using the MPI compiler wrappers.

    # Parameters

    branch: The git branch to clone.  Only recognized if the
    `repository` parameter is specified.  The default is empty, i.e.,
    use the default branch for the repository.

    check: Boolean flag to specify whether the `make check` step
    should be performed.  The default is False.

    commit: The git commit to clone.  Only recognized if the
    `repository` parameter is specified.  The default is empty, i.e.,
    use the latest commit on the default branch for the repository.

    configure_opts: List of options to pass to `configure`.  The
    default values are `--disable-getpwuid` and
    `--enable-orterun-prefix-by-default`.

    cuda: Boolean flag to control whether a CUDA aware build is
    performed.  If True, adds `--with-cuda` to the list of `configure`
    options, otherwise adds `--without-cuda`.  If the toolchain
    specifies `CUDA_HOME`, then that path is used.  The default value
    is True.

    disable_FEATURE: Flags to control disabling features when
    configuring.  For instance, `disable_foo=True` maps to
    `--disable-foo`.  Underscores in the parameter name are converted
    to dashes.

    enable_FEATURE[=ARG]: Flags to control enabling features when
    configuring.  For instance, `enable_foo=True` maps to
    `--enable-foo` and `enable_foo='yes'` maps to `--enable-foo=yes`.
    Underscores in the parameter name are converted to dashes.

    environment: Boolean flag to specify whether the environment
    (`LD_LIBRARY_PATH` and `PATH`) should be modified to include
    OpenMPI. The default is True.

    infiniband: Boolean flag to control whether InfiniBand
    capabilities are included.  If True, adds `--with-verbs` to the
    list of `configure` options, otherwise adds `--without-verbs`.
    The default value is True.

    ldconfig: Boolean flag to specify whether the OpenMPI library
    directory should be added dynamic linker cache.  If False, then
    `LD_LIBRARY_PATH` is modified to include the OpenMPI library
    directory. The default value is False.

    ospackages: List of OS packages to install prior to configuring
    and building.  For Ubuntu, the default values are `bzip2`, `file`,
    `hwloc`, `libnuma-dev`, `make`, `openssh-client`, `perl`, `tar`,
    and `wget`.  For RHEL-based Linux distributions, the default
    values are `bzip2`, `file`, `hwloc`, `make`, `numactl-devl`,
    `openssh-clients`, `perl`, `tar`, and `wget`.  If the `repository`
    parameter is set, then `autoconf`, `automake`, `ca-certificates`,
    `git`, and `libtool` are also included.

    pmi: Flag to control whether PMI is used by the build.  If True,
    adds `--with-pmi` to the list of `configure` options.  If a
    string, uses the value of the string as the PMI path, e.g.,
    `--with-pmi=/usr/local/slurm-pmi2`.  If False, does nothing.  The
    default is False.

    pmix: Flag to control whether PMIX is used by the build.  If True,
    adds `--with-pmix` to the list of `configure` options.  If a
    string, uses the value of the string as the PMIX path, e.g.,
    `--with-pmix=/usr/local/pmix`.  If False, does nothing.  The
    default is False.

    prefix: The top level install location.  The default value is
    `/usr/local/openmpi`.

    repository: The location of the git repository that should be used to build OpenMPI.  If True, then use the default `https://github.com/open-mpi/ompi.git`
    repository.  The default is empty, i.e., use the release package
    specified by `version`.

    toolchain: The toolchain object.  This should be used if
    non-default compilers or other toolchain options are needed.  The
    default is empty.

    ucx: Flag to control whether UCX is used by the build.  If True,
    adds `--with-ucx` to the list of `configure` options.  If a
    string, uses the value of the string as the UCX path, e.g.,
    `--with-ucx=/path/to/ucx`.  If False, adds `--without-ucx` to the
    list of `configure` options.  The default is False.

    url: The loation of the tarball that should be used to build
    OpenMPI.  The default is empty, i.e., use the release package
    specified by `version`.

    version: The version of OpenMPI source to download.  This
    value is ignored if `directory` is set.  The default value is
    `4.0.3rc3`.

    with_PACKAGE[=ARG]: Flags to control optional packages when
    configuring.  For instance, `with_foo=True` maps to `--with-foo`
    and `with_foo='/usr/local/foo'` maps to
    `--with-foo=/usr/local/foo`.  Underscores in the parameter name
    are converted to dashes.

    without_PACKAGE: Flags to control optional packages when
    configuring.  For instance `without_foo=True` maps to
    `--without-foo`.  Underscores in the parameter name are converted
    to dashes.

    # Examples

    ```python
    openmpi(cuda=False, infiniband=False, prefix='/opt/openmpi/2.1.2',
        version='2.1.2')
    ```

    ```python
    openmpi(repository='https://github.com/open-mpi/ompi.git')
    ```

    ```python
    p = pgi(eula=True)
    openmpi(toolchain=p.toolchain)
    ```

    ```python
    openmpi(configure_opts=['--disable-getpwuid', '--with-slurm'],
            ospackages=['file', 'hwloc', 'libslurm-dev'])
    ```

    ```python
    openmpi(pmi='/usr/local/slurm-pmi2', pmix='internal')
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(openmpi, self).__init__(**kwargs)

        self.__baseurl = kwargs.get('baseurl',
                                  'https://www.open-mpi.org/software/ompi')
        self.__check = kwargs.get('check', False)
        self.configure_opts = kwargs.get('configure_opts',
                                         ['--disable-getpwuid',
                                          '--enable-orterun-prefix-by-default'])
        self.cuda = kwargs.get('cuda', True)
        self.__default_repository = 'https://github.com/open-mpi/ompi.git'
        self.infiniband = kwargs.get('infiniband', True)
        self.__ospackages = kwargs.get('ospackages', [])
        self.__pmi = kwargs.get('pmi', False)
        self.__pmix = kwargs.get('pmix', False)
        self.prefix = kwargs.get('prefix', '/usr/local/openmpi')
        self.__runtime_ospackages = [] # Filled in by __distro()

        # Input toolchain, i.e., what to use when building
        self.__toolchain = kwargs.get('toolchain', toolchain())
        self.__version = kwargs.get('version', '4.0.3rc3')
        self.__ucx = kwargs.get('ucx', False)

        self.__commands = [] # Filled in by __setup()
        self.__wd = '/var/tmp' # working directory

        # Output toolchain
        self.toolchain = toolchain(CC='mpicc', CXX='mpicxx', F77='mpif77',
                                   F90='mpif90', FC='mpifort')

        # Set the Linux distribution specific parameters
        self.__distro()

        # Construct the series of steps to execute
        self.__setup()

        # Fill in container instructions
        self.__instructions()

    def __instructions(self):
        """Fill in container instructions"""

        if self.repository:
            if self.branch:
                self += comment('OpenMPI {} {}'.format(self.repository,
                                                       self.branch))
            elif self.commit:
                self += comment('OpenMPI {} {}'.format(self.repository,
                                                       self.commit))
            else:
                self += comment('OpenMPI {}'.format(self.repository))
        else:
            self += comment('OpenMPI version {}'.format(self.__version))
        self += packages(ospackages=self.__ospackages)
        self += shell(commands=self.__commands)
        self += environment(variables=self.environment_step())

    def __distro(self):
        """Based on the Linux distribution, set values accordingly.  A user
        specified value overrides any defaults."""

        if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
            if not self.__ospackages:
                self.__ospackages = ['bzip2', 'file', 'hwloc', 'libnuma-dev',
                                     'make', 'openssh-client', 'perl',
                                     'tar', 'wget']

                if self.repository:
                    self.__ospackages.extend(['autoconf', 'automake',
                                              'ca-certificates', 'git',
                                              'libtool'])
            self.__runtime_ospackages = ['hwloc', 'openssh-client']
        elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
            if not self.__ospackages:
                self.__ospackages = ['bzip2', 'file', 'hwloc', 'make',
                                     'numactl-devel', 'openssh-clients',
                                     'perl', 'tar', 'wget']

                if self.repository:
                    self.__ospackages.extend(['autoconf', 'automake',
                                              'ca-certificates', 'git',
                                              'libtool'])
            self.__runtime_ospackages = ['hwloc', 'openssh-clients']
        else: # pragma: no cover
            raise RuntimeError('Unknown Linux distribution')

    def __setup(self):

        """Construct the series of shell commands, i.e., fill in
           self.__commands"""

        build_environment = []
        remove = []

        # Use the default repository if set to True
        if self.repository is True:
            self.repository = self.__default_repository

        if not self.repository and not self.url:
            # The download URL has the format contains vMAJOR.MINOR in the
            # path and the tarball contains MAJOR.MINOR.REVISION, so pull
            # apart the full version to get the MAJOR and MINOR components.
            match = re.match(r'(?P<major>\d+)\.(?P<minor>\d+)', self.__version)
            major_minor = 'v{0}.{1}'.format(match.groupdict()['major'],
                                            match.groupdict()['minor'])
            tarball = 'openmpi-{}.tar.bz2'.format(self.__version)
            self.url = '{0}/{1}/downloads/{2}'.format(
                self.__baseurl, major_minor, tarball)
            remove.append(posixpath.join(self.__wd, tarball))

        # CUDA
        if self.cuda:
            if self.__toolchain.CUDA_HOME:
                self.configure_opts.append(
                    '--with-cuda={}'.format(self.__toolchain.CUDA_HOME))
            else:
                self.configure_opts.append('--with-cuda')
        else:
            self.configure_opts.append('--without-cuda')

        # PMI
        if self.__pmi:
            if isinstance(self.__pmi, string_types):
                # Use specified path
                self.configure_opts.append('--with-pmi={}'.format(self.__pmi))
            else:
                self.configure_opts.append('--with-pmi')

        # PMIX
        if self.__pmix:
            if isinstance(self.__pmix, string_types):
                # Use specified path
                self.configure_opts.append('--with-pmix={}'.format(
                    self.__pmix))
            else:
                self.configure_opts.append('--with-pmix')

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
                self.__commands.append('ln -sf {0} {1}'.format(
                    posixpath.join(cuda_home, 'lib64', 'stubs', 'libcuda.so'),
                    posixpath.join(cuda_home, 'lib64', 'stubs', 'libcuda.so.1')))
                if not self.__toolchain.LD_LIBRARY_PATH:
                    build_environment.append('LD_LIBRARY_PATH="{}:$LD_LIBRARY_PATH"'.format(posixpath.join(cuda_home, 'lib64', 'stubs')))

        # Download source from web
        self.__commands.append(self.download_step(recursive=True,
                                                  wd=self.__wd))

        # Generate configure script
        if self.repository:
            self.__commands.append('cd {} && ./autogen.pl'.format(
                self.src_directory))

        # Configure
        self.__commands.append(self.configure_step(
            directory=self.src_directory,
            environment=build_environment,
            toolchain=self.__toolchain))

        # Build
        self.__commands.append(self.build_step())

        # Check
        if self.__check:
            self.__commands.append(self.check_step())

        # Install
        self.__commands.append(self.install_step())

        # Set library path
        libpath = posixpath.join(self.prefix, 'lib')
        if self.ldconfig:
            self.__commands.append(self.ldcache_step(directory=libpath))
        else:
            self.environment_variables['LD_LIBRARY_PATH'] = '{}:$LD_LIBRARY_PATH'.format(libpath)

        # Cleanup
        if self.src_directory:
            remove.append(self.src_directory)
        self.__commands.append(self.cleanup_step(items=remove))

        # Set the environment
        self.environment_variables['PATH'] = '{}:$PATH'.format(
            posixpath.join(self.prefix, 'bin'))

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
        if self.ldconfig:
            instructions.append(shell(
                commands=[self.ldcache_step(
                    directory=posixpath.join(self.prefix, 'lib'))]))
        instructions.append(environment(variables=self.environment_step()))
        return '\n'.join(str(x) for x in instructions)
