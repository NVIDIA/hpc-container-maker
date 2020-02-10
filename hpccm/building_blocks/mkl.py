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

"""MKL building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import

import hpccm.config
import hpccm.templates.envvars
import hpccm.templates.wget

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.packages import packages
from hpccm.common import cpu_arch, linux_distro
from hpccm.primitives.comment import comment
from hpccm.primitives.environment import environment
from hpccm.primitives.shell import shell

class mkl(bb_base, hpccm.templates.envvars, hpccm.templates.wget):
    """The `mkl` building block downloads and installs the [Intel Math
    Kernel Library](http://software.intel.com/mkl).

    You must agree to the [Intel End User License Agreement](https://software.intel.com/en-us/articles/end-user-license-agreement)
    to use this building block.

    # Parameters

    environment: Boolean flag to specify whether the environment
    (`LD_LIBRARY_PATH`, `PATH`, and other variables) should be
    modified to include MKL. The default is True.

    eula: By setting this value to `True`, you agree to the [Intel End User License Agreement](https://software.intel.com/en-us/articles/end-user-license-agreement).
    The default value is `False`.

    mklvars: MKL provides an environment script (`mklvars.sh`) to
    setup the MKL environment.  If this value is `True`, the bashrc is
    modified to automatically source this environment script.
    However, the MKL environment is not automatically available to
    subsequent container image build steps; the environment is
    available when the container image is run.  To set the MKL
    environment in subsequent build steps you can explicitly call
    `source /opt/intel/mkl/bin/mklvars.sh intel64` in each build step.
    If this value is to set `False`, then the environment is set such
    that the environment is visible to both subsequent container image
    build steps and when the container image is run.  However, the
    environment may differ slightly from that set by `mklvars.sh`.
    The default value is `True`.

    ospackages: List of OS packages to install prior to installing
    MKL.  For Ubuntu, the default values are `apt-transport-https`,
    `ca-certificates`, `gnupg`, and `wget`.  For RHEL-based Linux
    distributions, the default is an empty list.

    version: The version of MKL to install.  The default value is
    `2020.0-088`.

    # Examples

    ```python
    mkl(eula=True, version='2018.3-051')
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(mkl, self).__init__(**kwargs)

        # By setting this value to True, you agree to the
        # corresponding Intel End User License Agreement
        # (https://software.intel.com/en-us/articles/end-user-license-agreement)
        self.__eula = kwargs.get('eula', False)

        self.__mklvars = kwargs.get('mklvars', True)
        self.__ospackages = kwargs.get('ospackages', [])
        self.__version = kwargs.get('version', '2020.0-088')
        self.__year = '2019' # Also used by 2018 and 2020 versions

        self.__bashrc = ''      # Filled in by __distro()

        if hpccm.config.g_cpu_arch != cpu_arch.X86_64: # pragma: no cover
            logging.warning('Using mkl on a non-x86_64 processor')

        # Set the Linux distribution specific parameters
        self.__distro()

        # Fill in container instructions
        self.__instructions()

    def __instructions(self):
        """Fill in container instructions"""

        self += comment('MKL version {}'.format(self.__version))

        if self.__ospackages:
            self += packages(ospackages=self.__ospackages)

        if not self.__eula:
            raise RuntimeError('Intel EULA was not accepted.  To accept, see the documentation for this building block')

        self += packages(
            apt_keys=['https://apt.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS-{}.PUB'.format(self.__year)],
            apt_repositories=['deb https://apt.repos.intel.com/mkl all main'],
            ospackages=['intel-mkl-64bit-{}'.format(self.__version)],
            yum_keys=['https://yum.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS-{}.PUB'.format(self.__year)],
            yum_repositories=['https://yum.repos.intel.com/mkl/setup/intel-mkl.repo'])

        # Set the environment
        if self.__mklvars:
            # Source the mklvars environment script when starting the
            # container, but the variables not be available for any
            # subsequent build steps.
            self += shell(commands=['echo "source /opt/intel/mkl/bin/mklvars.sh intel64" >> {}'.format(self.__bashrc)])
        else:
            # Set the environment so that it will be available to
            # subsequent build steps and when starting the container,
            # but this may miss some things relative to the mklvars
            # environment script.
            self.environment_variables={
                'CPATH': '/opt/intel/mkl/include:$CPATH',
                'LD_LIBRARY_PATH': '/opt/intel/mkl/lib/intel64:/opt/intel/lib/intel64:$LD_LIBRARY_PATH',
                'LIBRARY_PATH': '/opt/intel/mkl/lib/intel64:/opt/intel/lib/intel64:$LIBRARY_PATH',
                'MKLROOT': '/opt/intel/mkl'}
            self += environment(variables=self.environment_step())

    def __distro(self):
        """Based on the Linux distribution, set values accordingly.  A user
        specified value overrides any defaults."""

        if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
            if not self.__ospackages:
                self.__ospackages = ['apt-transport-https', 'ca-certificates',
                                     'gnupg', 'wget']

            self.__bashrc = '/etc/bash.bashrc'

        elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
            if not self.__ospackages:
                self.__ospackages = []

            self.__bashrc = '/etc/bashrc'

        else: # pragma: no cover
            raise RuntimeError('Unknown Linux distribution')

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples

        ```python
        m = mkl(...)
        Stage0 += m
        Stage1 += m.runtime()
        ```
        """
        return str(self)
