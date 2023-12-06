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

"""NVSHMEM building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import posixpath

import hpccm.templates.downloader
import hpccm.templates.envvars
import hpccm.templates.ldconfig
import hpccm.templates.rm
import hpccm.templates.tar

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.generic_cmake import generic_cmake
from hpccm.building_blocks.packages import packages
from hpccm.primitives.comment import comment
from hpccm.primitives.copy import copy
from hpccm.primitives.environment import environment
from hpccm.primitives.shell import shell

class nvshmem(bb_base, hpccm.templates.downloader, hpccm.templates.envvars,
              hpccm.templates.ldconfig, hpccm.templates.rm,
              hpccm.templates.tar):
    """The `nvshmem` building block builds and installs the
    [NVSHMEM](https://developer.nvidia.com/nvshmem) component.  CMake
    version 3.19 or later is required and must be installed separately.

    # Parameters

    build_examples: Boolean flag to specify whether the NVSHMEM
    examples should be built.  The default is False.

    build_packages: Boolean flag to specify whether the RPM and deb
    packages should be built.  The default is False.

    cmake_opts: List of additional options to pass to `cmake`.  The
    default value is an empty list.

    cuda: Flag to specify the path to the CUDA installation.  The
    default is `/usr/local/cuda`.

    environment: Boolean flag to specify whether the environment
    (`CPATH`, `LIBRARY_PATH`, and `PATH`) should be modified to
    include NVSHMEM. The default is True.

    gdrcopy: Flag to specify the path to the GDRCOPY installation.
    The default is empty.

    ldconfig: Boolean flag to specify whether the NVSHMEM library
    directory should be added dynamic linker cache.  If False, then
    `LD_LIBRARY_PATH` is modified to include the NVSHMEM library
    directory. The default value is False.

    mpi: Flag to specify the path to the MPI installation.  The
    default is empty, i.e., do not build NVSHMEM with MPI support.

    ospackages: List of OS packages to install prior to building.  The
    default values are `make` and `wget`.

    prefix: The top level install location.  The default value is
    `/usr/local/nvshmem`.

    shmem: Flag to specify the path to the SHMEM installation.  The
    default is empty, i.e., do not build NVSHMEM with SHMEM support.

    version: The version of NVSHMEM source to download.  The default
    value is `2.9.0-2`.

    # Examples

    ```python
    nvshmem(mpi='/usr/local/nvshmem', version='2.9.0-2')
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(nvshmem, self).__init__(**kwargs)

        self.__build_examples = kwargs.pop('build_examples', False)
        self.__build_packages = kwargs.pop('build_packages', False)
        self.__cmake_opts = kwargs.pop('cmake_opts', [])
        self.__cuda = kwargs.pop('cuda', '/usr/local/cuda')
        self.__gdrcopy = kwargs.pop('gdrcopy', None)
        self.__mpi = kwargs.pop('mpi', None)
        self.__ospackages = kwargs.pop('ospackages', ['make', 'wget'])
        self.__prefix = kwargs.pop('prefix', '/usr/local/nvshmem')
        self.__shmem = kwargs.pop('shmem', None)
        self.__version = kwargs.pop('version', '2.9.0-2')
        self.__wd = kwargs.get('wd', hpccm.config.g_wd) # working directory

        # Set the download specific parameters
        self.__download()
        kwargs['url'] = self.url

        # Setup the environment variables
        self.environment_variables['CPATH'] = '{}:$CPATH'.format(
            posixpath.join(self.__prefix, 'include'))
        self.environment_variables['LIBRARY_PATH'] = '{}:$LIBRARY_PATH'.format(
            posixpath.join(self.__prefix, 'lib'))
        self.environment_variables['PATH'] = '{}:$PATH'.format(
            posixpath.join(self.__prefix, 'bin'))
        if not self.ldconfig:
            self.environment_variables['LD_LIBRARY_PATH'] = '{}:$LD_LIBRARY_PATH'.format(posixpath.join(self.__prefix, 'lib'))

        if self.__version and not self.package:
            self += comment('NVSHMEM {}'.format(self.__version))
        else:
            self += comment('NVSHMEM')
        self += packages(ospackages=self.__ospackages)

        # Set the build options
        self.__configure()

        self.__bb = generic_cmake(
            cmake_opts=self.__cmake_opts,
            comment=False,
            devel_environment=self.environment_variables,
            prefix=self.__prefix,
            runtime_environment=self.environment_variables,
            **kwargs)
        self += self.__bb

    def __configure(self):
        """Setup build options based on user parameters"""

        if self.__build_examples is False:
            self.__cmake_opts.append('-DNVSHMEM_BUILD_EXAMPLES=OFF')

        if self.__build_packages is False:
            self.__cmake_opts.append('-DNVSHMEM_BUILD_PACKAGES=OFF')
            self.__cmake_opts.append('-DNVSHMEM_BUILD_DEB_PACKAGES=OFF')
            self.__cmake_opts.append('-DNVSHMEM_BUILD_RPM_PACKAGES=OFF')

        if self.__cuda:
            self.__cmake_opts.append('-DCUDA_HOME={}'.format(self.__cuda))

        if self.__gdrcopy:
            self.__cmake_opts.append('-DGDRCOPY_HOME={}'.format(self.__gdrcopy))

        if self.__mpi:
            self.__cmake_opts.append('-DNVSHMEM_MPI_SUPPORT=1')
            self.__cmake_opts.append('-DMPI_HOME={}'.format(self.__mpi))
        #else:
        #    self.__cmake_opts.append('-DNVSHMEM_MPI_SUPPORT=0')

        if self.__shmem:
            self.__cmake_opts.append('-DNVSHMEM_SHMEM_SUPPORT=1')
            self.__cmake_opts.append('-DSHMEM_HOME={}'.format(self.__shmem))

    def __download(self):
        """Set download source based on user parameters"""

        if not self.package and not self.repository and not self.url:
            self.url = 'https://developer.download.nvidia.com/compute/redist/nvshmem/{0}/source/nvshmem_src_{1}.txz'.format(self.__version.split('-')[0], self.__version)

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples

        ```python
        n = nvshmem(...)
        Stage0 += n
        Stage1 += n.runtime()
        ```
        """
        self.rt += comment('NVSHMEM')
        self.rt += self.__bb.runtime(_from=_from)
        return str(self.rt)
