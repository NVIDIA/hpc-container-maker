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

"""Build toolchain"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

class toolchain(object):
    """Class for the build toolchain.  Attributes map to the commonly used
       environment variables, e.g, CC is the C compiler, CXX is the
       C++ compiler."""

    __attrs__ = ['CC', 'CFLAGS', 'CPPFLAGS', 'CUDA_HOME', 'CXX',
                 'CXXFLAGS', 'F77', 'F90', 'FC', 'FCFLAGS', 'FFLAGS',
                 'FLIBS', 'LDFLAGS', 'LD_LIBRARY_PATH', 'LIBS']

    def __init__(self, **kwargs):
        """Initialize toolchain"""

        self.CC = kwargs.get('CC')
        self.CFLAGS = kwargs.get('CFLAGS')
        self.CPPFLAGS = kwargs.get('CPPFLAGS')
        self.CUDA_HOME = kwargs.get('CUDA_HOME')
        self.CXX = kwargs.get('CXX')
        self.CXXFLAGS = kwargs.get('CXXFLAGS')
        self.F77 = kwargs.get('F77')
        self.F90 = kwargs.get('F90')
        self.FC = kwargs.get('FC')
        self.FCFLAGS = kwargs.get('FCFLAGS')
        self.FFLAGS = kwargs.get('FFLAGS')
        self.FLIBS = kwargs.get('FLIBS')
        self.LDFLAGS = kwargs.get('LDFLAGS')
        self.LD_LIBRARY_PATH = kwargs.get('LD_LIBRARY_PATH')
        self.LIBS = kwargs.get('LIBS')

    def __copy__(self):
        """Copy all the attributes even if __dict__ only returns the pairs
           with non-null values."""
        cls = self.__class__
        result = cls.__new__(cls)
        for key in self.__attrs__:
          val = getattr(self, key)
          setattr(result, key, val if val else None)
        return result

    def __deepcopy__(self, memo):
        """Copy all the attributes even if __dict__ only returns the pairs
           with non-null values."""
        result = self.__copy__()
        memo[id(self)] = result
        return result

    @property
    def __dict__(self):
        """Return only those attributes that have non-null values.  This
           enables usage like 'environment(variables=var(toolchain))'"""
        return {key: getattr(self, key) for key in self.__attrs__
                if getattr(self, key)}
