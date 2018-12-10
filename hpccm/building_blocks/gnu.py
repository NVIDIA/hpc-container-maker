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

import logging # pylint: disable=unused-import

import hpccm.config

from hpccm.building_blocks.packages import packages
from hpccm.common import linux_distro
from hpccm.primitives.comment import comment
from hpccm.primitives.environment import environment
from hpccm.primitives.shell import shell
from hpccm.toolchain import toolchain

class gnu(object):
    """The `gnu` building block installs the GNU compilers from the
    upstream Linux distribution.

    As a side effect, a toolchain is created containing the GNU
    compilers.  The toolchain can be passed to other operations that
    want to build using the GNU compilers.

    # Parameters

    cc: Boolean flag to specify whether to install `gcc`.  The default
    is True.

    cxx: Boolean flag to specify whether to install `g++`.  The
    default is True.

    extra_repository: Boolean flag to specify whether to enable an
    extra package repository containing addition GNU compiler
    packages.  For Ubuntu, setting this flag to True enables the
    `ppa:ubuntu-toolchain-r/test` repository.  For RHEL-based Linux
    distributions, setting this flag to True enables the Software
    Collections (SCL) repository.  The default is False.

    fortran: Boolean flag to specify whether to install `gfortran`.
    The default is True.

    version: The version of the GNU compilers to install.  Note that
    the version refers to the Linux distribution packaging, not the
    actual compiler version.  For Ubuntu, the version is appended to
    the default package name, e.g., `gcc-7`.  For RHEL-based Linux
    distributions, the version is inserted into the SCL Developer
    Toolset package name, e.g., `devtoolset-7-gcc`.  For RHEL-based
    Linux distributions, specifying the version automatically sets
    `extra_repository` to True.  The default is an empty value.

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
    g = gnu()
    openmpi(..., toolchain=g.toolchain, ...)
    ```
    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        # Trouble getting MRO with kwargs working correctly, so just call
        # the parent class constructors manually for now.
        #super(gnu, self).__init__(**kwargs)

        self.__cc = kwargs.get('cc', True)
        self.__cxx = kwargs.get('cxx', True)
        self.__extra_repo = kwargs.get('extra_repository', False)
        self.__fortran = kwargs.get('fortran', True)
        self.__version = kwargs.get('version', None)

        self.__commands = []       # Filled in below
        self.__compiler_debs = []  # Filled in below
        self.__compiler_rpms = []  # Filled in below
        self.__environment = {}    # Filled in below
        self.__extra_repo_apt = [] # Filled in below
        self.__runtime_debs = ['libgomp1']
        self.__runtime_rpms = ['libgomp']

        # Output toolchain
        self.toolchain = toolchain()

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
            self.__compiler_rpms = [
                'devtoolset-{1}-{0}'.format(x, self.__version)
                for x in self.__compiler_rpms]

        self.__distro()

    def __distro(self):
        """Based on the Linux distribution, set values accordingly.  A user
        specified value overrides any defaults."""

        # Setup the environment so that the alternate compiler version
        # is the new default
        if self.__version:
            if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
                if self.__cc:
                    self.__commands.append('update-alternatives --install /usr/bin/gcc gcc $(which gcc-{}) 30'.format(self.__version))
                if self.__cxx:
                    self.__commands.append('update-alternatives --install /usr/bin/g++ g++ $(which g++-{}) 30'.format(self.__version))
                if self.__fortran:
                    self.__commands.append('update-alternatives --install /usr/bin/gfortran gfortran $(which gfortran-{}) 30'.format(self.__version))
            elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
                self.__environment = {'PATH': '/opt/rh/devtoolset-{}/root/usr/bin:$PATH'.format(self.__version)}
            else: # pragma: no cover
                raise RuntimeError('Unknown Linux distribution')

    def __str__(self):
        """String representation of the building block"""
        instructions = []
        instructions.append(comment('GNU compiler'))
        instructions.append(packages(apt=self.__compiler_debs,
                                     apt_ppas=self.__extra_repo_apt,
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
        g = gnu(...)
        Stage0 += g
        Stage1 += g.runtime()
        ```
        """
        instructions = []
        instructions.append(comment('GNU compiler runtime'))
        instructions.append(packages(apt=self.__runtime_debs,
                                     apt_ppas=self.__extra_repo_apt,
                                     scl=bool(self.__version), # True / False
                                     yum=self.__runtime_rpms))
        return '\n'.join(str(x) for x in instructions)
