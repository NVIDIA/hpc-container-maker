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

"""NVIDIA HPC SDK building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from distutils.version import StrictVersion
import logging
import re
import posixpath

import hpccm.config
import hpccm.templates.downloader
import hpccm.templates.envvars
import hpccm.templates.rm

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.packages import packages
from hpccm.common import cpu_arch, linux_distro
from hpccm.primitives.comment import comment
from hpccm.primitives.copy import copy
from hpccm.primitives.environment import environment
from hpccm.primitives.shell import shell
from hpccm.toolchain import toolchain

class nvhpc(bb_base, hpccm.templates.downloader, hpccm.templates.envvars,
            hpccm.templates.rm):
    """The `nvhpc` building block downloads and installs the [NVIDIA HPC
    SDK](https://developer.nvidia.com/hpc-sdk).  By default, the
    NVIDIA HPC SDK is downloaded, although a local tar package may
    used instead by specifying the `package` parameter.

    You must agree to the [NVIDIA HPC SDK End-User License Agreement](https://docs.nvidia.com/hpc-sdk/eula) to use this
    building block.

    As a side effect, a toolchain is created containing the NVIDIA
    compilers.  The tool can be passed to other operations that want
    to build using the NVIDIA compilers.

    # Parameters

    cuda: The default CUDA version to configure.  The default is an
    empty value, i.e., use the latest version supported by the NVIDIA
    HPC SDK.

    cuda_multi: Boolean flag to specify whether the NVIDIA HPC SDK
    support for multiple CUDA versions should be installed.  The
    default value is `True`.

    environment: Boolean flag to specify whether the environment
    (`LD_LIBRARY_PATH`, `MANPATH`, and `PATH`) should be modified to
    include the NVIDIA HPC SDK. The default is True.

    eula: By setting this value to `True`, you agree to the [NVIDIA HPC SDK End-User License Agreement](https://docs.nvidia.com/hpc-sdk/eula).
    The default value is `False`.

    extended_environment: Boolean flag to specify whether an extended
    set of environment variables should be defined.  If True, the
    following environment variables `CC`, `CPP`, `CXX`, `F77`, `F90`,
    and `FC`.  If False, then only `LD_LIBRARY_PATH`, `MANPATH`, and
    `PATH` will be extended to include the NVIDIA HPC SDK.  The
    default value is `False`.

    mpi: Boolean flag to specify whether MPI should be included in the
    environment.  The default value is `True`.

    ospackages: List of OS packages to install prior to installing the
    NVIDIA HPC SDK.  For Ubuntu, the default values are `bc`,
    `debianutils`, `gcc`, `g++`, `gfortran`, `libatomic`, `libnuma1`,
    `openssh-client`, and `wget`.  For RHEL-based Linux distributions,
    the default values are `bc`, `gcc`, `gcc-c++`, `gcc-gfortran`,
    `libatomic`, `numactl-libs`, `openssh-clients`, `wget`, and
    `which`.

    package: Path to the NVIDIA HPC SDK tar package file relative to
    the local build context.  The default value is empty.

    prefix: The top level install prefix.  The default value is
    `/opt/nvidia/hpc_sdk`.

    redist: The list of redistributable files to copy into the runtime
    stage.  The paths are relative to the `REDIST` directory and
    wildcards are supported.  The default is an empty list.

    url: The location of the package that should be installed.  The default value is `https://developer.download.nvidia.com/hpc-sdk/nvhpc_X_Y_Z_cuda_multi.tar.gz`, where `X, `Y`, and `Z` are the year, version, and architecture whose values are automatically determined.

    version: The version of the HPC SDK to use.  Note when `package`
    is set the version is determined automatically from the package
    file name.  The default value is `21.2`.

    # Examples

    ```python
    nvhpc(eula=True)
    ```

    ```python
    nvhpc(eula=True,
          url='https://developer.download.nvidia.com/hpc-sdk/nvhpc_2020_207_Linux_x86_64_cuda_11.0.tar.gz')
    ```

    ```python
    nvhpc(eula=True,
          package='nvhpc_2020_207_Linux_x86_64_cuda_multi.tar.gz',
          redist=['compilers/lib/*'])
    ```

    ```python
    n = nvhpc(eula=True, ...)
    openmpi(..., toolchain=n.toolchain, ...)
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(nvhpc, self).__init__(**kwargs)

        self.__arch_directory = None # Filled in __cpu_arch()
        self.__cuda_home = kwargs.get('cuda_home', False)
        self.__cuda_multi = kwargs.get('cuda_multi', True)
        self.__cuda_version = kwargs.get('cuda', None)
        self.__commands = [] # Filled in by __setup()

        # By setting this value to True, you agree to the NVIDIA HPC
        # SDK End-User License Agreement
        # (https://docs.nvidia.com/hpc-sdk/eula)
        self.__eula = kwargs.get('eula', False)

        self.__extended_environment = kwargs.get('extended_environment', False)
        self.__mpi = kwargs.get('mpi', True)
        self.__ospackages = kwargs.get('ospackages', [])
        self.__runtime_ospackages = [] # Filled in by __distro()
        self.__prefix = kwargs.get('prefix', '/opt/nvidia/hpc_sdk')
        self.__redist = kwargs.get('redist', [])
        self.__stdpar_cudacc = kwargs.get('stdpar_cudacc', None)
        self.__url = kwargs.get('url', None)
        self.__version = kwargs.get('version', '21.2')
        self.__wd = kwargs.get('wd', hpccm.config.g_wd) # working directory
        self.__year = '' # Filled in by __version()

        self.toolchain = toolchain(CC='nvc', CXX='nvc++', F77='nvfortran',
                                   F90='nvfortran', FC='nvfortran')

        if StrictVersion(self.__version) >= StrictVersion('21.2'):
            self.__cuda_version_default = '11.2'
        elif StrictVersion(self.__version) >= StrictVersion('20.11'):
            self.__cuda_version_default = '11.1'
        else:
            self.__cuda_version_default = '11.0'

        # Set the CPU architecture specific parameters
        self.__cpu_arch()

        # Set the Linux distribution specific parameters
        self.__distro()

        # Figure out the version information
        self.__get_version()

        # Set paths used extensively
        self.__basepath = posixpath.join(self.__prefix, self.__arch_directory,
                                         self.__version)

        # Construct the series of steps to execute
        self.__setup()

        # Fill in container instructions
        self.__instructions()

    def __instructions(self):
        """Fill in container instructions"""

        self += comment('NVIDIA HPC SDK version {}'.format(self.__version))
        if self.package:
            # Use package from local build context
            self += copy(src=self.package,
                         dest=posixpath.join(self.__wd,
                                             posixpath.basename(self.package)))
        if self.__ospackages:
            self += packages(ospackages=self.__ospackages)
        self += shell(commands=self.__commands)
        self += environment(variables=self.environment_step())

    def __cpu_arch(self):
        """Based on the CPU architecture, set values accordingly.  A user
        specified value overrides any defaults."""

        if hpccm.config.g_cpu_arch == cpu_arch.AARCH64:
            self.__arch_directory = 'Linux_aarch64'
            if StrictVersion(self.__version) < StrictVersion('20.11'):
                self.__cuda_multi = False # CUDA multi packages not available
        elif hpccm.config.g_cpu_arch == cpu_arch.PPC64LE:
            self.__arch_directory = 'Linux_ppc64le'
        elif hpccm.config.g_cpu_arch == cpu_arch.X86_64:
            self.__arch_directory = 'Linux_x86_64'
        else: # pragma: no cover
            raise RuntimeError('Unknown CPU architecture')

    def __distro(self):
        """Based on the Linux distribution, set values accordingly.  A user
        specified value overrides any defaults."""

        if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
            if not self.__ospackages:
                self.__ospackages = ['bc', 'debianutils', 'gcc', 'g++',
                                     'gfortran', 'libatomic1', 'libnuma1',
                                     'openssh-client', 'wget']
            self.__runtime_ospackages = ['libatomic1', 'libnuma1',
                                         'openssh-client']
        elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
            if not self.__ospackages:
                self.__ospackages = ['bc', 'gcc', 'gcc-c++', 'gcc-gfortran',
                                     'libatomic', 'openssh-clients',
                                     'numactl-libs', 'wget', 'which']
            self.__runtime_ospackages = ['libatomic', 'numactl-libs',
                                         'openssh-clients']
        else: # pragma: no cover
            raise RuntimeError('Unknown Linux distribution')

    def __environment(self):
        """Define environment variables"""
        e = {}

        # Development environment
        if self.__extended_environment:
            # Mirror the environment defined by the environment module
            e['CC'] = posixpath.join(self.__basepath, 'compilers', 'bin',
                                     'nvc')
            e['CPP'] = 'cpp'
            e['CXX'] = posixpath.join(self.__basepath, 'compilers', 'bin',
                                      'nvc++')
            e['F77'] = posixpath.join(self.__basepath, 'compilers', 'bin',
                                      'nvfortran')
            e['F90'] = posixpath.join(self.__basepath, 'compilers', 'bin',
                                      'nvfortran')
            e['FC'] = posixpath.join(self.__basepath, 'compilers', 'bin',
                                     'nvfortran')

        cpath = [
            posixpath.join(self.__basepath, 'comm_libs', 'nvshmem', 'include'),
            posixpath.join(self.__basepath, 'comm_libs', 'nccl', 'include'),
            posixpath.join(self.__basepath, 'math_libs', 'include'),
            posixpath.join(self.__basepath, 'compilers', 'include'),
            posixpath.join(self.__basepath, 'cuda', 'include')]

        ld_library_path = [
            posixpath.join(self.__basepath, 'comm_libs', 'nvshmem', 'lib'),
            posixpath.join(self.__basepath, 'comm_libs', 'nccl', 'lib'),
            posixpath.join(self.__basepath, 'math_libs', 'lib64'),
            posixpath.join(self.__basepath, 'compilers', 'lib'),
            posixpath.join(self.__basepath, 'cuda', 'lib64')]

        path = [
            posixpath.join(self.__basepath, 'comm_libs', 'nvshmem', 'bin'),
            posixpath.join(self.__basepath, 'comm_libs', 'nccl', 'bin'),
            posixpath.join(self.__basepath, 'profilers', 'bin'),
            posixpath.join(self.__basepath, 'compilers', 'bin'),
            posixpath.join(self.__basepath, 'cuda', 'bin')]

        if self.__mpi:
            cpath.append(
                posixpath.join(self.__basepath, 'comm_libs', 'mpi', 'include'))
            ld_library_path.append(
                posixpath.join(self.__basepath, 'comm_libs', 'mpi', 'lib'))
            path.append(
                posixpath.join(self.__basepath, 'comm_libs', 'mpi', 'bin'))

        #e['CPATH'] = '{}:$CPATH'.format(':'.join(cpath))
        e['LD_LIBRARY_PATH'] = '{}:$LD_LIBRARY_PATH'.format(':'.join(
            ld_library_path))
        e['MANPATH'] = '{}:$MANPATH'.format(
            posixpath.join(self.__basepath, 'compilers', 'man'))
        e['PATH'] = '{}:$PATH'.format(':'.join(path))

        return e

    def __get_version(self):
        """Figure out the version information"""

        if self.package:
            # Figure out the version from the package name
            match = re.search(r'nvhpc_\d+_(?P<year>\d\d)0?(?P<month>[1-9][0-9]?)',
                              self.package)
            if (match and match.groupdict()['year'] and
                match.groupdict()['month']):
                self.__version = '{0}.{1}'.format(match.groupdict()['year'],
                                                  match.groupdict()['month'])
                self.__year = '20' + match.groupdict()['year']
            else:
                raise RuntimeError('could not parse version from package name')
        else:
            match = re.search(r'(?P<year>\d\d)\.\d+', self.__version)
            if match and match.groupdict()['year']:
                self.__year = '20' + match.groupdict()['year']

    def __setup(self):
        """Construct the series of shell commands, i.e., fill in
           self.__commands"""

        # Download / copy package
        if not self.package:
            if self.__url:
                self.url = self.__url
            else:
                baseurl = 'https://developer.download.nvidia.com/hpc-sdk/{0}/nvhpc_{1}_{2}_{3}_cuda_{{}}.tar.gz'.format(
                    self.__version, self.__year,
                    self.__version.replace('.', ''), self.__arch_directory)
                if self.__cuda_multi:
                    self.url = baseurl.format('multi')
                else:
                    self.url = baseurl.format(
                        self.__cuda_version if self.__cuda_version
                        else self.__cuda_version_default)

        self.__commands.append(self.download_step(wd=self.__wd))

        # Set installer flags
        flags = {'NVHPC_ACCEPT_EULA': 'accept',
                 'NVHPC_INSTALL_DIR': self.__prefix,
                 'NVHPC_SILENT': 'true'}
        if self.__cuda_version:
            flags['NVHPC_DEFAULT_CUDA'] = self.__cuda_version
        if self.__stdpar_cudacc:
            flags['NVHPC_STDPAR_CUDACC'] = self.__stdpar_cudacc
        if not self.__eula:
            # This will fail when building the container
            logging.warning('NVIDIA HPC SDK EULA was not accepted')
            flags['NVHPC_ACCEPT_EULA'] = 'decline'
            flags['NVHPC_SILENT'] = 'false'
        flag_string = ' '.join('{0}={1}'.format(key, val)
                               for key, val in sorted(flags.items()))

        # Install
        self.__commands.append('cd {0} && {1} ./install'.format(
            self.src_directory, flag_string))

        # Cleanup
        remove = [self.src_directory]
        if self.url:
            remove.append(posixpath.join(self.__wd,
                                         posixpath.basename(self.url)))
        elif self.package:
            remove.append(posixpath.join(self.__wd,
                                         posixpath.basename(self.package)))
        self.__commands.append(self.cleanup_step(items=remove))

        # Set the environment
        self.environment_variables = self.__environment()

        # Adjust the toolchain
        if self.__cuda_home:
            self.toolchain.CUDA_HOME = posixpath.join(
                self.__basepath, 'cuda',
                self.__cuda_version if self.__cuda_version
                else self.__cuda_version_default)

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples

        ```python
        n = nvhpc(redist=[...], ...)
        Stage0 += n
        Stage1 += n.runtime()
        ```
        """
        if self.__redist:
            self.rt += comment('NVIDIA HPC SDK')

            if self.__runtime_ospackages:
                self.rt += packages(ospackages=self.__runtime_ospackages)

            redistpath = posixpath.join(self.__prefix,
                                        self.__arch_directory,
                                        self.__version, 'REDIST')

            libdirs = {}

            for r in self.__redist:
                src = posixpath.join(redistpath, r)

                if '*' in posixpath.basename(r):
                    # When using COPY with more than one source file,
                    # the destination must be a directory and end with
                    # a /
                    dest = posixpath.join(posixpath.dirname(redistpath),
                                          posixpath.dirname(r)) + '/'
                else:
                    dest = posixpath.join(posixpath.dirname(redistpath), r)

                self.rt += copy(_from=_from, src=src, dest=dest)

                # If the redist path looks like a library directory,
                # add it to LD_LIBRARY_PATH
                if '/lib' in posixpath.dirname(r):
                    libdirs[posixpath.join(posixpath.dirname(redistpath),
                                           posixpath.dirname(r))] = True

            if self.__redist and self.__mpi:
                mpipath = posixpath.join(self.__basepath, 'comm_libs', 'mpi')
                self.rt += copy(_from=_from, src=mpipath, dest=mpipath)
                libdirs[posixpath.join(mpipath, 'lib')] = True
                self.runtime_environment_variables['PATH'] = '{}:$PATH'.format(
                    posixpath.join(mpipath, 'bin'))

            if libdirs:
                liblist = sorted(libdirs.keys())
                liblist.append('$LD_LIBRARY_PATH')
                
                self.runtime_environment_variables['LD_LIBRARY_PATH'] = ':'.join(liblist)
                self.rt += environment(
                    variables=self.runtime_environment_variables)

        return str(self.rt)
