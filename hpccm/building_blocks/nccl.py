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

"""NCCL building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from distutils.version import StrictVersion
import posixpath

import hpccm.templates.downloader
import hpccm.templates.envvars
import hpccm.templates.ldconfig

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.generic_build import generic_build
from hpccm.building_blocks.packages import packages
from hpccm.common import linux_distro
from hpccm.config import get_cpu_architecture
from hpccm.primitives.comment import comment
from hpccm.primitives.copy import copy
from hpccm.primitives.environment import environment

class nccl(bb_base, hpccm.templates.downloader, hpccm.templates.envvars,
           hpccm.templates.ldconfig):
    """The `nccl` building block installs the
    [NCCL](https://developer.nvidia.com/nccl) component.

    # Parameters

    branch: The git branch to clone.  Only recognized if the
    `repository` parameter is specified.  The default is empty, i.e.,
    use the default branch for the repository.

    build: Boolean flag to specify whether NCCL should be built from
    source.  The default value is False.

    commit: The git commit to clone.  Only recognized if the
    `repository` parameter is specified.  The default is empty, i.e.,
    use the latest commit on the default branch for the repository.

    cuda: Flag to specify the CUDA version of the package to download.
    The default is `11.6`.  This option is ignored if build is True.

    environment: Boolean flag to specify whether the environment
    (`CPATH`, `LD_LIBRARY_PATH`, `LIBRARY_PATH`, and `PATH`) should be
    modified to include NCCL. The default is True.  This option is
    ignored if build is False.

    make_variables: Dictionary of environment variables and values to
    set when building NCCL.  The default is an empty dictionary.  This
    option is ignored if build is False.

    ospackages: List of OS packages to install prior to building.  The
    default values are `make` and `wget`.

    prefix: The top level install location.  The default value is
    `/usr/local/nccl`.  This option is ignored if build is False.

    repository: The location of the git repository that should be used to build NCCL.  If True, then use the default `https://github.com/NVIDIA/nccl.git`
    repository.  The default is empty, i.e., use the release package
    specified by `version`.

    version: The version of NCCL to install.  The default value is
    `2.12.10-1`.

    # Examples

    ```python
    nccl(cuda='11.0', version='2.7.6-1')
    ```

    ```python
    nccl(build=True, version='2.7.6-1')
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(nccl, self).__init__(**kwargs)

        self.__baseurl = kwargs.pop('baseurl', 'https://github.com/NVIDIA/nccl/archive')
        self.__build = kwargs.pop('build', False)
        self.__build_environment = '' # Filled in by __configure
        self.__default_repository = 'https://github.com/NVIDIA/nccl.git'
        self.__distro_label = ''     # Filled in by __distro
        self.__cuda = kwargs.pop('cuda', '11.6')
        self.__make_variables = kwargs.pop('make_variables', {})
        self.__ospackages = kwargs.pop('ospackages', [])
        self.__prefix = kwargs.pop('prefix', '/usr/local/nccl')
        self.__src_directory = kwargs.pop('src_directory', None)
        self.__version = kwargs.pop('version', '2.12.10-1')
        self.__wd = kwargs.get('wd', hpccm.config.g_wd) # working directory

        if not self.__build:
            # Install prebuild package

            # Set the Linux distribution specific parameters
            self.__distro()

            self += comment('NCCL {}'.format(self.__version))
            self += packages(ospackages=self.__ospackages)
            self += packages(
                apt=['libnccl2={0}+cuda{1}'.format(self.__version,
                                                   self.__cuda),
                     'libnccl-dev={0}+cuda{1}'.format(self.__version,
                                                      self.__cuda)],
                apt_keys=['https://developer.download.nvidia.com/compute/cuda/repos/{0}/{1}/3bf863cc.pub'.format(self.__distro_label, get_cpu_architecture())],
                apt_repositories=['deb https://developer.download.nvidia.com/compute/cuda/repos/{0}/{1} /'.format(self.__distro_label, get_cpu_architecture())],
                yum=['libnccl-{0}+cuda{1}'.format(self.__version, self.__cuda),
                     'libnccl-devel-{0}+cuda{1}'.format(self.__version,
                                                        self.__cuda)],
                yum_keys=['https://developer.download.nvidia.com/compute/cuda/repos/{0}/{1}/3bf863cc.pub'.format(self.__distro_label, get_cpu_architecture())],
                yum_repositories=['https://developer.download.nvidia.com/compute/cuda/repos/{0}/{1}'.format(self.__distro_label, get_cpu_architecture())])

        else:
            # Build from source

            # Set the build options
            self.__configure()

            self.__download()
            kwargs['repository'] = self.repository
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

            self.__bb = generic_build(
                base_annotation=self.__class__.__name__,
                build = ['{} make -j$(nproc) install'.format(
                    self.__build_environment)],
                comment=False,
                devel_environment=self.environment_variables,
                directory='nccl-{}'.format(self.__version) if not self.repository else None,
                prefix=self.__prefix,
                runtime_environment=self.environment_variables,
                **kwargs)

            self += comment('NCCL')
            self += packages(ospackages=self.__ospackages)
            self += self.__bb

    def __configure(self):
        """Setup build options based on user parameters"""

        e = {}

        e['PREFIX'] = self.__prefix

        if self.__make_variables:
          e.update(self.__make_variables)

        l = []
        if e:
            for key, val in sorted(e.items()):
                l.append('{0}={1}'.format(key, val))

        self.__build_environment = ' '.join(l)

    def __distro(self):
        """Based on the Linux distribution, set values accordingly.  A user
        specified value overrides any defaults."""

        if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
            if not self.__ospackages:
                self.__ospackages = ['apt-transport-https', 'ca-certificates',
                                     'gnupg', 'wget']

            if hpccm.config.g_linux_version >= StrictVersion('18.0'):
                self.__distro_label = 'ubuntu1804'
            else:
                self.__distro_label = 'ubuntu1604'

        elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
            if hpccm.config.g_linux_version >= StrictVersion('8.0'):
                self.__distro_label = 'rhel8'
            else:
                self.__distro_label = 'rhel7'

        else: # pragma: no cover
            raise RuntimeError('Unknown Linux distribution')

    def __download(self):
        """Set download source based on user parameters"""

        if not self.__ospackages:
            self.__ospackages = ['make', 'wget']

            if hpccm.config.g_linux_distro == linux_distro.CENTOS:
                self.__ospackages.append('which')

            if self.repository:
                self.__ospackages.append('git')

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
        n = nccl(...)
        Stage0 += n
        Stage1 += n.runtime()
        ```
        """
        self.rt += comment('NCCL')
        if self.__build:
            self.rt += copy(_from=_from, src=self.__prefix, dest=self.__prefix)
            self.rt += environment(variables=self.environment_step())
        else:
            self.rt += packages(ospackages=self.__ospackages)
            self.rt += packages(
                apt=['libnccl2={0}+cuda{1}'.format(self.__version,
                                                   self.__cuda)],
                apt_keys=['https://developer.download.nvidia.com/compute/cuda/repos/{0}/{1}/3bf863cc.pub'.format(self.__distro_label, get_cpu_architecture())],
                apt_repositories=['deb https://developer.download.nvidia.com/compute/cuda/repos/{0}/{1} /'.format(self.__distro_label, get_cpu_architecture())],
                yum=['libnccl-{0}+cuda{1}'.format(self.__version, self.__cuda)],
                yum_keys=['https://developer.download.nvidia.com/compute/cuda/repos/{0}/{1}/3bf863cc.pub'.format(self.__distro_label, get_cpu_architecture())],
                yum_repositories=['https://developer.download.nvidia.com/compute/cuda/repos/{0}/{1}'.format(self.__distro_label, get_cpu_architecture())])

        return str(self.rt)
