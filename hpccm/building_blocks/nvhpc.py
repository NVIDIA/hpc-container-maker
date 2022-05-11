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
    NVIDIA HPC SDK is installed from a package repository.
    Alternatively the tar package can be downloaded by specifying the
    `tarball` parameter, or a local tar package may used instead by
    specifying the `package` parameter.

    You must agree to the [NVIDIA HPC SDK End-User License Agreement](https://docs.nvidia.com/hpc-sdk/eula) to use this
    building block.

    As a side effect, a toolchain is created containing the NVIDIA
    compilers.  The tool can be passed to other operations that want
    to build using the NVIDIA compilers.

    # Parameters

    cuda: The default CUDA version to configure.  The default is an
    empty value, i.e., use the latest version supported by the NVIDIA
    HPC SDK.  This value is ignored if installing from the package
    repository.

    cuda_multi: Boolean flag to specify whether the NVIDIA HPC SDK
    support for multiple CUDA versions should be installed.  The
    default value is `True`.

    environment: Boolean flag to specify whether the environment
    (`CPATH`, `LD_LIBRARY_PATH`, `MANPATH`, and `PATH`) should be
    modified to include the NVIDIA HPC SDK. The default is True.

    eula: By setting this value to `True`, you agree to the [NVIDIA HPC SDK End-User License Agreement](https://docs.nvidia.com/hpc-sdk/eula).
    The default value is `False`.

    extended_environment: Boolean flag to specify whether an extended
    set of environment variables should be defined.  If True, the
    following environment variables `CC`, `CPP`, `CXX`, `F77`, `F90`,
    and `FC`.  If False, then only `CPATH`, `LD_LIBRARY_PATH`,
    `MANPATH`, and `PATH` will be extended to include the NVIDIA HPC
    SDK.  The default value is `False`.

    mpi: Boolean flag to specify whether MPI should be included in the
    environment.  The default value is `True`.

    ospackages: List of OS packages to install prior to installing the
    NVIDIA HPC SDK.  The default value is `ca-certificates`.  If not
    installing from the package repository, then for Ubuntu, the
    default values are `bc`, `debianutils`, `gcc`, `g++`, `gfortran`,
    `libatomic1`, `libnuma1`, `openssh-client`, and `wget`, and for
    RHEL-based Linux distributions, the default values are `bc`,
    `gcc`, `gcc-c++`, `gcc-gfortran`, `libatomic`, `numactl-libs`,
    `openssh-clients`, `wget`, and `which`.

    package: Path to the NVIDIA HPC SDK tar package file relative to
    the local build context.  The default value is empty.

    prefix: The top level install prefix.  The default value is
    `/opt/nvidia/hpc_sdk`.  This value is ignored when installing from
    the package repository.

    redist: The list of redistributable files to copy into the runtime
    stage.  The paths are relative to the `REDIST` directory and
    wildcards are supported.  The default is an empty list.

    tarball: Boolean flag to specify whether the NVIDIA HPC SDK should
    be installed by downloading the tar package file.  If False,
    install from the package repository.  The default is False.

    toolchain: The toolchain object to be used to configure the HPC
    SDK with a specific GNU toolchain.  The default is empty, i.e., use
    the default GNU toolchain.

    url: The location of the package that should be installed.  The default value is `https://developer.download.nvidia.com/hpc-sdk/nvhpc_X_Y_Z_cuda_multi.tar.gz`, where `X, `Y`, and `Z` are the year, version, and architecture whose values are automatically determined.

    version: The version of the HPC SDK to use.  Note when `package`
    is set the version is determined automatically from the package
    file name.  The default value is `22.3`.

    # Examples

    ```python
    nvhpc(eula=True)
    ```

    ```python
    nvhpc(eula=True, tarball=True)
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

        self.__arch_directory = None # Filled in by __cpu_arch()
        self.__arch_label = '' # Filled in by __cpu_arch()
        self.__cuda_multi = kwargs.get('cuda_multi', True)
        self.__cuda_version = kwargs.get('cuda', None)
        self.__commands = [] # Filled in by __setup_tarball()

        # By setting this value to True, you agree to the NVIDIA HPC
        # SDK End-User License Agreement
        # (https://docs.nvidia.com/hpc-sdk/eula)
        self.__eula = kwargs.get('eula', False)

        self.__extended_environment = kwargs.get('extended_environment', False)
        self.__hpcx = kwargs.get('_hpcx', False)
        self.__mpi = kwargs.get('mpi', True)
        self.__nvhpc_package = '' # Filled in by __distro()
        self.__ospackages = kwargs.get('ospackages', [])
        self.__runtime_ospackages = [] # Filled in by __distro()
        self.__prefix = kwargs.get('prefix', '/opt/nvidia/hpc_sdk')
        self.__redist = kwargs.get('redist', [])
        self.__stdpar_cudacc = kwargs.get('stdpar_cudacc', None)
        self.__tarball = kwargs.get('tarball', False)
        self.__toolchain = kwargs.get('toolchain', None)
        self.__url = kwargs.get('url', None)
        self.__version = kwargs.get('version', '22.3')
        self.__wd = kwargs.get('wd', hpccm.config.g_wd) # working directory
        self.__year = '' # Filled in by __get_version()

        self.toolchain = toolchain(CC='nvc', CXX='nvc++', F77='nvfortran',
                                   F90='nvfortran', FC='nvfortran')

        if StrictVersion(self.__version) >= StrictVersion('22.2'):
            self.__cuda_version_default = '11.6'
        elif StrictVersion(self.__version) >= StrictVersion('21.11'):
            self.__cuda_version_default = '11.5'
        elif StrictVersion(self.__version) >= StrictVersion('21.7'):
            self.__cuda_version_default = '11.4'
        elif StrictVersion(self.__version) >= StrictVersion('21.5'):
            self.__cuda_version_default = '11.3'
        elif StrictVersion(self.__version) >= StrictVersion('21.2'):
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
        if self.package or self.__tarball or self.__url:
            self.__setup_tarball()

        # Set the environment
        self.environment_variables = self.__environment()

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

        if self.package or self.__tarball or self.__url:
            # tarball install
            self += shell(commands=self.__commands)
        else:
            # repository install
            self += packages(
                apt_repositories=['deb [trusted=yes] https://developer.download.nvidia.com/hpc-sdk/ubuntu/{} /'.format(self.__arch_label)],
                ospackages=[self.__nvhpc_package],
                yum_repositories=['https://developer.download.nvidia.com/hpc-sdk/rhel/nvhpc.repo'])

        if self.__toolchain:
            # Regenerate the localrc using the compilers from the specified
            # toolchain
            compiler_bin = posixpath.join(self.__basepath, 'compilers', 'bin')

            args = ['-x']
            if self.__toolchain.CC:
                args.append('-gcc {}'.format(self.__toolchain.CC))
            if self.__toolchain.CXX:
                args.append('-gpp {}'.format(self.__toolchain.CXX))
            if self.__toolchain.F77:
                args.append('-g77 {}'.format(self.__toolchain.F77))

            self += shell(commands=['{0} {1} {2}'.format(
                posixpath.join(compiler_bin, 'makelocalrc'), compiler_bin,
                ' '.join(args))])

        self += environment(variables=self.environment_step())

    def __cpu_arch(self):
        """Based on the CPU architecture, set values accordingly.  A user
        specified value overrides any defaults."""

        if hpccm.config.g_cpu_arch == cpu_arch.AARCH64:
            self.__arch_directory = 'Linux_aarch64'
            if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
                self.__arch_label = 'arm64'
            else:
                self.__arch_label = 'aarch64'
            if StrictVersion(self.__version) < StrictVersion('20.11'):
                self.__cuda_multi = False # CUDA multi packages not available
        elif hpccm.config.g_cpu_arch == cpu_arch.PPC64LE:
            self.__arch_directory = 'Linux_ppc64le'
            if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
                self.__arch_label = 'ppc64el'
            else:
                self.__arch_label = 'ppc64le'
        elif hpccm.config.g_cpu_arch == cpu_arch.X86_64:
            self.__arch_directory = 'Linux_x86_64'
            if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
                self.__arch_label = 'amd64'
            else:
                self.__arch_label = 'x86_64'
        else: # pragma: no cover
            raise RuntimeError('Unknown CPU architecture')

    def __distro(self):
        """Based on the Linux distribution, set values accordingly.  A user
        specified value overrides any defaults."""

        if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
            version = self.__version.replace('.', '-')
            if self.__cuda_multi:
                self.__nvhpc_package = 'nvhpc-{}-cuda-multi'.format(version)
            else:
                self.__nvhpc_package = 'nvhpc-{}'.format(version)

            if not self.__ospackages:
                if self.package or self.__tarball:
                    self.__ospackages = ['bc', 'debianutils', 'gcc', 'g++',
                                         'gfortran', 'libatomic1', 'libnuma1',
                                         'openssh-client', 'wget']
                else:
                    self.__ospackages = ['ca-certificates']
            self.__runtime_ospackages = ['libatomic1', 'libnuma1',
                                         'openssh-client']
        elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
            if self.__cuda_multi:
                self.__nvhpc_package = 'nvhpc-cuda-multi-{}'.format(self.__version)
            else:
                self.__nvhpc_package = 'nvhpc-{}'.format(self.__version)

            if not self.__ospackages:
                if self.package or self.__tarball:
                    self.__ospackages = ['bc', 'gcc', 'gcc-c++',
                                         'gcc-gfortran', 'libatomic',
                                         'openssh-clients', 'numactl-libs',
                                         'wget', 'which']
                else:
                    self.__ospackages = ['ca-certificates']
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
            posixpath.join(self.__basepath, 'compilers', 'extras', 'qd',
                           'include', 'qd'),
            posixpath.join(self.__basepath, 'math_libs', 'include')]

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
        elif self.__hpcx:
            # Set environment for HPC-X
            if StrictVersion(self.__version) >= StrictVersion('22.2'):
                hpcx_version = 'latest'
            elif StrictVersion(self.__version) >= StrictVersion('21.11'):
                hpcx_version = 'hpcx-2.10.beta'
            elif StrictVersion(self.__version) >= StrictVersion('21.9'):
                hpcx_version = 'hpcx-2.9.0'
            elif StrictVersion(self.__version) >= StrictVersion('21.7'):
                hpcx_version = 'hpcx-2.8.1'
            elif StrictVersion(self.__version) < StrictVersion('21.5'):
              hpcx_version = 'hpcx-2.7.4'
            hpcx_dir = posixpath.join(self.__basepath, 'comm_libs', 'hpcx',
                                      hpcx_version)

            hpcx_ucx_dir = posixpath.join(hpcx_dir, 'ucx', 'mt')
            #hpcx_ucx_dir = posixpath.join(hpcx_dir, 'ucx')
            hpcx_sharp_dir = posixpath.join(hpcx_dir, 'sharp')
            hpcx_nccl_rdma_sharp_plugin_dir = posixpath.join(
                hpcx_dir, 'nccl_rdma_sharp_plugin')
            hpcx_hcoll_dir = posixpath.join(hpcx_dir, 'hcoll')
            hpcx_mpi_dir = posixpath.join(hpcx_dir, 'ompi')
            hpcx_oshmem_dir = hpcx_mpi_dir

            cpath.append(':'.join([
                posixpath.join(hpcx_hcoll_dir, 'include'),
                posixpath.join(hpcx_mpi_dir, 'include'),
                posixpath.join(hpcx_sharp_dir, 'include'),
                posixpath.join(hpcx_ucx_dir, 'include'),
                '$CPATH']))
            e['HPCX_DIR'] = hpcx_dir
            e['HPCX_HCOLL_DIR'] = hpcx_hcoll_dir
            e['HPCX_MPI_DIR'] = hpcx_mpi_dir
            e['HPCX_NCCL_RDMA_SHARP_PLUGIN_DIR'] = hpcx_nccl_rdma_sharp_plugin_dir
            e['HPCX_OSHMEM_DIR'] = hpcx_oshmem_dir
            e['HPCX_SHARP_DIR'] = hpcx_sharp_dir
            e['HPCX_UCX_DIR'] = hpcx_ucx_dir
            e['LIBRARY_PATH'] = ':'.join([
                posixpath.join(hpcx_hcoll_dir, 'lib'),
                posixpath.join(hpcx_mpi_dir, 'lib'),
                posixpath.join(hpcx_nccl_rdma_sharp_plugin_dir, 'lib'),
                posixpath.join(hpcx_sharp_dir, 'lib'),
                posixpath.join(hpcx_ucx_dir, 'lib'),
                '$LIBRARY_PATH'])
            ld_library_path.append(':'.join([
                posixpath.join(hpcx_hcoll_dir, 'lib'),
                posixpath.join(hpcx_mpi_dir, 'lib'),
                posixpath.join(hpcx_nccl_rdma_sharp_plugin_dir, 'lib'),
                posixpath.join(hpcx_sharp_dir, 'lib'),
                posixpath.join(hpcx_ucx_dir, 'lib'),
                posixpath.join(hpcx_ucx_dir, 'lib', 'ucx'),
                '$LD_LIBRARY_PATH']))
            e['MPI_HOME'] = hpcx_mpi_dir
            e['OMPI_HOME'] = hpcx_mpi_dir
            e['OPAL_PREFIX'] = hpcx_mpi_dir
            e['OSHMEM_HOME'] = hpcx_mpi_dir
            path.append(':'.join([
                posixpath.join(hpcx_hcoll_dir, 'bin'),
                posixpath.join(hpcx_mpi_dir, 'bin'),
                posixpath.join(hpcx_ucx_dir, 'bin'),
                '$PATH']))
            e['PKG_CONFIG_PATH'] = ':'.join([
                posixpath.join(hpcx_hcoll_dir, 'lib', 'pkgconfig'),
                posixpath.join(hpcx_mpi_dir, 'lib', 'pkgconfig'),
                posixpath.join(hpcx_sharp_dir, 'lib', 'pkgconfig'),
                posixpath.join(hpcx_ucx_dir, 'lib', 'pkgconfig'),
                '$PKG_CONFIG_PATH'])
            e['SHMEM_HOME'] = hpcx_mpi_dir

        if cpath:
            e['CPATH'] = '{}:$CPATH'.format(':'.join(cpath))
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

    def __setup_tarball(self):
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
