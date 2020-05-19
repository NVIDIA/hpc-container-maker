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

"""AmgX building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import posixpath

import hpccm.config
import hpccm.templates.envvars
import hpccm.templates.ldconfig

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.generic_cmake import generic_cmake
from hpccm.building_blocks.packages import packages
from hpccm.primitives.comment import comment

class amgx(bb_base, hpccm.templates.envvars, hpccm.templates.ldconfig):
    """The `amgx` building block downloads, configures, builds, and installs the [AMGX] component.

    [AMGX]: https://developer.nvidia.com/amgx

    The [CMake](#cmake) building block should be installed prior to this building block.

    Installing an MPI building block before this one is optional and will build the [AMGX] library with MPI support.
    Some Eigensolvers make use of the MAGMA and/or MKL libraries and are only available if the paths to these libraries is specified as shown below in the cmake_opts.

    # Parameters

    repository: The git repository to clone.
    The default is `https://github.com/NVIDIA/AMGX`.

    branch: The git branch to clone.
    AMGX releases are tagged, that is, specifying `branch='v2.1.0'` downloads a particular AMGX version.
    The default is `master`.

    commit: The git commit to clone.
    The default is empty and uses the latest commit on the selected branch of the repository.

    directory: Build from an unpackaged source directory relative to the local build context instead of fetching AMGX sources from a git repository.
    This option is incompatible with `repository`/`branch`/ `commit`.
    The default is `None`.

    cmake_opts: List of options to pass to `cmake`.
    The default value is an empty list.
    See the ["Building"](https://github.com/NVIDIA/AMGX#-building) section of the AMGX documentation of the specified library version for more details.
    Some options are:
      - `CMAKE_NO_MPI:Boolean` (default=`False`): build without MPI support even if the `FindMPI` script finds an MPI library.
      - `AMGX_NO_RPATH:Boolean` (default=`False`): by default CMake adds `-rpath` flags to binaries, this option disables that.
      - `MKL_ROOT_DIR:String`, `MAGMA_ROOT_DIR:String`: MAGMA/MKL are used to accelerate some of the Eigensolvers.
    These solvers will return "error 'not supported'" if AMGX was not build with MKL/MAGMA support.

    ospackages: List of OS packages to install prior to downloading, configuring, and building
    .
    The default value is `[git]`.

    prefix: The top level install location.
    The default is `/usr/local/amgx`.

    toolchain: The toolchain object.
    This should be used if non-default compilers or other toolchain options are needed.
    The default is empty.

    annotate: Boolean flag to specify whether to include annotations (labels).
    The default is False.

    # Examples

    ```python
    amgx(branch='v2.1.0')
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""
        super(amgx, self).__init__(**kwargs)

        self.__repository = kwargs.pop('baseurl', 'https://github.com/NVIDIA/amgx')
        self.__cmake_opts = kwargs.pop('cmake_opts', [])
        self.__version = kwargs.get('branch')
        self.__prefix = kwargs.pop('prefix', '/usr/local/amgx')
        self.__ospackages = kwargs.pop('ospackages', ['git'])

        # Set the configure options
        self.__cmake()

        # Set the environment
        self.environment_variables['CPATH'] = '{}:$CPATH'.format(
            posixpath.join(self.__prefix, 'include'))
        self.environment_variables['LIBRARY_PATH'] = '{}:$LIBRARY_PATH'.format(
            posixpath.join(self.__prefix, 'lib'))
        if not self.ldconfig:
            self.environment_variables['LD_LIBRARY_PATH'] = '{}:$LD_LIBRARY_PATH'.format(posixpath.join(self.__prefix, 'lib'))

        # Setup build configuration
        self.__bb = generic_cmake(
            annotations={'branch': kwargs.get('branch')},
            base_annotation=self.__class__.__name__,
            comment=False,
            cmake_opts=self.__cmake_opts,
            devel_environment=self.environment_variables,
            prefix=self.__prefix,
            runtime_environment=self.environment_variables,
            repository=self.__repository,
            **kwargs)

        # Container instructions
        self += comment('AMGX branch {}'.format(kwargs.get('branch')))
        self += packages(ospackages=self.__ospackages)
        self += self.__bb


    def __cmake(self):
        """Setup CMake options"""
        # Nothing yet

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples

        ```python
        f = amgx(...)
        Stage0 += f
        Stage1 += f.runtime()
        ```
        """
        instructions = []
        instructions.append(comment('AMGX'))
        instructions.append(self.__bb.runtime(_from=_from))
        return '\n'.join(str(x) for x in instructions)
