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

"""Intel MPI building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from distutils.version import LooseVersion
import logging

import hpccm.config
import hpccm.templates.envvars
import hpccm.templates.wget

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.packages import packages
from hpccm.common import cpu_arch, linux_distro
from hpccm.primitives.comment import comment
from hpccm.primitives.environment import environment
from hpccm.primitives.shell import shell
from hpccm.toolchain import toolchain

class intel_mpi(bb_base, hpccm.templates.envvars, hpccm.templates.wget):
    """The `intel_mpi` building block downloads and installs the [Intel
    MPI Library](https://software.intel.com/en-us/intel-mpi-library).

    You must agree to the [Intel End User License Agreement](https://software.intel.com/en-us/articles/end-user-license-agreement)
    to use this building block.

    # Parameters

    environment: Boolean flag to specify whether the environment
    (`LD_LIBRARY_PATH`, `PATH`, and others) should be modified to
    include Intel MPI. `mpivars` has precedence. The default is True.

    eula: By setting this value to `True`, you agree to the [Intel End User License Agreement](https://software.intel.com/en-us/articles/end-user-license-agreement).
    The default value is `False`.

    mpivars: Intel MPI provides an environment script (`mpivars.sh`)
    to setup the Intel MPI environment.  If this value is `True`, the
    bashrc is modified to automatically source this environment
    script.  However, the Intel MPI environment is not automatically
    available to subsequent container image build steps; the
    environment is available when the container image is run.  To set
    the Intel MPI environment in subsequent build steps you can
    explicitly call `source
    /opt/intel/compilers_and_libraries/linux/mpi/intel64/bin/mpivars.sh
    intel64` in each build step.  If this value is to set `False`,
    then the environment is set such that the environment is visible
    to both subsequent container image build steps and when the
    container image is run.  However, the environment may differ
    slightly from that set by `mpivars.sh`.  The default value is
    `True`.

    ospackages: List of OS packages to install prior to installing
    Intel MPI.  For Ubuntu, the default values are
    `apt-transport-https`, `ca-certificates`, `gnupg`, `man-db`,
    `openssh-client`, and `wget`.  For RHEL-based Linux distributions,
    the default values are `man-db` and `openssh-clients`.

    version: The version of Intel MPI to install.  The default value
    is `2019.6-088`.

    # Examples

    ```python
    intel_mpi(eula=True, version='2018.3-051')
    ```
    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(intel_mpi, self).__init__(**kwargs)

        # By setting this value to True, you agree to the
        # corresponding Intel End User License Agreement
        # (https://software.intel.com/en-us/articles/end-user-license-agreement)
        self.__eula = kwargs.get('eula', False)

        self.__mpivars = kwargs.get('mpivars', True)
        self.__ospackages = kwargs.get('ospackages', [])
        self.__version = kwargs.get('version', '2019.6-088')
        self.__year = '2019' # Also used by 2018 versions

        self.__bashrc = ''      # Filled in by __distro()

        # Output toolchain
        self.toolchain = toolchain(CC='mpicc', CXX='mpicxx', F77='mpif77',
                                   F90='mpif90', FC='mpifc')

        if hpccm.config.g_cpu_arch != cpu_arch.X86_64: # pragma: no cover
            logging.warning('Using intel_mpi on a non-x86_64 processor')

        # Set the Linux distribution specific parameters
        self.__distro()

        # Fill in container instructions
        self.__instructions()

    def __instructions(self):
        """Fill in container instructions"""

        self += comment('Intel MPI version {}'.format(self.__version))

        if self.__ospackages:
            self += packages(ospackages=self.__ospackages)

        if not self.__eula:
            raise RuntimeError('Intel EULA was not accepted.  To accept, see the documentation for this building block')

        self += packages(
            apt_keys=['https://apt.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS-{}.PUB'.format(self.__year)],
            apt_repositories=['deb https://apt.repos.intel.com/mpi all main'],
            ospackages=['intel-mpi-{}'.format(self.__version)],
            yum_keys=['https://yum.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS-{}.PUB'.format(self.__year)],
            yum_repositories=['https://yum.repos.intel.com/mpi/setup/intel-mpi.repo'])

        # Set the environment
        if self.__mpivars:
            # Source the mpivars environment script when starting the
            # container, but the variables not be available for any
            # subsequent build steps.
            self += shell(commands=['echo "source /opt/intel/compilers_and_libraries/linux/mpi/intel64/bin/mpivars.sh intel64" >> {}'.format(self.__bashrc)])
        else:
            # Set the environment so that it will be available to
            # subsequent build steps and when starting the container,
            # but this may miss some things relative to the mpivars
            # environment script.
            if LooseVersion(self.__version) >= LooseVersion('2019.0'):
              self.environment_variables={
                  'FI_PROVIDER_PATH': '/opt/intel/compilers_and_libraries/linux/mpi/intel64/libfabric/lib/prov',
                  'I_MPI_ROOT': '/opt/intel/compilers_and_libraries/linux/mpi',
                  'LD_LIBRARY_PATH': '/opt/intel/compilers_and_libraries/linux/mpi/intel64/lib:/opt/intel/compilers_and_libraries/linux/mpi/intel64/libfabric/lib:$LD_LIBRARY_PATH',
                  'PATH': '/opt/intel/compilers_and_libraries/linux/mpi/intel64/bin:/opt/intel/compilers_and_libraries/linux/mpi/intel64/libfabric/bin:$PATH'}
            else:
              self.environment_variables={
                  'I_MPI_ROOT': '/opt/intel/compilers_and_libraries/linux/mpi',
                  'LD_LIBRARY_PATH': '/opt/intel/compilers_and_libraries/linux/mpi/intel64/lib:$LD_LIBRARY_PATH',
                  'PATH': '/opt/intel/compilers_and_libraries/linux/mpi/intel64/bin:$PATH'}

            self += environment(variables=self.environment_step())

    def __distro(self):
        """Based on the Linux distribution, set values accordingly.  A user
        specified value overrides any defaults."""

        if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
            if not self.__ospackages:
                self.__ospackages = ['apt-transport-https', 'ca-certificates',
                                     'gnupg', 'man-db', 'openssh-client',
                                     'wget']

            self.__bashrc = '/etc/bash.bashrc'

        elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
            if not self.__ospackages:
                self.__ospackages = ['man-db', 'openssh-clients']

            self.__bashrc = '/etc/bashrc'

        else: # pragma: no cover
            raise RuntimeError('Unknown Linux distribution')

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples

        ```python
        i = intel_mpi(...)
        Stage0 += i
        Stage1 += i.runtime()
        ```
        """
        return str(self)
