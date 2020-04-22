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

"""Arm Allinea Studio building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from distutils.version import StrictVersion
import logging
import posixpath
import re

import hpccm.config
import hpccm.templates.envvars
import hpccm.templates.rm
import hpccm.templates.tar
import hpccm.templates.wget

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.packages import packages
from hpccm.common import cpu_arch, linux_distro
from hpccm.primitives.comment import comment
from hpccm.primitives.copy import copy
from hpccm.primitives.environment import environment
from hpccm.primitives.shell import shell
from hpccm.toolchain import toolchain

class arm_allinea_studio(bb_base, hpccm.templates.envvars, hpccm.templates.rm,
                         hpccm.templates.tar, hpccm.templates.wget):
    """The `arm_allinea_studio` building block downloads and installs the
    [Arm Allinea
    Studio](https://developer.arm.com/tools-and-software/server-and-hpc/arm-architecture-tools/arm-allinea-studio).

    You must agree to the [Arm End User License Agreement](https://developer.arm.com/tools-and-software/server-and-hpc/arm-architecture-tools/arm-allinea-studio/licensing/eula)
    to use this building block.

    As a side effect, a toolchain is created containing the Arm
    Allinea Studio compilers.  The toolchain can be passed to other
    operations that want to build using the Arm Allinea Studio
    compilers.  However, the environment is not automatically
    configured for the Arm Allinea Studio compilers.  The desired
    environment module must be manually loaded, e.g., `module load
    Generic-AArch64/RHEL/7/arm-linux-compiler/20.0`.

    # Parameters

    environment: Boolean flag to specify whether the environment
    (`MODULEPATH`) should be modified to include Arm Allinea
    Studio. The default is True.

    eula: By setting this value to `True`, you agree to the [Arm End User License Agreement](https://developer.arm.com/tools-and-software/server-and-hpc/arm-architecture-tools/arm-allinea-studio/licensing/eula).
    The default value is `False`.

    microarchitectures: List of microarchitectures to install.
    Available values are `generic`, `generic-sve`, `neoverse-n1`, and
    `thunderx2t99`.  Irrespective of this setting, the generic
    implementation will always be installed.  The default is
    `generic`.

    ospackages: List of OS packages to install prior to installing Arm
    Allinea Studio.  For Ubuntu, the default values are `libc6-dev`,
    `lmod`, `python`, `tar`, `tcl`, and `wget`.  For RHEL-based Linux
    distributions, the default values are `glibc-devel`, `Lmod`,
    `tar`, and `wget`.

    prefix: The top level install prefix.  The default value is
    `/opt/arm`.

    tarball: Path to the Arm Allinea Studio tarball relative to the
    local build context.  The default value is empty.  If this is
    defined, the tarball in the local build context will be used
    rather than downloading the tarball from the web.

    version: The version of Arm Allinea Studio to install.  The
    default value is `20.0`.  Due to differences in the packaging
    scheme, versions prior to 20.0 are not supported.

    # Examples

    ```python
    arm_allinea_studio(eula=True,
                       microarchitectures=['generic', 'thunderx2t99'],
                       version='20.0')
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(arm_allinea_studio, self).__init__(**kwargs)

        self.__baseurl = kwargs.get('baseurl',
                                    'https://developer.arm.com/-/media/Files/downloads/hpc/arm-allinea-studio')
        self.__commands = [] # Filled in by __setup()
        self.__directory_string = '' # Filled in by __distro()

        # By setting this value to True, you agree to the
        # corresponding Arm Allinea Studio End User License Agreement
        # https://developer.arm.com/tools-and-software/server-and-hpc/arm-architecture-tools/arm-allinea-studio/licensing/eula
        self.__eula = kwargs.get('eula', False)

        self.__gcc_version = kwargs.get('gcc_version', '9.2.0')
        self.__installer_template = '' # Filled in by __distro()
        self.__microarchitectures = kwargs.get('microarchitectures',
                                               ['generic'])
        self.__ospackages = kwargs.get('ospackages', [])
        self.__package_string = '' # Filled in by __distro()
        self.__prefix = kwargs.get('prefix', '/opt/arm')
        self.__tarball = kwargs.get('tarball', None)
        self.__version = kwargs.get('version', '20.0')
        self.__wd = '/var/tmp' # working directory

        self.toolchain = toolchain(CC='armclang', CXX='armclang++',
                                   F77='armflang', F90='armflang',
                                   FC='armflang')

        if hpccm.config.g_cpu_arch != cpu_arch.AARCH64: # pragma: no cover
            logging.warning('Using arm_allinea_studio on a non-aarch64 processor')

        if not self.__eula:
            raise RuntimeError('Arm Allinea Studio EULA was not accepted.  To accept, see the documentation for this building block')

        # Set the Linux distribution specific parameters
        self.__distro()

        # Construct the series of steps to execute
        self.__setup()

        # Fill in container instructions
        self.__instructions()

    def __instructions(self):
        """Fill in container instructions"""

        self += comment('Arm Allinea Studio version {}'.format(self.__version))

        if self.__ospackages:
            # EPEL necessary for Lmod
            self += packages(epel=True, ospackages=self.__ospackages)

        if self.__tarball:
            self += copy(src=self.__tarball, dest=self.__wd)

        self += shell(commands=self.__commands)
        self += environment(variables=self.environment_step())

    def __distro(self):
        """Based on the Linux distribution, set values accordingly.  A user
        specified value overrides any defaults."""

        if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
            self.__directory_string = 'Ubuntu-16.04'
            self.__package_string = 'Ubuntu_16.04'
            self.__url_string = 'Ubuntu16.04'

            self.__installer_template = 'arm-compiler-for-linux-{{}}_Generic-AArch64_{0}_aarch64-linux-deb.sh'.format(self.__directory_string)

            if not self.__ospackages:
                self.__ospackages = ['libc6-dev', 'lmod', 'python', 'tar',
                                     'tcl', 'wget']

        elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
            if hpccm.config.g_linux_version >= StrictVersion('8.0'):
                self.__directory_string = 'RHEL-8'
                self.__package_string = 'RHEL_8'
                self.__url_string = 'RHEL8'
            else:
                self.__directory_string = 'RHEL-7'
                self.__package_string = 'RHEL_7'
                self.__url_string = 'RHEL7'

            self.__installer_template = 'arm-compiler-for-linux-{{}}_Generic-AArch64_{}_aarch64-linux-rpm.sh'.format(self.__directory_string)

            if not self.__ospackages:
                self.__ospackages = ['Lmod', 'glibc-devel', 'tar', 'wget']

        else: # pragma: no cover
            raise RuntimeError('Unknown Linux distribution')

    def __setup(self):
        """Construct the series of shell commands, i.e., fill in
           self.__commands"""

        # Use a tarball.  Figure out the version from the tarball name.
        if self.__tarball:
            tarball = posixpath.basename(self.__tarball)

            # Figure out the version from the tarball name
            match = re.match(r'Arm-Compiler-for-Linux_(?P<year>\d\d)\.0?(?P<month>[0-9][0-9]?)',
                             tarball)
            if match and match.groupdict()['year'] and match.groupdict()['month']:
                self.__version = '{0}.{1}'.format(match.groupdict()['year'],
                                                  match.groupdict()['month'])
        else:
            # The download URL has the format MAJOR-MINOR in the path
            # and the tarball contains MAJOR.MINOR, so pull apart the
            # full version to get the individual components.
            match = re.match(r'(?P<major>\d+)\.(?P<minor>\d+)', self.__version)
            major_minor = '{0}-{1}'.format(match.groupdict()['major'],
                                           match.groupdict()['minor'])

            tarball = 'Arm-Compiler-for-Linux_{0}_{1}_aarch64.tar'.format(
                self.__version, self.__package_string)
            url = '{0}/{1}/{2}/{3}'.format(self.__baseurl, major_minor,
                                           self.__url_string, tarball)

            # Download source from web
            self.__commands.append(self.download_step(url=url,
                                                      directory=self.__wd))

        # Untar package
        self.__commands.append(self.untar_step(
            tarball=posixpath.join(self.__wd, tarball), directory=self.__wd))

        # Install
        install_args = ['--install-to {}'.format(self.__prefix)]
        if self.__eula:
            install_args.append('--accept')
        if self.__microarchitectures:
            install_args.append('--only-install-microarchitectures={}'.format(
                ','.join(self.__microarchitectures)))
        package_directory = 'Arm-Compiler-for-linux_{0}_AArch64_{1}_aarch64'.format(self.__version, self.__package_string)
        self.__commands.append('cd {0} && ./{1} {2}'.format(
            posixpath.join(self.__wd, package_directory),
            self.__installer_template.format(self.__version),
            ' '.join(install_args)))

        # Cleanup tarball and directory
        self.__commands.append(self.cleanup_step(
            items=[posixpath.join(self.__wd, tarball),
                   posixpath.join(self.__wd, package_directory)]))

        # Set environment
        self.environment_variables['MODULEPATH'] = '{}:$MODULEPATH'.format(
            posixpath.join(self.__prefix, 'modulefiles'))

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples

        ```python
        a = arm_allinea_compiler(...)
        Stage0 += a
        Stage1 += a.runtime()
        ```
        """
        instructions = []
        instructions.append(comment('Arm Allinea Studio'))

        paths = []

        # Redistributable libraries from redistributables.txt
        # The allowed list of redistributable libraries does not
        # include all Arm Allinea Studio libraries that get typically
        # linked; consider using '-static-arm-libs'.

        # OpenMP and Fortran runtime libraries
        compiler_redist_path = posixpath.join(
            self.__prefix,
            'arm-linux-compiler-{0}_Generic-AArch64_{1}_aarch64-linux'.format(
                self.__version, self.__directory_string),
            'lib')
        paths.append(compiler_redist_path)
        instructions.append(
            copy(_from=_from,
                 src=[posixpath.join(compiler_redist_path, lib)
                      for lib in ['libgomp.so', 'libiomp5.so', 'libomp.so',
                                  'libflang.so', 'libflangrti.so']],
                 dest=posixpath.join(compiler_redist_path, '')))

        # Performance libraries
        microarch_string = {'generic': 'Generic-AArch64',
                            'generic-sve': 'Generic-SVE',
                            'neoverse-n1': 'Neoverse-N1',
                            'thunderx2t99': 'ThunderX2CN99'}
        for microarch in self.__microarchitectures:
            armpl_arm_redist_path = posixpath.join(
                self.__prefix,
                'armpl-{0}.0_{1}_{2}_arm-linux-compiler_{0}_aarch64-linux'.format(
                    self.__version, microarch_string[microarch],
                    self.__directory_string),
                'lib')
            paths.append(armpl_arm_redist_path)
            instructions.append(
                copy(_from=_from,
                     src=[posixpath.join(armpl_arm_redist_path, lib)
                          for lib in ['libamath.so', 'libamath_dummy.so',
                                      'libastring.so']],
                     dest=posixpath.join(armpl_arm_redist_path, '')))

            armpl_gcc_redist_path = posixpath.join(
                self.__prefix,
                'armpl-{0}.0_{1}_{2}_gcc_{3}_aarch64-linux'.format(
                    self.__version, microarch_string[microarch],
                    self.__directory_string, self.__gcc_version),
                'lib')
            paths.append(armpl_gcc_redist_path)
            instructions.append(
                copy(_from=_from,
                     src=[posixpath.join(armpl_gcc_redist_path, lib)
                          for lib in ['libamath.so', 'libamath_dummy.so',
                                      'libastring.so']],
                     dest=posixpath.join(armpl_gcc_redist_path, '')))

        paths.append('$LD_LIBRARY_PATH') # tack on existing value at end
        self.runtime_environment_variables['LD_LIBRARY_PATH'] = ':'.join(paths)
        instructions.append(environment(variables=self.environment_step(
            runtime=True)))

        return '\n'.join(str(x) for x in instructions)
