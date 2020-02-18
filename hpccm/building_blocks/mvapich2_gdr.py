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

"""MVAPICH2-GDR building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import posixpath
import re

import hpccm.config
import hpccm.templates.envvars
import hpccm.templates.ldconfig
import hpccm.templates.rm
import hpccm.templates.wget

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.packages import packages
from hpccm.common import linux_distro
from hpccm.primitives.comment import comment
from hpccm.primitives.copy import copy
from hpccm.primitives.environment import environment
from hpccm.primitives.shell import shell
from hpccm.toolchain import toolchain

class mvapich2_gdr(bb_base, hpccm.templates.envvars, hpccm.templates.ldconfig,
                   hpccm.templates.rm, hpccm.templates.wget):
    """The `mvapich2_gdr` building blocks installs the
    [MVAPICH2-GDR](http://mvapich.cse.ohio-state.edu) component.
    Depending on the parameters, the package will be downloaded from
    the web (default) or copied from the local build context.

    MVAPICH2-GDR is distributed as a binary package, so certain
    dependencies need to be met and only certain combinations of
    recipe components are supported; please refer to the MVAPICH2-GDR
    documentation for more information.

    The [GNU compiler](#gnu) or [PGI compiler](#pgi) building blocks
    should be installed prior to this building block.

    The [Mellanox OFED](#mlnx_ofed) building block should be installed
    prior to this building block.

    The [gdrcopy](#gdrcopy) building block should be installed prior
    to this building block.

    As a side effect, a toolchain is created containing the MPI
    compiler wrappers.  The toolchain can be passed to other
    operations that want to build using the MPI compiler wrappers.

    Note: Using MVAPICH2-GDR on non-RHEL-based Linux distributions has
    several issues, including compiler version mismatches and libnuma
    incompatibilities.

    # Parameters

    arch: The processor architecture of the MVAPICH2-GDR package.  The
    default value is set automatically based on the processor
    architecture of the base image.

    cuda_version: The version of CUDA the MVAPICH2-GDR package was
    built against.  The version string format is X.Y.  The version
    should match the version of CUDA provided by the base image.  This
    value is ignored if `package` is set.  The default value is `9.2`.

    environment: Boolean flag to specify whether the environment
    (`LD_LIBRARY_PATH` and `PATH`) should be modified to include
    MVAPICH2-GDR. The default is True.

    gnu: Boolean flag to specify whether a GNU build should be used.
    The default value is True.

    ldconfig: Boolean flag to specify whether the MVAPICH2-GDR library
    directory should be added dynamic linker cache.  If False, then
    `LD_LIBRARY_PATH` is modified to include the MVAPICH2-GDR library
    directory. The default value is False.

    mlnx_ofed_version: The version of Mellanox OFED the
    MVAPICH2-GDR package was built against.  The version string format
    is X.Y.  The version should match the version of Mellanox OFED
    installed by the `mlnx_ofed` building block.  This value is
    ignored if `package` is set.  The default value is `4.5`.

    ospackages: List of OS packages to install prior to installation.
    For Ubuntu, the default values are `cpio`, `libnuma1`,
    `openssh-client`, `rpm2cpio` and `wget`, plus `libgfortran3` if a
    GNU compiled package is selected.  For RHEL-based Linux
    distributions, the default values are `libpciaccess`,
    `numactl-libs`, `openssh-clients`, and `wget`, plus `libgfortran`
    if a GNU compiled package is selected.

    package: Specify the package name to download.  The package should
    correspond to the other recipe components (e.g., compiler version,
    CUDA version, Mellanox OFED version).  If specified, this option
    overrides all other building block options (e.g., compiler family,
    compiler version, CUDA version, Mellanox OFED version,
    MVAPICH2-GDR version).

    pgi: Boolean flag to specify whether a PGI build should be used.
    The default value is False.

    release: The release of MVAPICH2-GDR to download.  The value is
    ignored is `package` is set.  The default value is `2`.

    version: The version of MVAPICH2-GDR to download.  The value is
    ignored if `package` is set.  The default value is `2.3.3`.  Due
    to differences in the packaging scheme, versions prior to 2.3 are
    not supported.

    # Examples

    ```python
    mvapich2_gdr(version='2.3.1')
    ```

    ```python
    mvapich2_gdr(package='mvapich2-gdr-mcast.cuda10.0.mofed4.3.gnu4.8.5-2.3-1.el7.x86_64.rpm')
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(mvapich2_gdr, self).__init__(**kwargs)

        self.__arch = kwargs.get('arch', hpccm.config.get_cpu_architecture())
        self.__baseurl = kwargs.get('baseurl',
                                    'http://mvapich.cse.ohio-state.edu/download/mvapich/gdr')
        self.__cuda_version = kwargs.get('cuda_version', '9.2')
        self.__gnu = kwargs.get('gnu', True)
        self.__gnu_version = kwargs.get('gnu_version', '4.8.5')
        self.__install_path_template = '/opt/mvapich2/gdr/{0}/mcast/no-openacc/{1}/{2}/mpirun/{3}'
        self.__mofed_version = kwargs.get('mlnx_ofed_version', '4.5')
        self.__ospackages = kwargs.get('ospackages', [])
        self.__package = kwargs.get('package', '')
        self.__package_template = 'mvapich2-gdr-mcast.{0}.{1}.{2}-{3}-{4}.el7.{5}.rpm'
        self.__pgi = kwargs.get('pgi', False)
        self.__pgi_version = kwargs.get('pgi_version', '18.10')
        self.__release = kwargs.get('release', '2')
        self.version = kwargs.get('version', '2.3.3')
        self.__wd = '/var/tmp' # working directory

        # Output toolchain
        self.toolchain = toolchain(CC='mpicc', CXX='mpicxx', F77='mpif77',
                                   F90='mpif90', FC='mpifort')

        # Validate compiler choice
        if self.__gnu and self.__pgi and not self.__package:
            logging.warning('Multiple compilers selected, using PGI')
            self.__gnu = False
        elif not self.__gnu and not self.__pgi:
            logging.warning('No compiler selected, using GNU')
            self.__gnu = True

        self.__commands = []              # Filled in by __setup()
        self.__install_path = ''          # Filled in by __setup()

        # Set the Linux distribution specific parameters
        self.__distro()

        # Construct the series of steps to execute
        self.__setup()

        # Fill in container instructions
        self.__instructions()

    def __instructions(self):
        """Fill in container instructions"""

        self += comment('MVAPICH2-GDR version {}'.format(self.version))
        self += packages(ospackages=self.__ospackages)
        self += shell(commands=self.__commands)
        self += environment(variables=self.environment_step())

    def __distro(self):
        """Based on the Linux distribution, set values accordingly.  A user
        specified value overrides any defaults."""

        if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
            if not self.__ospackages:
                self.__ospackages = ['cpio', 'libnuma1', 'libpciaccess0',
                                     'openssh-client', 'rpm2cpio', 'wget']
                if self.__gnu:
                    self.__ospackages.append('libgfortran3')
            self.__runtime_ospackages = ['libnuma1', 'libpciaccess0',
                                         'openssh-client']
            if self.__gnu:
                self.__runtime_ospackages.append('libgfortran3')

            self.__installer_template = 'cd / && rpm2cpio {} | cpio -id'
        elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
            if not self.__ospackages:
                self.__ospackages = ['libpciaccess', 'numactl-libs',
                                     'openssh-clients', 'wget']
                if self.__gnu:
                    self.__ospackages.append('libgfortran')
            self.__runtime_ospackages = ['libpciaccess', 'numactl-libs',
                                         'openssh-clients']
            if self.__gnu:
                self.__runtime_ospackages.append('libgfortran')

            # The RPM has dependencies on some CUDA libraries that are
            # present, but not in the RPM database.  Use --nodeps as a
            # workaround.
            self.__installer_template = 'rpm --install --nodeps {}'

        else: # pragma: no cover
            raise RuntimeError('Unknown Linux distribution')

    def __setup(self):
        """Construct the series of shell commands and environment variables,
           i.e., fill in self.__commands and self.environment_variables"""

        if self.__package:
            # Override individual settings and just use the specified package
            package = self.__package

            # Deduce version strings from package name
            match = re.search(r'(?P<cuda>cuda\d+\.\d+)\.(?P<mofed>mofed\d+\.\d+)\.(?P<compiler>(gnu\d+\.\d+\.\d+)|(pgi\d+\.\d+))-(?P<version>\d+\.\d+)', package)
            cuda_string = match.groupdict()['cuda']
            mofed_string = match.groupdict()['mofed']
            compiler_string = match.groupdict()['compiler']
            self.version = match.groupdict()['version']
        else:
            # Build the version strings based on the specified options
            if self.__gnu:
                compiler_string = 'gnu{}'.format(self.__gnu_version)
            elif self.__pgi:
                compiler_string = 'pgi{}'.format(self.__pgi_version)
            else:
                logging.error('Unknown compiler')
                compiler_string = 'unknown'

            cuda_string = 'cuda{}'.format(self.__cuda_version)
            mofed_string = 'mofed{}'.format(self.__mofed_version)

            # Package filename
            package = self.__package_template.format(
                cuda_string, mofed_string, compiler_string, self.version,
                self.__release, self.__arch)

        self.__install_path = self.__install_path_template.format(
            self.version, cuda_string, mofed_string, compiler_string)

        # Download source from web
        url = '{0}/{1}/{2}/{3}'.format(self.__baseurl, self.version,
                                       mofed_string, package)
        self.__commands.append(self.download_step(url=url, directory=self.__wd))

        # Install the package
        self.__commands.append(
            self.__installer_template.format(posixpath.join(self.__wd,
                                                            package)))

        # Workaround for bad path in the MPI compiler wrappers
        self.__commands.append('(test -f /usr/bin/bash || ln -s /bin/bash /usr/bin/bash)')

        # Workaround for using compiler wrappers in the build stage
        cuda_home = '/usr/local/cuda'
        self.__commands.append('ln -s {0} {1}'.format(
            posixpath.join(cuda_home, 'lib64', 'stubs', 'nvidia-ml.so'),
            posixpath.join(cuda_home, 'lib64', 'stubs', 'nvidia-ml.so.1')))

        # Cleanup
        self.__commands.append(self.cleanup_step(
            items=[posixpath.join(self.__wd, package)]))

        # Setup environment variables
        self.environment_variables['PATH'] = '{}:$PATH'.format(
            posixpath.join(self.__install_path, 'bin'))
        # Workaround for using compiler wrappers in the build stage
        self.environment_variables['PROFILE_POSTLIB'] = '"-L{} -lnvidia-ml"'.format('/usr/local/cuda/lib64/stubs')

        # Set library path
        libpath = posixpath.join(self.__install_path, 'lib64')
        if self.ldconfig:
            self.__commands.append(self.ldcache_step(directory=libpath))
        else:
            self.environment_variables['LD_LIBRARY_PATH'] = '{}:$LD_LIBRARY_PATH'.format(libpath)


    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples

        ```python
        m = mvapich2_gdr(...)
        Stage0 += m
        Stage1 += m.runtime()
        ```
        """
        instructions = []
        instructions.append(comment('MVAPICH2-GDR'))
        instructions.append(packages(ospackages=self.__runtime_ospackages))
        instructions.append(copy(src=self.__install_path,
                                 dest=self.__install_path, _from=_from))
        if self.ldconfig:
            instructions.append(shell(
                commands=[self.ldcache_step(
                    directory=posixpath.join(self.__install_path, 'lib64'))]))
        # No need to workaround compiler wrapper issue for the runtime.
        instructions.append(environment(
            variables=self.environment_step(exclude=['PROFILE_POSTLIB'])))
        return '\n'.join(str(x) for x in instructions)
