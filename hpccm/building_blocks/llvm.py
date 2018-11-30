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

import logging # pylint: disable=unused-import

import hpccm.config

from hpccm.building_blocks.packages import packages
from hpccm.common import linux_distro
from hpccm.primitives.comment import comment
from hpccm.primitives.environment import environment
from hpccm.primitives.shell import shell
from hpccm.toolchain import toolchain

class llvm(object):
    """The `llvm` building block installs the LLVM compilers (clang and
    clang++) from the upstream Linux distribution.

    As a side effect, a toolchain is created containing the LLVM
    compilers.  A toolchain can be passed to other operations that
    want to build using the LLVM compilers.

    # Parameters

    extra_repository: Boolean flag to specify whether to enable an
    extra package repository containing addition LLVM compiler
    packages.  For Ubuntu, setting this flag to True enables the
    `ppa:ubuntu-toolchain-r/test` repository.  For RHEL-based Linux
    distributions, setting this flag to True enables the Software
    Collections (SCL) repository.  The default is False.

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
    l = llvm()
    openmpi(..., toolchain=l.toolchain, ...)
    ```
    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        # Trouble getting MRO with kwargs working correctly, so just call
        # the parent class constructors manually for now.
        #super(llvm, self).__init__(**kwargs)

        self.__extra_repo = kwargs.get('extra_repository', False)
        self.__version = kwargs.get('version', None)

        self.__commands = []       # Filled in below
        self.__compiler_debs = ['clang']  # Filled in below
        self.__compiler_rpms = ['clang']  # Filled in below
        self.__environment = {}    # Filled in below
        self.__ospackages = kwargs.get('ospackages', [])
        self.__runtime_debs = ['libclang1']
        self.__runtime_rpms = ['llvm-libs']

        # Output toolchain
        self.toolchain = toolchain()
        self.toolchain.CC = 'clang'
        self.toolchain.CXX = 'clang++'

        # Install an alternate version, i.e., not the default for
        # the Linux distribution
        if self.__version:
            # Adjust package names based on specified version
            self.__compiler_debs = [
                '{0}-{1}'.format(x, self.__version)
                for x in self.__compiler_debs]
            self.__compiler_rpms = [
                'llvm-toolset-{0}-{1}'.format(self.__version, x)
                for x in self.__compiler_rpms]
            self.__runtime_rpms = [
                'llvm-toolset-{0}-runtime'.format(self.__version),
                'llvm-toolset-{0}-libomp'.format(self.__version),
                'llvm-toolset-{0}-compiler-rt'.format(self.__version)]

        self.__distro()

    def __distro(self):
        """Based on the Linux distribution, set values accordingly.  A user
        specified value overrides any defaults."""

        if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
            # Setup the environment so that the alternate compiler version
            # is the new default
            if self.__version:
                self.__commands.append('update-alternatives --install /usr/bin/clang clang $(which clang-{}) 30'.format(self.__version))
                self.__commands.append('update-alternatives --install /usr/bin/clang++ clang++ $(which clang++-{}) 30'.format(self.__version))
        elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
            # Dependencies on the GNU compiler
            if not self.__ospackages:
                self.__ospackages = ['gcc', 'gcc-c++']

            # Setup the environment so that the alternate compiler version
            # is the new default
            if self.__version:
                self.__environment = {'PATH': '/opt/rh/llvm-toolset-{}/root/usr/bin:$PATH'.format(self.__version),
                                      'LD_LIBRARY_PATH': '/opt/rh/llvm-toolset-{}/root/usr/lib64:$LD_LIBRARY_PATH'.format(self.__version)}
        else: # pragma: no cover
                raise RuntimeError('Unknown Linux distribution')

    def __str__(self):
        """String representation of the building block"""
        instructions = []
        instructions.append(comment('LLVM compiler'))
        if self.__ospackages:
            instructions.append(packages(ospackages=self.__ospackages))
        instructions.append(packages(apt=self.__compiler_debs,
                                     scl=bool(self.__version), # True / False
                                     yum=self.__compiler_rpms))
        if self.__commands:
            instructions.append(shell(commands=self.__commands))
        if self.__environment:
            instructions.append(environment(variables=self.__environment))
        return '\n'.join(str(x) for x in instructions)

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
        instructions.append(packages(apt=self.__runtime_debs,
                                     scl=bool(self.__version), # True / False
                                     yum=self.__runtime_rpms))
        return '\n'.join(str(x) for x in instructions)
