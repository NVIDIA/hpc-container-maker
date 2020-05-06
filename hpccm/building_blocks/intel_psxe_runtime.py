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

"""Intel Parallel Studio XE runtime building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from distutils.version import LooseVersion
import logging # pylint: disable=unused-import
import posixpath

import hpccm.config
import hpccm.templates.envvars

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.packages import packages
from hpccm.common import cpu_arch, linux_distro
from hpccm.primitives.comment import comment
from hpccm.primitives.environment import environment
from hpccm.primitives.shell import shell

class intel_psxe_runtime(bb_base, hpccm.templates.envvars):
    """The `intel_mpi` building block downloads and installs the [Intel
    Parallel Studio XE runtime](https://software.intel.com/en-us/articles/intel-parallel-studio-xe-runtime-by-version).

    You must agree to the [Intel End User License Agreement](https://software.intel.com/en-us/articles/end-user-license-agreement)
    to use this building block.

    Note: this building block does *not* install development versions
    of the Intel software tools.  Please see the
    [intel_psxe](#intel_psxe), [intel_mpi](#intel_mpi), or [mkl](#mkl)
    building blocks for development environments.

    # Parameters

    daal: Boolean flag to specify whether the Intel Data Analytics
    Acceleration Library runtime should be installed.  The default is
    True.

    environment: Boolean flag to specify whether the environment
    (`LD_LIBRARY_PATH`, `PATH`, and others) should be modified to
    include Intel Parallel Studio XE runtime. `psxevars` has
    precedence. The default is True.

    eula: By setting this value to `True`, you agree to the [Intel End User License Agreement](https://software.intel.com/en-us/articles/end-user-license-agreement).
    The default value is `False`.

    icc: Boolean flag to specify whether the Intel C++ Compiler
    runtime should be installed.  The default is True.

    ifort: Boolean flag to specify whether the Intel Fortran Compiler
    runtime should be installed.  The default is True.

    ipp: Boolean flag to specify whether the Intel Integrated
    Performance Primitives runtime should be installed.  The default
    is True.

    mkl: Boolean flag to specify whether the Intel Math Kernel Library
    runtime should be installed.  The default is True.

    mpi: Boolean flag to specify whether the Intel MPI Library runtime
    should be installed.  The default is True.

    psxevars: Intel Parallel Studio XE provides an environment script
    (`psxevars.sh`) to setup the environment.  If this value is
    `True`, the bashrc is modified to automatically source this
    environment script.  However, the Intel runtime environment is not
    automatically available to subsequent container image build steps;
    the environment is available when the container image is run.  To
    set the Intel Parallel Studio XE runtime environment in subsequent
    build steps you can explicitly call `source
    /opt/intel/psxe_runtime/linux/bin/psxevars.sh intel64` in each
    build step.  If this value is to set `False`, then the environment
    is set such that the environment is visible to both subsequent
    container image build steps and when the container image is run.
    However, the environment may differ slightly from that set by
    `psxevars.sh`.  The default value is `True`.

    ospackages: List of OS packages to install prior to installing
    Intel MPI.  For Ubuntu, the default values are
    `apt-transport-https`, `ca-certificates`, `gcc`, `gnupg`,
    `man-db`, `openssh-client`, and `wget`.  For RHEL-based Linux
    distributions, the default values are `man-db`, `openssh-clients`,
    and `which`.

    tbb: Boolean flag to specify whether the Intel Threading Building
    Blocks runtime should be installed.  The default is True.

    version: The version of the Intel Parallel Studio XE runtime to
    install.  The default value is `2020.1-12`.

    # Examples

    ```python
    intel_psxe_runtime(eula=True, version='2018.5-281')
    ```

    ```python
    intel_psxe_runtime(daal=False, eula=True, ipp=False, psxevars=False)
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(intel_psxe_runtime, self).__init__(**kwargs)

        # By setting this value to True, you agree to the
        # corresponding Intel End User License Agreement
        # (https://software.intel.com/en-us/articles/end-user-license-agreement)
        self.__eula = kwargs.get('eula', False)

        self.__daal = kwargs.get('daal', True)
        self.__icc = kwargs.get('icc', True)
        self.__ifort = kwargs.get('ifort', True)
        self.__ipp = kwargs.get('ipp', True)
        self.__mkl = kwargs.get('mkl', True)
        self.__mpi = kwargs.get('mpi', True)
        self.__psxevars = kwargs.get('psxevars', True)
        self.__ospackages = kwargs.get('ospackages', [])
        self.__tbb = kwargs.get('tbb', True)
        self.__version = kwargs.get('version', '2020.1-12')
        self.__year = self.__version.split('.')[0]

        self.__bashrc = ''            # Filled in by __distro()
        self.__apt = []               # Filled in by __setup()
        self.__yum = []               # Filled in by __setup()

        if hpccm.config.g_cpu_arch != cpu_arch.X86_64: # pragma: no cover
            logging.warning('Using intel_psxe_runtime on a non-x86_64 processor')

        # Set the Linux distribution specific parameters
        self.__distro()

        # Construct the list of runtime packages to install
        self.__setup()

        # Fill in container instructions
        self.__instructions()

    def __instructions(self):
        """Fill in container instructions"""

        self += comment('Intel Parallel Studio XE runtime version {}'.format(self.__version))

        if self.__ospackages:
            self += packages(ospackages=self.__ospackages)

        if not self.__eula:
            raise RuntimeError('Intel EULA was not accepted.  To accept, see the documentation for this building block')

        if int(self.__year) >= 2019:
            apt_repositories = ['deb https://apt.repos.intel.com/{0} intel-psxe-runtime main'.format(self.__year)]
        else:
            # The APT keys expired and had to be reissued.  They were only
            # reissued for 2019 and later.  Blindly (and insecurely!) trust
            # the 2018 and earlier repositories.
            apt_repositories = ['deb [trusted=yes] https://apt.repos.intel.com/{0} intel-psxe-runtime main'.format(self.__year)]

        self += packages(
            apt=self.__apt,
            apt_keys = ['https://apt.repos.intel.com/{0}/GPG-PUB-KEY-INTEL-PSXE-RUNTIME-{0}'.format(self.__year)],
            apt_repositories=apt_repositories,
            aptitude=True,
            yum=self.__yum,
            yum_keys=['https://yum.repos.intel.com/{0}/setup/RPM-GPG-KEY-intel-psxe-runtime-{0}'.format(self.__year)],
            yum_repositories=['https://yum.repos.intel.com/{0}/setup/intel-psxe-runtime-{0}.repo'.format(self.__year)],
            yum4=True)

        # Set the environment
        if self.__psxevars:
            # Source the psxevars environment script when starting the
            # container, but the variables not be available for any
            # subsequent build steps.
            self += shell(commands=['echo "source /opt/intel/psxe_runtime/linux/bin/psxevars.sh intel64" >> {}'.format(self.__bashrc)])
        else:
            # Set the environment so that it will be available to
            # subsequent build steps and when starting the container,
            # but this may miss some things relative to the psxevars
            # environment script.
            self += environment(variables=self.environment_step())

    def __distro(self):
        """Based on the Linux distribution, set values accordingly.  A user
        specified value overrides any defaults."""

        if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
            if not self.__ospackages:
                self.__ospackages = ['apt-transport-https', 'ca-certificates',
                                     'gcc', 'gnupg', 'man-db',
                                     'openssh-client', 'wget']

            self.__bashrc = '/etc/bash.bashrc'

        elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
            if not self.__ospackages:
                self.__ospackages = ['man-db', 'openssh-clients', 'which']

            self.__bashrc = '/etc/bashrc'

        else: # pragma: no cover
            raise RuntimeError('Unknown Linux distribution')

    def __environment(self):
        """Manually set the environment as an alternative to psxevars.sh"""

        basepath = '/opt/intel/psxe_runtime/linux'

        ld_library_path = []
        path = []
        env = {}

        if self.__daal:
            env['DAALROOT'] = posixpath.join(basepath, 'daal')
            ld_library_path.append(posixpath.join(basepath, 'daal', 'lib',
                                                  'intel64'))

        if self.__icc:
            ld_library_path.append(posixpath.join(basepath, 'compiler', 'lib',
                                                  'intel64_lin'))

        if self.__ifort:
            ld_library_path.append(posixpath.join(basepath, 'compiler', 'lib',
                                                  'intel64_lin'))

        if self.__ipp:
            env['IPPROOT' ] = posixpath.join(basepath, 'ipp')
            ld_library_path.append(posixpath.join(basepath, 'ipp', 'lib',
                                                  'intel64'))

        if self.__mkl:
            env['MKLROOT'] = posixpath.join(basepath, 'mkl')
            ld_library_path.append(posixpath.join(basepath, 'mkl', 'lib',
                                                  'intel64'))

        if self.__mpi:
            env['I_MPI_ROOT'] = posixpath.join(basepath, 'mpi')
            ld_library_path.append(posixpath.join(basepath, 'mpi', 'intel64',
                                                  'lib'))
            path.append(posixpath.join(basepath, 'mpi', 'intel64', 'bin'))

            if LooseVersion(self.__version) >= LooseVersion('2019'):
                env['FI_PROVIDER_PATH'] = posixpath.join(
                    basepath, 'mpi', 'intel64', 'libfabric', 'lib', 'prov')
                ld_library_path.append(posixpath.join(
                    basepath, 'mpi', 'intel64', 'libfabric', 'lib'))
                path.append(posixpath.join(basepath, 'mpi', 'intel64',
                                           'libfabric', 'bin'))

            if LooseVersion(self.__version) >= LooseVersion('2020'):
                ld_library_path.append(posixpath.join(
                    basepath, 'mpi', 'intel64', 'lib', 'release'))

        if self.__tbb:
            if int(self.__year) >= 2020:
                ld_library_path.append(posixpath.join(basepath, 'tbb', 'lib',
                                                      'intel64', 'gcc4.8'))
            else:
                ld_library_path.append(posixpath.join(basepath, 'tbb', 'lib',
                                                      'intel64', 'gcc4.7'))

        if ld_library_path:
            ld_library_path.append('$LD_LIBRARY_PATH')
            env['LD_LIBRARY_PATH'] = ':'.join(ld_library_path)

        if path:
            path.append('$PATH')
            env['PATH'] = ':'.join(path)

        return env

    def __setup(self):
        """Construct the list of packages, i.e., fill in
           self.__apt and self.__yum"""

        if (self.__daal and self.__icc and self.__ifort and self.__ipp
            and self.__mkl and self.__mpi and self.__tbb):
            # Everything selected, so install the omnibus runtime package
            self.__apt = ['intel-psxe-runtime={}'.format(self.__version)]
            self.__yum = ['intel-psxe-runtime-{}'.format(self.__version)]
        else:
            if self.__daal:
                self.__apt.append(
                    'intel-daal-runtime={}'.format(self.__version))
                self.__yum.append(
                    'intel-daal-runtime-64bit-{}'.format(self.__version))
            if self.__icc:
                self.__apt.append(
                    'intel-icc-runtime={}'.format(self.__version))
                self.__yum.append(
                    'intel-icc-runtime-64bit-{}'.format(self.__version))
            if self.__ifort:
                self.__apt.append(
                    'intel-ifort-runtime={}'.format(self.__version))
                self.__yum.append(
                    'intel-ifort-runtime-64bit-{}'.format(self.__version))
            if self.__ipp:
                self.__apt.append(
                    'intel-ipp-runtime={}'.format(self.__version))
                self.__yum.append(
                    'intel-ipp-runtime-64bit-{}'.format(self.__version))
            if self.__mkl:
                self.__apt.append(
                    'intel-mkl-runtime={}'.format(self.__version))
                self.__yum.append(
                    'intel-mkl-runtime-64bit-{}'.format(self.__version))
            if self.__mpi:
                self.__apt.append(
                    'intel-mpi-runtime={}'.format(self.__version))
                self.__yum.append(
                    'intel-mpi-runtime-64bit-{}'.format(self.__version))
            if self.__tbb:
                self.__apt.append(
                    'intel-tbb-runtime={}'.format(self.__version))
                self.__yum.append(
                    'intel-tbb-runtime-64bit-{}'.format(self.__version))

        # Set the environment
        self.environment_variables = self.__environment()

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples

        ```python
        i = intel_psxe_runtime(...)
        Stage0 += i
        Stage1 += i.runtime()
        ```
        """
        return str(self)
