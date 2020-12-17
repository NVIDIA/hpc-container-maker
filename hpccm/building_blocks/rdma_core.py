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

"""rdma-core building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from six import string_types

from distutils.version import StrictVersion
import posixpath

import hpccm.config
import hpccm.templates.downloader
import hpccm.templates.envvars
import hpccm.templates.ldconfig

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.generic_cmake import generic_cmake
from hpccm.building_blocks.packages import packages
from hpccm.common import cpu_arch
from hpccm.common import linux_distro
from hpccm.primitives.comment import comment
from hpccm.toolchain import toolchain

class rdma_core(bb_base, hpccm.templates.downloader, hpccm.templates.envvars,
                hpccm.templates.ldconfig):
    """The `rdma_core` building block configures, builds, and installs the
    [RDMA Core](https://github.com/linux-rdma/rdma-core) component.

    The [CMake](#cmake) building block should be installed prior to
    this building block.

    # Parameters

    annotate: Boolean flag to specify whether to include annotations
    (labels).  The default is False.

    branch: The git branch to clone.  Only recognized if the
    `repository` parameter is specified.  The default is empty, i.e.,
    use the default branch for the repository.

    commit: The git commit to clone.  Only recognized if the
    `repository` parameter is specified.  The default is empty, i.e.,
    use the latest commit on the default branch for the repository.

    environment: Boolean flag to specify whether the environment
    (`CPATH`, `LD_LIBRARY_PATH`, `LIBRARY_PATH`, and `PATH`) should be
    modified to include RDMA Core. The default is True.

    ldconfig: Boolean flag to specify whether the RDMA Core library
    directory should be added dynamic linker cache.  If False, then
    `LD_LIBRARY_PATH` is modified to include the RDMA Core library
    directory. The default value is False.

    ospackages: List of OS packages to install prior to configuring
    and building.  For Ubuntu, the default values are `libudev-dev`,
    `libnl-3-dev`, `libnl-route-3-dev`, `make`, `pkg-config`,
    `python3-docutils`, `pandoc`, and `wget`.  For RHEL-based Linux
    distributions, the default values are `libnl3-devel`,
    `libudev-devel`, `make`, `pkgconfig`, `pandoc`, `python-docutils`,
    and `wget`.  If the `repository` parameter is set, then
    `ca-certificates` and `git` are also included.

    prefix: The top level install location.  The default value is
    `/usr/local/rdma-core`.

    repository: The location of the git repository that should be used to build RDMA Core.  If True, then use the default `https://github.com/linux-rdma/rdma-core.git`
    repository.  The default is empty, i.e., use the release package
    specified by `version`.

    toolchain: The toolchain object.  This should be used if
    non-default compilers or other toolchain options are needed.  The
    default value is empty.

    url: The location of the tarball that should be used to build RDMA
    Core.  The default is empty, i.e., use the release package
    specified by `version`.

    version: The version of RDMA Core source to download.  The default
    value is `31.2`.

    # Examples

    ```python
    rdma_core(prefix='/opt/rdma-core/31.2', version='31.2')
    ```

    ```python
    rdma_core(repository='https://github.com/linux-rdma/rdma-core.git')
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(rdma_core, self).__init__(**kwargs)

        # Parameters
        self.__baseurl = kwargs.pop('baseurl', 'https://github.com/linux-rdma/rdma-core/archive')
        self.__default_repository = 'https://github.com/linux-rdma/rdma-core.git'
        self.__ospackages = kwargs.pop('ospackages', [])
        self.__prefix = kwargs.pop('prefix', '/usr/local/rdma-core')
        self.__runtime_ospackages = [] # Filled in by __distro()
        self.__toolchain = kwargs.pop('toolchain', toolchain())
        self.__version = kwargs.pop('version', '31.2')

        # Set the Linux distribution specific parameters
        self.__distro()

        # Set the download specific parameters
        self.__download()
        kwargs['repository'] = self.repository
        kwargs['url'] = self.url

        # Setup the environment variables
        self.environment_variables['CPATH'] = '{}:$CPATH'.format(
            posixpath.join(self.__prefix, 'include'))
        self.environment_variables['LIBRARY_PATH'] = '{0}:{1}:$LIBRARY_PATH'.format(
            posixpath.join(self.__prefix, 'lib'),
            posixpath.join(self.__prefix, 'lib64'))
        self.environment_variables['PATH'] = '{}:$PATH'.format(
            posixpath.join(self.__prefix, 'bin'))
        if not self.ldconfig:
            self.environment_variables['LD_LIBRARY_PATH'] = '{0}:{1}:$LD_LIBRARY_PATH'.format(
                posixpath.join(self.__prefix, 'lib'),
                posixpath.join(self.__prefix, 'lib64'))

        # Setup build configuration
        self.__bb = generic_cmake(
            annotations={'version': self.__version} if not self.repository else {},
            base_annotation=self.__class__.__name__,
            comment=False,
            devel_environment=self.environment_variables,
            directory='rdma-core-{}'.format(self.__version) if self.url else None,
            prefix=self.__prefix,
            runtime_environment=self.environment_variables,
            toolchain=self.__toolchain,
            **kwargs)

        # Container instructions
        if self.repository:
            if self.branch:
                self += comment('RDMA Core {} {}'.format(self.repository,
                                                         self.branch))
            elif self.commit:
                self += comment('RDMA Core {} {}'.format(self.repository,
                                                         self.commit))
            else:
                self += comment('RDMA Core {}'.format(self.repository))
        else:
            self += comment('RDMA Core version {}'.format(self.__version))
        # pandoc is in EPEL on CentOS 7 and PowerTools on CentOS 8
        self += packages(epel=True, ospackages=self.__ospackages,
                         powertools=True)
        self += self.__bb

    def __distro(self):
        """Based on the Linux distribution, set values accordingly.  A user
        specified value overrides any defaults."""

        if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
            if not self.__ospackages:
                self.__ospackages = ['libudev-dev', 'libnl-3-dev',
                                     'libnl-route-3-dev', 'make',
                                     'pkg-config', 'python3-docutils',
                                     'pandoc', 'wget']

            self.__runtime_ospackages = ['libnl-3-200', 'libnl-route-3-200',
                                         'libnuma1']
        elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
            if not self.__ospackages:
                self.__ospackages = ['libnl3-devel', 'libudev-devel', 'make',
                                     'pkgconfig', 'pandoc', 'wget']

                if hpccm.config.g_linux_version >= StrictVersion('8.0'):
                    self.__ospackages.append('python3-docutils')
                else:
                    self.__ospackages.append('python-docutils')

            self.__runtime_ospackages = ['libnl', 'libnl3', 'numactl-libs']
        else: # pragma: no cover
            raise RuntimeError('Unknown Linux distribution')

        if self.repository:
            self.__ospackages.extend(['ca-certificates', 'git'])

    def __download(self):
        """Set download source based on user parameters"""

        # Use the default repository if set to True
        if self.repository is True:
            self.repository = self.__default_repository

        if not self.repository and not self.url:
            self.url = '{0}/v{1}.tar.gz'.format(self.__baseurl, self.__version)

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples

        ```python
        r = rdma_core(...)
        Stage0 += r
        Stage1 += r.runtime()
        ```
        """
        self.rt += comment('RDMA Core')
        self.rt += packages(ospackages=self.__runtime_ospackages)
        self.rt += self.__bb.runtime(_from=_from)
        return str(self.rt)
