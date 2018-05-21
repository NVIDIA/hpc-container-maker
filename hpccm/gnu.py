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

from hpccm.comment import comment
from hpccm.packages import packages
from hpccm.toolchain import toolchain

class gnu(object):
    """GNU compiler building block"""

    def __init__(self, **kwargs):
        """Initialize building block"""

        # Trouble getting MRO with kwargs working correctly, so just call
        # the parent class constructors manually for now.
        #super(gnu, self).__init__(**kwargs)

        self.__cc = kwargs.get('cc', True)
        self.__cxx = kwargs.get('cxx', True)
        self.__fortran = kwargs.get('fortran', True)

        self.__compiler_debs = [] # Filled in below
        self.__compiler_rpms = [] # Filled in below
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

    def __str__(self):
        """String representation of the building block"""
        instructions = []
        instructions.append(comment('GNU compiler'))
        instructions.append(packages(apt=self.__compiler_debs,
                                     yum=self.__compiler_rpms))
        return '\n'.join(str(x) for x in instructions)

    def runtime(self, _from='0'):
        """Runtime specification"""
        instructions = []
        instructions.append(comment('GNU compiler runtime'))
        instructions.append(packages(apt=self.__runtime_debs,
                                     yum=self.__runtime_rpms))
        return instructions
