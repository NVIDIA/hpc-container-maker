# Copyright (c) 2019, NVIDIA CORPORATION.  All rights reserved.
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

"""Kokkos building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from six import string_types

from distutils.version import StrictVersion

import hpccm.config
import hpccm.templates.downloader
import hpccm.templates.envvars

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.generic_cmake import generic_cmake
from hpccm.building_blocks.packages import packages
from hpccm.common import linux_distro
from hpccm.primitives.comment import comment

class kokkos(bb_base, hpccm.templates.downloader, hpccm.templates.envvars):
    """The `kokkos` building block downloads and installs the
    [Kokkos](https://github.com/kokkos/kokkos) component.

    The [CMake](#cmake) building block should be installed prior to
    this building block.

    # Parameters

    annotate: Boolean flag to specify whether to include annotations
    (labels).  The default is False.

    arch: List of target architectures to build. If set adds
    `-DKokkos_ARCH_<value>=ON` to the list of CMake options. The
    default value is `VOLTA70`, i.e., sm_70.  If a CUDA aware build is
    not selected, then a non-default value should be used.

    branch: The git branch to clone.  Only recognized if the
    `repository` parameter is specified.  The default is empty, i.e.,
    use the default branch for the repository.

    check: Boolean flag to specify whether the build should be
    checked.  If True, adds `-DKokkos_ENABLE_TESTS=ON` to the list of
    CMake options. The default is False.

    cmake_opts: List of options to pass to `cmake`.  The default is
    `-DCMAKE_BUILD_TYPE=RELEASE`.

    commit: The git commit to clone.  Only recognized if the
    `repository` parameter is specified.  The default is empty, i.e.,
    use the latest commit on the default branch for the repository.

    cuda: Flag to control whether a CUDA aware build is performed.  If
    True, adds `-DKokkos_ENABLE_CUDA=ON` and
    `-DCMAKE_CXX_COMPILER=$(pwd)/../bin/nvcc_wrapper` to the list of
    CMake options.  The default value is True.

    environment: Boolean flag to specify whether the environment
    (`LD_LIBRARY_PATH` and `PATH`) should be modified to include
    Kokkos. The default is True.

    hwloc: Flag to control whether a hwloc aware build is performed.
    If True, adds `-DKokkos_ENABLE_HWLOC=ON` to the list of CMake
    options. The default value is True.

    ospackages: List of OS packages to install prior to building.  For
    Ubuntu, the default values are `gzip`, `libhwloc-dev`, `make`,
    `tar`, and `wget`.  For RHEL-based Linux distributions the default
    values are `gzip`, `hwloc-devel`, `make`, `tar`, and `wget`.

    prefix: The top level installation location.  The default value
    is `/usr/local/kokkos`.

    repository: The location of the git repository that should be used to build OpenMPI.  If True, then use the default `https://github.com/kokkos/kokkos.git`
    repository.  The default is empty, i.e., use the release package
    specified by `version`.

    url: The location of the tarball that should be used to build
    Kokkos.  The default is empty, i.e., use the release package
    specified by `version`.

    version: The version of Kokkos source to download.  The default
    value is `3.1.01`.

    # Examples

    ```python
    kokkos(prefix='/opt/kokkos/3.1.01', version='3.1.01')
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(kokkos, self).__init__(**kwargs)

        self.__arch = kwargs.pop('arch', ['VOLTA70'])
        self.__baseurl = kwargs.pop('baseurl',
                                    'https://github.com/kokkos/kokkos/archive')
        self.__check = kwargs.pop('check', False)
        self.__cmake_opts = kwargs.pop('cmake_opts',
                                       ['-DCMAKE_BUILD_TYPE=RELEASE'])
        self.__cuda = kwargs.pop('cuda', True)
        self.__default_repository = 'https://github.com/kokkos/kokkos.git'
        self.__hwloc = kwargs.pop('hwloc', True)
        self.__ospackages = kwargs.pop('ospackages', [])
        self.__powertools = False # enable the CentOS PowerTools repo
        self.__prefix = kwargs.pop('prefix', '/usr/local/kokkos')
        self.__version = kwargs.pop('version', '3.1.01')

        if self.repository:
            self.__directory = ''
        else:
            self.__directory = kwargs.pop('directory',
                                          'kokkos-{}'.format(self.__version))

        # Set the CMake options
        self.__cmake()

        # Set the Linux distribution specific parameters
        self.__distro()

        # Set the download specific parameters
        self.__download()
        kwargs['repository'] = self.repository
        kwargs['url'] = self.url

        # Setup the environment variables
        self.environment_variables['PATH'] = '{}/bin:$PATH'.format(
            self.__prefix)

        # Setup build configuration
        self.__bb = generic_cmake(
            annotations={'version': self.__version},
            base_annotation=self.__class__.__name__,
            cmake_opts=self.__cmake_opts,
            comment=False,
            devel_environment=self.environment_variables,
            directory=self.__directory,
            prefix=self.__prefix,
            runtime_environment=self.environment_variables,
            **kwargs)

        # Container instructions
        self += comment('Kokkos version {}'.format(self.__version))
        self += packages(ospackages=self.__ospackages,
                         powertools=self.__powertools)
        self += self.__bb

    def __cmake(self):
        """Set CMake options based on user input"""

        # Set options
        if self.__arch:
            for arch in self.__arch:
                self.__cmake_opts.append('-DKokkos_ARCH_{}=ON'.format(
                    arch.upper()))

        if self.__check:
            self.__cmake_opts.append('-DKokkos_ENABLE_TESTS=ON')

        if self.__cuda:
            self.__cmake_opts.append('-DKokkos_ENABLE_CUDA=ON')
            self.__cmake_opts.append(
                '-DCMAKE_CXX_COMPILER=$(pwd)/../bin/nvcc_wrapper')
        if self.__hwloc:
            self.__cmake_opts.append('-DKokkos_ENABLE_HWLOC=ON')

    def __distro(self):
        """Based on the Linux distribution, set values accordingly.  A user
        specified value overrides any defaults."""

        if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
            if not self.__ospackages:
                self.__ospackages = ['libhwloc-dev', 'make']

        elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
            if not self.__ospackages:
                self.__ospackages = ['hwloc-devel', 'make']

            if hpccm.config.g_linux_version >= StrictVersion('8.0'):
                # hwloc-devel is in the CentOS powertools repository
                self.__powertools = True
        else: # pragma: no cover
            raise RuntimeError('Unknown Linux distribution')

        if self.repository:
            self.__ospackages.extend(['ca-certificates', 'git'])
        else:
            self.__ospackages.extend(['gzip', 'tar', 'wget'])

    def __download(self):
        """Set download source based on user parameters"""

        # Use the default repository if set to True
        if self.repository is True:
            self.repository = self.__default_repository

        if not self.repository and not self.url:
            self.url='{0}/{1}.tar.gz'.format(self.__baseurl, self.__version)

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples

        ```python
        k = kokkos(...)
        Stage0 += k
        Stage1 += k.runtime()
        ```
        """
        instructions = []
        instructions.append(comment('Kokkos'))
        instructions.append(self.__bb.runtime(_from=_from))
        return '\n'.join(str(x) for x in instructions)
