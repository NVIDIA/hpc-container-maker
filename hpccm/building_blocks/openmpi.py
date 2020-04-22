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
import hpccm.templates.downloader
import hpccm.templates.envvars
import hpccm.templates.ldconfig

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.generic_autotools import generic_autotools
from hpccm.building_blocks.packages import packages
from hpccm.common import linux_distro
from hpccm.primitives.comment import comment
from hpccm.toolchain import toolchain

class openmpi(bb_base, hpccm.templates.downloader, hpccm.templates.envvars,
              hpccm.templates.ldconfig):
    """The `openmpi` building block configures, builds, and installs the
    [OpenMPI](https://www.open-mpi.org) component.

    As a side effect, a toolchain is created containing the MPI
    compiler wrappers.  The tool can be passed to other operations
    that want to build using the MPI compiler wrappers.

    # Parameters

    annotate: Boolean flag to specify whether to include annotations
    (labels).  The default is False.

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
    `4.0.3`.

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

        self.__baseurl = kwargs.pop('baseurl',
                                    'https://www.open-mpi.org/software/ompi')
        self.__configure_opts = kwargs.pop('configure_opts',
                                           ['--disable-getpwuid',
                                            '--enable-orterun-prefix-by-default'])
        self.__cuda = kwargs.pop('cuda', True)
        self.__default_repository = 'https://github.com/open-mpi/ompi.git'
        self.__infiniband = kwargs.pop('infiniband', True)
        self.__ospackages = kwargs.pop('ospackages', [])
        self.__pmi = kwargs.pop('pmi', False)
        self.__pmix = kwargs.pop('pmix', False)
        self.__prefix = kwargs.pop('prefix', '/usr/local/openmpi')
        self.__recursive = kwargs.pop('recursive', True)
        self.__runtime_ospackages = [] # Filled in by __distro()
        # Input toolchain, i.e., what to use when building
        self.__toolchain = kwargs.pop('toolchain', toolchain())
        self.__version = kwargs.pop('version', '4.0.3')
        self.__ucx = kwargs.pop('ucx', False)

        # Output toolchain
        self.toolchain = toolchain(CC='mpicc', CXX='mpicxx', F77='mpif77',
                                   F90='mpif90', FC='mpifort')

        # Set the configure options
        self.__configure()

        # Set the Linux distribution specific parameters
        self.__distro()

        # Set the download specific parameters
        self.__download()
        kwargs['repository'] = self.repository
        kwargs['url'] = self.url

        # Setup the environment variables
        self.environment_variables['PATH'] = '{}:$PATH'.format(
            posixpath.join(self.__prefix, 'bin'))
        if not self.ldconfig:
            self.environment_variables['LD_LIBRARY_PATH'] = '{}:$LD_LIBRARY_PATH'.format(posixpath.join(self.__prefix, 'lib'))

        # Setup build configuration
        self.__bb = generic_autotools(
            annotations={'version': self.__version} if not self.repository else {},
            base_annotation=self.__class__.__name__,
            comment=False,
            configure_opts=self.__configure_opts,
            devel_environment=self.environment_variables,
            preconfigure=['./autogen.pl'] if self.repository else None,
            prefix=self.__prefix,
            recursive=self.__recursive,
            runtime_environment=self.environment_variables,
            toolchain=self.__toolchain,
            **kwargs)

        # Container instructions
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
        self += self.__bb

    def __configure(self):
        """Setup configure options based on user parameters"""

        # CUDA
        if self.__cuda:
            if self.__toolchain.CUDA_HOME:
                self.__configure_opts.append(
                    '--with-cuda={}'.format(self.__toolchain.CUDA_HOME))
            else:
                self.__configure_opts.append('--with-cuda')
        else:
            self.__configure_opts.append('--without-cuda')

        # PMI
        if self.__pmi:
            if isinstance(self.__pmi, string_types):
                # Use specified path
                self.__configure_opts.append(
                    '--with-pmi={}'.format(self.__pmi))
            else:
                self.__configure_opts.append('--with-pmi')

        # PMIX
        if self.__pmix:
            if isinstance(self.__pmix, string_types):
                # Use specified path
                self.__configure_opts.append('--with-pmix={}'.format(
                    self.__pmix))
            else:
                self.__configure_opts.append('--with-pmix')

        # InfiniBand
        if self.__infiniband:
            self.__configure_opts.append('--with-verbs')
        else:
            self.__configure_opts.append('--without-verbs')

        # UCX
        if self.__ucx:
            if isinstance(self.__ucx, string_types):
                # Use specified path
                self.__configure_opts.append(
                    '--with-ucx={}'.format(self.__ucx))
            else:
                self.__configure_opts.append('--with-ucx')

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

    def __download(self):
        """Set download source based on user parameters"""

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
        instructions.append(self.__bb.runtime(_from=_from))
        return '\n'.join(str(x) for x in instructions).rstrip()
