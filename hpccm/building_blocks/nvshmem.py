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


import os
import posixpath

from packaging.version import Version

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

    Args:
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
        mpi: Flag to enable MPI support.  If True, enables MPI and relies
            on CMake's FindMPI to locate the installation.  If a string, uses
            the value as the MPI installation path (MPI_HOME).  If False,
            MPI support is explicitly disabled.  The default is True, matching
            the upstream NVSHMEM CMake default.
        ospackages: List of OS packages to install prior to building.  The
            default values are `make` and `wget`.
        prefix: The top level install location.  The default value is
            `/usr/local/nvshmem`.
        shmem: Flag to specify the path to the SHMEM installation.  The
            default is empty, i.e., do not build NVSHMEM with SHMEM support.
        version: The version of NVSHMEM source to download.  The default
            value is `3.7.2-0`.

    Examples:
        ```python
        nvshmem(mpi='/usr/local/nvshmem', version='3.7.2-0')
        ```

    """

    def __init__(self, **kwargs):

        super(nvshmem, self).__init__(**kwargs)
        # First NVSHMEM version published as a GitHub release tarball
        self.__github_min_version = Version('3.4.5')

        self.__build_examples = kwargs.pop('build_examples', False)
        self.__build_packages = kwargs.pop('build_packages', False)
        self.__cmake_opts = kwargs.pop('cmake_opts', [])
        self.__cuda = kwargs.pop('cuda', '/usr/local/cuda')
        self.__gdrcopy = kwargs.pop('gdrcopy', None)
        self.__mpi = kwargs.pop('mpi', True)
        self.__ospackages = kwargs.pop('ospackages', ['make', 'wget'])
        self.__prefix = kwargs.pop('prefix', '/usr/local/nvshmem')
        self.__shmem = kwargs.pop('shmem', None)
        self.__version = kwargs.pop('version', '3.7.2-0')
        self.__wd = kwargs.get('wd', hpccm.config.g_wd) # working directory

        # Set the download specific parameters
        self.__download()
        kwargs['url'] = self.url

        # GitHub release tarballs use paths like .../v3.6.5-0.tar.gz; tar strips the
        # extension but the top-level directory is nvshmem-3.6.5-0, not v3.6.5-0.
        if (kwargs.get('directory') is None and self.url
                and 'github.com/NVIDIA/nvshmem' in self.url):
            kwargs['directory'] = 'nvshmem-{0}'.format(self.__version)

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

        # NVSHMEM's CMake configure step (find_package(CUDAToolkit) and
        # several find_library calls) needs to be able to dlopen CUDA
        # runtime libraries, so prepend cuda/lib64 to LD_LIBRARY_PATH for
        # the build environment whenever a CUDA installation is known.
        if self.__cuda:
            be = kwargs.get('build_environment', {})
            cuda_lib = posixpath.join(self.__cuda, 'lib64')
            existing = be.get('LD_LIBRARY_PATH', '')
            if cuda_lib not in existing:
                be['LD_LIBRARY_PATH'] = '{}:{}'.format(cuda_lib, existing).rstrip(':')
            kwargs['build_environment'] = be

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
            self.__cmake_opts.append('-DNVSHMEM_BUILD_DEB_PACKAGE=OFF')
            self.__cmake_opts.append('-DNVSHMEM_BUILD_RPM_PACKAGE=OFF')

        if self.__cuda:
            self.__cmake_opts.append('-DCUDA_HOME={}'.format(self.__cuda))

        if self.__gdrcopy:
            self.__cmake_opts.append('-DGDRCOPY_HOME={}'.format(self.__gdrcopy))

        if self.__mpi:
            self.__cmake_opts.append('-DNVSHMEM_MPI_SUPPORT=ON')
            if isinstance(self.__mpi, str):
                self.__cmake_opts.append('-DMPI_HOME={}'.format(self.__mpi))
        else:
            # NVSHMEM 3.4.5+ defaults NVSHMEM_MPI_SUPPORT to ON, so an
            # explicit OFF is required when the user did not request MPI.
            self.__cmake_opts.append('-DNVSHMEM_MPI_SUPPORT=OFF')

        if self.__shmem:
            self.__cmake_opts.append('-DNVSHMEM_SHMEM_SUPPORT=1')
            self.__cmake_opts.append('-DSHMEM_HOME={}'.format(self.__shmem))

    def __download(self):
        """Set download source based on user parameters"""

        if not self.package and not self.repository and not self.url:
            v = Version(self.__version.split('-')[0])
            if v >= self.__github_min_version:
                tag = self.__version if self.__version.startswith('v') else 'v{}'.format(self.__version)
                self.url = 'https://github.com/NVIDIA/nvshmem/archive/refs/tags/{}.tar.gz'.format(tag)
            else:
                self.url = 'https://developer.download.nvidia.com/compute/redist/nvshmem/{0}/source/nvshmem_src_{1}.txz'.format(self.__version.split('-')[0], self.__version)

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        Examples:
            ```python
            n = nvshmem(...)
            Stage0 += n
            Stage1 += n.runtime()
            ```
        """
        self.rt += comment('NVSHMEM')
        self.rt += self.__bb.runtime(_from=_from)
        return str(self.rt)
