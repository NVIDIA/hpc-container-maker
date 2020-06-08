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

"""LLVM compiler building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from distutils.version import StrictVersion
import logging

import hpccm.config
import hpccm.templates.envvars

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.packages import packages
from hpccm.common import cpu_arch, linux_distro
from hpccm.primitives.comment import comment
from hpccm.primitives.environment import environment
from hpccm.primitives.shell import shell
from hpccm.toolchain import toolchain

class llvm(bb_base, hpccm.templates.envvars):
    """The `llvm` building block installs the LLVM compilers (clang and
    clang++) from the upstream Linux distribution.

    As a side effect, a toolchain is created containing the LLVM
    compilers.  A toolchain can be passed to other operations that
    want to build using the LLVM compilers.

    # Parameters

    environment: Boolean flag to specify whether the environment
    (`CPATH`, `LD_LIBRARY_PATH` and `PATH`) should be modified to
    include the LLVM compilers. The default is True.

    extra_repository: Boolean flag to specify whether to enable an extra package repository containing addition LLVM compiler packages.  For Ubuntu, setting this flag to True enables the `ppa:ubuntu-toolchain-r/test`
    repository.  For RHEL-based Linux distributions, setting this flag
    to True enables the Software Collections (SCL) repository.  The
    default is False.

    extra_tools: Boolean flag to specify whether to also install
    `clang-format` and `clang-tidy`.  The default is False.

    nightly: Boolean flag to specify whether to use the [nightly LLVM packages](https://apt.llvm.org).
    This option is ignored if the base image is not Ubuntu.

    version: The version of the LLVM compilers to install.  Note that
    the version refers to the Linux distribution packaging, not the
    actual compiler version.  For Ubuntu, the version is appended to
    the default package name, e.g., `clang-6.0`.  For RHEL-based Linux
    distributions, the version is inserted into the SCL Developer
    Toolset package name, e.g., `llvm-toolset-7-clang`.  For
    RHEL-based Linux distributions, specifying the version
    automatically sets `extra_repository` to True.  The default is an
    empty value.

    # Examples

    ```python
    llvm()
    ```

    ```python
    llvm(extra_repository=True, version='7')
    ```

    ```python
    llvm(nightly=True, version='11')
    ```

    ```python
    l = llvm()
    openmpi(..., toolchain=l.toolchain, ...)
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(llvm, self).__init__(**kwargs)

        self.__apt_keys = []       # Filled in below
        self.__apt_repositories = [] # Filled in below
        self.__commands = []       # Filled in below
        self.__compiler_debs = []  # Filled in below
        self.__compiler_rpms = []  # Filled in below
        self.__extra_repo = kwargs.get('extra_repository', False)
        self.__extra_tools = kwargs.get('extra_tools', False)
        self.__nightly = kwargs.get('nightly', False)
        self.__ospackages = kwargs.get('ospackages', []) # Filled in below
        self.__runtime_debs = []   # Filled in below
        self.__runtime_ospackages = [] # Filled in below
        self.__runtime_rpms = []   # Filled in below
        self.__version = kwargs.get('version', None)

        # Output toolchain
        self.toolchain = toolchain()
        self.toolchain.CC = 'clang'
        self.toolchain.CXX = 'clang++'

        # Set the packages to install based on the Linux distribution
        # and CPU architecture
        self.__setup()

        # Fill in container instructions
        self.__instructions()

    def __setup(self):
        """Based on the Linux distribution and CPU architecture, set values
        accordingly."""

        if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
            self.__ospackages = []

            if self.__nightly and self.__version:
                # Nightly packages from apt.llvm.org
                if hpccm.config.g_cpu_arch != cpu_arch.X86_64:
                    raise RuntimeError('LLVM nightly builds only available for x86')

                self.__compiler_debs = ['clang-{}'.format(self.__version),
                                        'libomp-{}-dev'.format(self.__version)]
                self.__runtime_debs = ['libclang1-{}'.format(self.__version),
                                       'llvm-{}-runtime'.format(self.__version)]
                self.__apt_keys = ['https://apt.llvm.org/llvm-snapshot.gpg.key']
                self.__apt_repositories = self.__nightly_package_repos()

                self.__ospackages = ['apt-transport-https', 'ca-certificates',
                                     'gnupg', 'wget']
                self.__runtime_ospackages = self.__ospackages

                # Setup the environment so that the alternate compiler
                # version is the new default
                self.__commands.append('update-alternatives --install /usr/bin/clang clang $(which clang-{}) 30'.format(self.__version))
                self.__commands.append('update-alternatives --install /usr/bin/clang++ clang++ $(which clang++-{}) 30'.format(self.__version))

                # Install and configure clang-format and clang-tidy
                if self.__extra_tools:
                    self.__compiler_debs.extend([
                        'clang-format-{}'.format(self.__version),
                        'clang-tidy-{}'.format(self.__version)])
                    self.__commands.append('update-alternatives --install /usr/bin/clang-format clang-format $(which clang-format-{}) 30'.format(self.__version))
                    self.__commands.append('update-alternatives --install /usr/bin/clang-tidy clang-tidy $(which clang-tidy-{}) 30'.format(self.__version))

            elif self.__version:
                # distro provided version
                self.__compiler_debs = ['clang-{}'.format(self.__version),
                                        'libomp-dev']
                self.__runtime_debs = ['libclang1', 'libomp5']

                # Setup the environment so that the alternate compiler
                # version is the new default
                self.__commands.append('update-alternatives --install /usr/bin/clang clang $(which clang-{}) 30'.format(self.__version))
                self.__commands.append('update-alternatives --install /usr/bin/clang++ clang++ $(which clang++-{}) 30'.format(self.__version))

                # Install and configure clang-format and clang-tidy
                if self.__extra_tools:
                    self.__compiler_debs.append('clang-format-{}'.format(
                        self.__version))
                    self.__compiler_debs.append('clang-tidy-{}'.format(
                        self.__version))
                    self.__commands.append('update-alternatives --install /usr/bin/clang-format clang-format $(which clang-format-{}) 30'.format(self.__version))
                    self.__commands.append('update-alternatives --install /usr/bin/clang-tidy clang-tidy $(which clang-tidy-{}) 30'.format(self.__version))
            else:
                self.__compiler_debs = ['clang', 'libomp-dev']
                self.__runtime_debs = ['libclang1', 'libomp5']

                if self.__extra_tools:
                    self.__compiler_debs.extend(['clang-format', 'clang-tidy'])

        elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
            # Dependencies on the GNU compiler
            self.__ospackages = ['gcc', 'gcc-c++']

            # Version that appears in paths below
            compiler_version = ''

            if self.__version:
                if hpccm.config.g_linux_version >= StrictVersion('8.0'):
                    # Multiple versions are not available for CentOS 8
                    self.__compiler_rpms = ['llvm-toolset-8.0.1']
                    self.__runtime_rpms = ['llvm-libs-8.0.1', 'libomp']
                    compiler_version = '8'

                    if self.__extra_tools:
                        self.__compiler_rpms.append('clang-tools-extra-8.0.1')
                else:
                    # CentOS 7
                    self.__compiler_rpms = [
                        'llvm-toolset-{}-clang'.format(self.__version),
                        'llvm-toolset-{}-libomp-devel'.format(self.__version)]
                    self.__runtime_rpms = [
                        'llvm-toolset-{}-runtime'.format(self.__version),
                        'llvm-toolset-{}-libomp'.format(self.__version),
                        'llvm-toolset-{}-compiler-rt'.format(self.__version)]
                    compiler_version = '4.8.2'

                    if self.__extra_tools:
                        self.__compiler_rpms.append('llvm-toolset-{}-clang-tools-extra'.format(self.__version))

                    # Setup environment for devtoolset
                    self.environment_variables['PATH'] = '/opt/rh/llvm-toolset-{}/root/usr/bin:$PATH'.format(self.__version)
                    self.environment_variables['LD_LIBRARY_PATH'] = '/opt/rh/llvm-toolset-{}/root/usr/lib64:$LD_LIBRARY_PATH'.format(self.__version)
            else:
                self.__compiler_rpms = ['clang']
                if hpccm.config.g_linux_version >= StrictVersion('8.0'):
                    # CentOS 8
                    self.__runtime_rpms = ['llvm-libs', 'libomp']
                    compiler_version = '8'

                    if self.__extra_tools:
                        self.__compiler_rpms.append('clang-tools-extra')
                else:
                    # CentOS 7
                    self.__runtime_rpms = ['llvm-libs', 'libgomp']
                    compiler_version = '4.8.2'

                    if self.__extra_tools: # pragma: no cover
                        logging.warning('llvm extra tools are not available for default CentOS 7, specify a LLVM version')

            # The default llvm configuration for CentOS is unable to
            # locate some gcc components. Setup the necessary gcc
            # environment.
            if hpccm.config.g_cpu_arch == cpu_arch.AARCH64:
                self.environment_variables['COMPILER_PATH'] = '/usr/lib/gcc/aarch64-redhat-linux/{}:$COMPILER_PATH'.format(compiler_version)
                self.environment_variables['CPATH'] = '/usr/include/c++/{0}:/usr/include/c++/{0}/aarch64-redhat-linux:/usr/lib/gcc/aarch64-redhat-linux/{0}/include:$CPATH'.format(compiler_version)
                self.environment_variables['LIBRARY_PATH'] = '/usr/lib/gcc/aarch64-redhat-linux/{}'.format(compiler_version)
            elif hpccm.config.g_cpu_arch == cpu_arch.X86_64:
                self.environment_variables['CPATH'] = '/usr/lib/gcc/x86_64-redhat-linux/{}/include:$CPATH'.format(compiler_version)
            else:
                # Packages for CentOS + PPC64LE are not available
                raise RuntimeError('Unsupported processor architecture')

        else: # pragma: no cover
            raise RuntimeError('unknown Linux distribution')

    def __instructions(self):
        """Fill in container instructions"""

        self += comment('LLVM compiler')
        if self.__ospackages:
            self += packages(ospackages=self.__ospackages)
        self += packages(apt=self.__compiler_debs,
                         apt_keys=self.__apt_keys,
                         apt_repositories=self.__apt_repositories,
                         scl=bool(self.__version), # True / False
                         yum=self.__compiler_rpms)
        if self.__commands:
            self += shell(commands=self.__commands)
        self += environment(variables=self.environment_step())

    def __nightly_package_repos(self):
        """Return the package repositories for the given distro and llvm
        version.  The development branch repositories are not
        versioned and must be handled differently.  Currently the
        development branch is version 11."""

        codename = 'xenial'
        codename_ver = 'xenial'

        if (hpccm.config.g_linux_version >= StrictVersion('18.0') and
            hpccm.config.g_linux_version < StrictVersion('19.0')):
            codename = 'bionic'
            if self.__version == '11':
                codename_ver = 'bionic'
            else:
                codename_ver = 'bionic-{}'.format(self.__version)
        elif (hpccm.config.g_linux_version >= StrictVersion('16.0') and
              hpccm.config.g_linux_version < StrictVersion('17.0')):
            codename = 'xenial'
            if self.__version == '11':
                codename_ver = 'xenial'
            else:
                codename_ver = 'xenial-{}'.format(self.__version)
        else:
            raise RuntimeError('Unsupported Ubuntu version')

        return [
            'deb http://apt.llvm.org/{0}/ llvm-toolchain-{1} main'.format(codename, codename_ver),
            'deb-src http://apt.llvm.org/{0}/ llvm-toolchain-{1} main'.format(codename, codename_ver)]

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples

        ```python
        l = llvm(...)
        Stage0 += l
        Stage1 += l.runtime()
        ```
        """
        instructions = []
        instructions.append(comment('LLVM compiler runtime'))
        if self.__runtime_ospackages:
            instructions.append(packages(ospackages=self.__runtime_ospackages))
        instructions.append(packages(apt=self.__runtime_debs,
                                     apt_keys=self.__apt_keys,
                                     apt_repositories=self.__apt_repositories,
                                     scl=bool(self.__version), # True / False
                                     yum=self.__runtime_rpms))
        return '\n'.join(str(x) for x in instructions)
