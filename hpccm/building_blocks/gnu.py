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

"""GNU compiler building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from distutils.version import StrictVersion
import posixpath

import hpccm.config
import hpccm.templates.ConfigureMake
import hpccm.templates.envvars
import hpccm.templates.git
import hpccm.templates.ldconfig
import hpccm.templates.rm
import hpccm.templates.tar
import hpccm.templates.wget

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.packages import packages
from hpccm.common import linux_distro
from hpccm.primitives.comment import comment
from hpccm.primitives.copy import copy
from hpccm.primitives.environment import environment
from hpccm.primitives.shell import shell
from hpccm.toolchain import toolchain

class gnu(bb_base, hpccm.templates.ConfigureMake, hpccm.templates.envvars,
          hpccm.templates.git, hpccm.templates.ldconfig, hpccm.templates.rm,
          hpccm.templates.tar, hpccm.templates.wget):
    """The `gnu` building block installs the GNU compilers from the
    upstream Linux distribution.

    As a side effect, a toolchain is created containing the GNU
    compilers.  The toolchain can be passed to other operations that
    want to build using the GNU compilers.

    # Parameters

    cc: Boolean flag to specify whether to install `gcc`.  The default
    is True.

    configure_opts: List of options to pass to `configure`.  The
    default value is `--disable-multilib`. This option is only
    recognized if a source build is enabled.

    cxx: Boolean flag to specify whether to install `g++`.  The
    default is True.

    environment: Boolean flag to specify whether the environment
    (`LD_LIBRARY_PATH` and `PATH`) should be modified to include
    the GNU compiler. The default is True.

    extra_repository: Boolean flag to specify whether to enable an
    extra package repository containing addition GNU compiler
    packages.  For Ubuntu, setting this flag to True enables the
    `ppa:ubuntu-toolchain-r/test` repository.  For RHEL-based Linux
    distributions, setting this flag to True enables the Software
    Collections (SCL) repository.  The default is False.

    fortran: Boolean flag to specify whether to install `gfortran`.
    The default is True.

    ldconfig: Boolean flag to specify whether the GNU library
    directory should be added dynamic linker cache.  If False, then
    `LD_LIBRARY_PATH` is modified to include the GNU library
    directory. The default value is False. This option is only
    recognized if a source build is enabled.

    openacc: Boolean flag to control whether a OpenACC enabled
    compiler is built. If True, adds `--with-cuda-driver` and
    `--enable-offload-targets=nvptx-none` to the list of host compiler
    `configure` options and also builds the accelerator compiler and
    dependencies (`nvptx-tools` and `nvptx-newlib`). The default value
    is False. This option is only recognized if a source build is
    enabled.

    ospackages: List of OS packages to install prior to configuring
    and building.  For Ubuntu, the default values are `bzip2`, `file`,
    `gcc`, `g++`, `git`, `make`, `perl`, `tar`, `wget`, and
    `xz-utils`.  For RHEL-based Linux distributions, the default
    values are `bzip2`, `file`, `gcc`, `gcc-c++`, `git`, `make`,
    `perl`, `tar`, `wget`, and `xz`. This option is only recognized if
    a source build is enabled.

    prefix: The top level install location.  The default value is
    `/usr/local/gnu`. This option is only recognized if a source build
    is enabled.

    source: Boolean flag to control whether to build the GNU compilers
    from source. The default value is False.

    version: The version of the GNU compilers to install.  Note that
    the version refers to the Linux distribution packaging, not the
    actual compiler version.  For Ubuntu, the version is appended to
    the default package name, e.g., `gcc-7`.  For RHEL-based Linux
    distributions, the version is inserted into the SCL Developer
    Toolset package name, e.g., `devtoolset-7-gcc`.  For RHEL-based
    Linux distributions, specifying the version automatically sets
    `extra_repository` to True.  If a source build is enabled, the
    version is the compiler tarball version on the GNU FTP site and
    the version must be specified. The default is an empty value.

    # Examples

    ```python
    gnu()
    ```

    ```python
    gnu(fortran=False)
    ```

    ```python
    gnu(extra_repository=True, version='7')
    ```

    ```python
    gnu(openacc=True, source=True, version='9.1.0')
    ```

    ```python
    g = gnu()
    openmpi(..., toolchain=g.toolchain, ...)
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(gnu, self).__init__(**kwargs)

        self.__baseurl = kwargs.get('baseurl', 'http://ftpmirror.gnu.org/gcc')
        self.__cc = kwargs.get('cc', True)
        self.configure_opts = kwargs.get('configure_opts',
                                         ['--disable-multilib'])
        self.__cxx = kwargs.get('cxx', True)
        self.__extra_repo = kwargs.get('extra_repository', False)
        self.__fortran = kwargs.get('fortran', True)
        self.__openacc = kwargs.get('openacc', False)
        self.__ospackages = kwargs.get('ospackages', [])
        self.prefix = kwargs.get('prefix', '/usr/local/gnu')
        self.__source = kwargs.get('source', False)
        self.__version = kwargs.get('version', None)
        self.__wd = '/var/tmp' # working directory

        self.__commands = []       # Filled in below
        self.__compiler_debs = []  # Filled in below
        self.__compiler_rpms = []  # Filled in below
        self.__extra_repo_apt = [] # Filled in below
        self.__runtime_debs = ['libgomp1']
        self.__runtime_rpms = ['libgomp']

        # Output toolchain
        self.toolchain = toolchain()

        if self.__source:
            self.__build()
        else:
            self.__repository()

        # Set the Linux distribution specific parameters
        self.__distro()

        # Fill in container instructions
        self.__instructions()

    def __build(self):
        """Build compilers from source"""

        if not self.__version:
            raise RuntimeError('The compiler version must be specified when performing a source build')

        # Determine which compiler frontends to build
        languages = []
        if self.__cc:
            languages.append('c')
        if self.__cxx:
            languages.append('c++')
        if self.__fortran:
            languages.append('fortran')
        if self.__openacc:
            languages.append('lto')

        # Download source from web
        tarball = 'gcc-{0}.tar.xz'.format(self.__version)
        url = '{0}/gcc-{1}/{2}'.format(self.__baseurl, self.__version, tarball)
        self.__commands.append(self.download_step(url=url, directory=self.__wd))

        # Unpackage
        self.__commands.append(self.untar_step(
            tarball=posixpath.join(self.__wd, tarball),
            directory=self.__wd))

        # Download prerequisites
        self.__commands.append(
            'cd {} && ./contrib/download_prerequisites'.format(
                posixpath.join(self.__wd, 'gcc-{}'.format(self.__version))))

        # Configure accelerator compiler and dependencies
        if self.__openacc:
            # Build nvptx-tools
            # Download
            self.__commands.append(
                self.clone_step(repository='https://github.com/MentorEmbedded/nvptx-tools.git',
                                branch='master', path=self.__wd))

            # Configure
            nvptx_tools = hpccm.templates.ConfigureMake(prefix=self.prefix)
            self.__commands.append(nvptx_tools.configure_step(
                directory=posixpath.join(self.__wd, 'nvptx-tools')))
            # Build
            self.__commands.append(nvptx_tools.build_step())
            self.__commands.append(nvptx_tools.install_step())
            # Cleanup
            self.__commands.append(self.cleanup_step(
                items=[posixpath.join(self.__wd, 'nvptx-tools')]))

            # Setup nvptx-newlib
            self.__commands.append('cd {}'.format(self.__wd))
            self.__commands.append(
                self.clone_step(repository='https://github.com/MentorEmbedded/nvptx-newlib',
                                branch='master', path=self.__wd))
            self.__commands.append('ln -s {0} {1}'.format(
                posixpath.join(self.__wd, 'nvptx-newlib', 'newlib'),
                posixpath.join(self.__wd, 'gcc-{}'.format(self.__version),
                               'newlib')))

            # Accelerator compiler

            # Configure
            accel = hpccm.templates.ConfigureMake(prefix=self.prefix)
            self.__commands.append(accel.configure_step(
                build_directory=posixpath.join(self.__wd, 'accel_objdir'),
                directory=posixpath.join(self.__wd,
                                         'gcc-{}'.format(self.__version)),
                opts=['--enable-languages={}'.format(','.join(languages)),
                      '--target=nvptx-none',
                      '--enable-as-accelerator-for=x86_64-pc-linux-gnu',
                      '--disable-sjlj-exceptions',
                      '--enable-newlib-io-long-long',
                      '--disable-multilib']))

            # Build
            self.__commands.append(accel.build_step())

            # Install
            self.__commands.append(accel.install_step())

        # Configure host compiler
        if self.__openacc:
            self.configure_opts.extend(['--with-cuda-driver=/usr/local/cuda',
                                        '--enable-offload-targets=nvptx-none={}/nvptx-none'.format(self.prefix)])

        self.configure_opts.append('--enable-languages={}'.format(','.join(languages)))

        self.__commands.append(self.configure_step(
            build_directory=posixpath.join(self.__wd, 'objdir'),
            directory=posixpath.join(self.__wd,
                                     'gcc-{}'.format(self.__version))))

        # Build
        self.__commands.append(self.build_step())

        # Install
        self.__commands.append(self.install_step())

        # Environment
        self.environment_variables['PATH'] = '{}:$PATH'.format(
            posixpath.join(self.prefix, 'bin'))
        if self.ldconfig:
            self.__commands.append(self.ldcache_step(
                directory=posixpath.join(self.prefix, 'lib64')))
        else:
            self.environment_variables['LD_LIBRARY_PATH'] = '{}:$LD_LIBRARY_PATH'.format(posixpath.join(self.prefix, 'lib64'))

        # Cleanup
        self.__commands.append(self.cleanup_step(
            items=[posixpath.join(self.__wd, tarball),
                   posixpath.join(self.__wd, 'gcc-{}'.format(self.__version)),
                   posixpath.join(self.__wd, 'objdir')]))
        if self.__openacc:
            self.__commands.append(self.cleanup_step(
                items=[posixpath.join(self.__wd, 'accel_objdir'),
                       posixpath.join(self.__wd, 'nvptx-newlib')]))

    def __distro(self):
        """Based on the Linux distribution, set values accordingly.  A user
        specified value overrides any defaults."""

        if self.__source:
            # Build dependencies
            if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
                self.__ospackages = ['bzip2', 'file', 'gcc', 'g++', 'git',
                                     'make', 'perl', 'tar', 'wget', 'xz-utils']
            elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
                self.__ospackages = ['bzip2', 'file', 'gcc', 'gcc-c++', 'git',
                                     'make', 'perl', 'tar', 'wget', 'xz']
            else: # pragma: no cover
                raise RuntimeError('Unknown Linux distribution')

        elif self.__version and not self.__source:
            # Setup the environment so that the alternate compiler version
            # is the new default
            alternatives = {}
            if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
                if self.__cc:
                    alternatives['gcc'] = '$(which gcc-{})'.format(
                        self.__version)
                if self.__cxx:
                    alternatives['g++'] = '$(which g++-{})'.format(
                        self.__version)
                if self.__fortran:
                    alternatives['gfortran'] = '$(which gfortran-{})'.format(
                        self.__version)
                alternatives['gcov'] = '$(which gcov-{})'.format(
                    self.__version)
            elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
                # Default for CentOS 7
                toolset_path = '/opt/rh/devtoolset-{}/root/usr/bin'.format(
                    self.__version)
                if hpccm.config.g_linux_version >= StrictVersion('8.0'):
                    # CentOS 8
                    toolset_path = '/opt/rh/gcc-toolset-{}/root/usr/bin'.format(self.__version)

                if self.__cc:
                    alternatives['gcc'] = posixpath.join(toolset_path, 'gcc')
                if self.__cxx:
                    alternatives['g++'] = posixpath.join(toolset_path, 'g++')
                if self.__fortran:
                    alternatives['gfortran'] = posixpath.join(toolset_path,
                                                              'gfortran')
                alternatives['gcov'] = posixpath.join(toolset_path, 'gcov')

            else: # pragma: no cover
                raise RuntimeError('Unknown Linux distribution')

            for tool,alt in sorted(alternatives.items()):
                self.__commands.append('update-alternatives --install {0} {1} {2} 30'.format(posixpath.join('/usr/bin', tool), tool, alt))

    def __instructions(self):
        """Fill in container instructions"""
        self += comment('GNU compiler')
        if self.__source:
            # Installing from source
            self += packages(ospackages=self.__ospackages)
        else:
            # Installing from package repository
            self += packages(apt=self.__compiler_debs,
                             apt_ppas=self.__extra_repo_apt,
                             release_stream=bool(self.__version), # True/False
                             scl=bool(self.__version), # True / False
                             yum=self.__compiler_rpms)
        if self.__commands:
            self += shell(commands=self.__commands)
        self += environment(variables=self.environment_step())

    def __repository(self):
        """Setup installation from a package repository"""

        if self.__cc:
            self.__compiler_debs.append('gcc')
            self.__compiler_rpms.append('gcc')
            self.toolchain.CC = 'gcc'

        if self.__cxx:
            self.__compiler_debs.append('g++')
            self.__compiler_rpms.append('gcc-c++')
            self.toolchain.CXX = 'g++'

        if self.__fortran:
            self.__compiler_debs.append('gfortran')
            self.__runtime_debs.append('libgfortran3')
            self.__compiler_rpms.append('gcc-gfortran')
            self.__runtime_rpms.append('libgfortran')
            self.toolchain.F77 = 'gfortran'
            self.toolchain.F90 = 'gfortran'
            self.toolchain.FC = 'gfortran'

        # Install an alternate version, i.e., not the default for
        # the Linux distribution
        if self.__version:
            if self.__extra_repo:
                self.__extra_repo_apt = ['ppa:ubuntu-toolchain-r/test']

            # Adjust package names based on specified version
            self.__compiler_debs = [
                '{0}-{1}'.format(x, self.__version)
                for x in self.__compiler_debs]

            if hpccm.config.g_linux_version >= StrictVersion('8.0'):
                # CentOS 8
                self.__compiler_rpms = [
                    'gcc-toolset-{1}-{0}'.format(x, self.__version)
                    for x in self.__compiler_rpms]
            else:
                # CentOS 7
                self.__compiler_rpms = [
                    'devtoolset-{1}-{0}'.format(x, self.__version)
                    for x in self.__compiler_rpms]

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples

        ```python
        g = gnu(...)
        Stage0 += g
        Stage1 += g.runtime()
        ```
        """
        instructions = []
        instructions.append(comment('GNU compiler runtime'))
        if self.__source:
            instructions.append(copy(_from=_from,
                                     dest=posixpath.join(self.prefix, 'lib64'),
                                     src=posixpath.join(self.prefix, 'lib64')))
            if self.ldconfig:
                instructions.append(shell(
                    commands=[self.ldcache_step(
                        directory=posixpath.join(self.prefix, 'lib64'))]))
            else:
                instructions.append(environment(
                    variables=self.environment_step(
                        include_only=['LD_LIBRARY_PATH'])))
        else:
            instructions.append(
                packages(apt=self.__runtime_debs,
                         apt_ppas=self.__extra_repo_apt,
                         release_stream=bool(self.__version), # True / False
                         scl=bool(self.__version), # True / False
                         yum=self.__runtime_rpms))

        return '\n'.join(str(x) for x in instructions)
