# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
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

"""MAGMA building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import posixpath

import hpccm.templates.envvars
import hpccm.templates.ldconfig

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.generic_cmake import generic_cmake
from hpccm.building_blocks.packages import packages
from hpccm.primitives.comment import comment

class magma(bb_base, hpccm.templates.envvars, hpccm.templates.ldconfig):
    """The `magma` building block configures, builds, and installs the
    [MAGMA](https://icl.cs.utk.edu/magma) component.

    The [CMake](#cmake) building block should be installed prior to
    this building block.

    Either the [MKL](#mkl) or [OpenBLAS](#openblas) building block
    should also be installed.

    # Parameters

    annotate: Boolean flag to specify whether to include annotations
    (labels).  The default is False.

    cmake_opts: List of options to pass to `cmake`.  The default value
    is an empty list.

    gpu_target: List of GPU architectures to compile.  The default
    values are `Pascal`, `Volta`, and `Turing`.

    ospackages: List of OS packages to install prior to configuring
    and building.  The default values are `tar` and `wget`.

    prefix: The top level install location.  The default value is
    `/usr/local/magma`.

    toolchain: The toolchain object.  This should be used if
    non-default compilers or other toolchain options are needed.  The
    default is empty.

    version: The version of MAGMA source to download.  The default
    value is `2.5.3`.

    # Examples

    ```python
    magma(prefix='/opt/magma', version='2.5.3')
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(magma, self).__init__(**kwargs)

        self.__baseurl = kwargs.pop('baseurl', 'http://icl.utk.edu/projectsfiles/magma/downloads')
        self.__cmake_opts = kwargs.pop('cmake_opts', [])
        self.__gpu_target = kwargs.pop('gpu_target',
                                       ['Pascal', 'Volta', 'Turing'])
        self.__ospackages = kwargs.pop('ospackages', ['tar', 'wget'])
        self.__prefix = kwargs.pop('prefix', '/usr/local/magma')
        self.__version = kwargs.pop('version', '2.5.3')

        # Set the cmake options
        self.__cmake()

        # Setup the environment variables
        self.environment_variables['CPATH'] = '{}:$CPATH'.format(
            posixpath.join(self.__prefix, 'include'))
        self.environment_variables['LIBRARY_PATH'] = '{}:$LIBRARY_PATH'.format(
            posixpath.join(self.__prefix, 'lib'))
        if not self.ldconfig:
            self.environment_variables['LD_LIBRARY_PATH'] = '{}:$LD_LIBRARY_PATH'.format(posixpath.join(self.__prefix, 'lib'))

        # Setup build configuration
        self.__bb = generic_cmake(
            annotations={'version': self.__version},
            base_annotation=self.__class__.__name__,
            comment=False,
            cmake_opts=self.__cmake_opts,
            devel_environment=self.environment_variables,
            prefix=self.__prefix,
            runtime_environment=self.environment_variables,
            url='{0}/magma-{1}.tar.gz'.format(self.__baseurl, self.__version),
            **kwargs)

        # Container instructions
        self += comment('MAGMA version {}'.format(self.__version))
        self += packages(ospackages=self.__ospackages)
        self += self.__bb

    def __cmake(self):
        """Setup cmake options based on users parameters"""

        # GPU architectures
        if self.__gpu_target:
            self.__cmake_opts.append('-DGPU_TARGET="{}"'.format(
                ' '.join(self.__gpu_target)))

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples
        ```python
        m = magma(...)
        Stage0 += m
        Stage1 += m.runtime()
        ```
        """
        instructions = []
        instructions.append(comment('MAGMA'))
        instructions.append(self.__bb.runtime(_from=_from))
        return '\n'.join(str(x) for x in instructions)
