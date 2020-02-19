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

from distutils.version import LooseVersion
import logging # pylint: disable=unused-import
import re
import posixpath

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

class nvcompiler(bb_base, hpccm.templates.envvars, hpccm.templates.rm,
                 hpccm.templates.tar, hpccm.templates.wget):
    """The `nvcompiler` building block downloads and installs the NVIDIA HPC
    SDK.  Currently, the only option is to install the latest
    community edition.

    You must agree to the [NVIDIA HPC SDK End-User License Agreement](https://www.pgroup.com/doc/LICENSE.txt) to use this
    building block.

    As a side effect, a toolchain is created containing the NVIDIA
    compilers.  The tool can be passed to other operations that want
    to build using the NVIDIA compilers.

    # Parameters

    environment: Boolean flag to specify whether the environment
    (`LD_LIBRARY_PATH`, `PATH`, and potentially other variables)
    should be modified to include the NVIDIA HPC SDK. The default is
    True.

    eula: By setting this value to `True`, you agree to the [NVIDIA HPC SDK End-User License Agreement](https://www.pgroup.com/doc/LICENSE.txt).
    The default value is `False`.

    extended_environment: Boolean flag to specify whether an extended
    set of environment variables should be defined.  If True, the
    following environment variables will be defined: `CC`, `CPP`,
    `CXX`, `F77`, `F90`, `FC`, and `MODULEPATH`.  In addition, if the
    MPI component is selected then `PGI_OPTL_INCLUDE_DIRS` and
    `PGI_OPTL_LIB_DIRS` will also be defined and `PATH` and
    `LD_LIBRARY_PATH` will include the MPI component.  If False, then
    only `PATH` and `LD_LIBRARY_PATH` will be extended to include the
    NVIDIA HPC SDK.  The default value is `False`.

    mpi: Boolean flag to specify whether the MPI component should be
    installed.  If True, MPI will be installed.  The default value is
    False.

    ospackages: List of OS packages to install prior to installing the
    NVIDIA HPC SDK.  For Ubuntu, the default values are `gcc`, `g++`,
    `gfortran`, `libnuma1`, and also `wget` (if downloading the NVIDIA
    HPC SDK rather than using a tarball in the local build context).
    For RHEL-based Linux distributions, the default values are `gcc`,
    `gcc-c++`, `gcc-gfortran`, `numactl-libs`, and also `wget` (if
    downloading the NVIDIA HPC SDK rather than using a tarball in the
    local build context).

    prefix: The top level install prefix.  The default value is
    `/opt/nvidia`.

    system_cuda: Boolean flag to specify whether the NVIDIA HPC SDK
    should use the system CUDA.  If False, the version(s) of CUDA
    bundled with the NVIDIA HPC SDK will be installed.  The default
    value is False.

    tarball: Path to the NVIDIA HPC SDK tarball relative to the local
    build context.  The default value is empty.  If this is defined,
    the tarball in the local build context will be used rather than
    downloading the tarball from the web.

    version: The version of the NVIDIA HPC SDK to use.  Note this
    value is currently only used when setting the environment and does
    not control the version downloaded.  The default value is `20.1`.

    # Examples

    ```python
    nvcompiler(eula=True)
    ```

    ```python
    nvcompiler(eula=True, tarball='nvlinux-2020-201-x86_64.tar.gz')
    ```

    ```python
    n = nvcompiler(eula=True)
    openmpi(..., toolchain=n.toolchain, ...)
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(nvcompiler, self).__init__(**kwargs)

        self.__arch_directory = None # Filled in __cpu_arch()
        self.__arch_pkg = None # Filled in by __cpu_arch()
        self.__commands = [] # Filled in by __setup()
        self.__libnuma_path = '' # Filled in __distro()
        self.__runtime_commands = [] # Filled in by __setup()

        # By setting this value to True, you agree to the NVIDIA HPC
        # SDK End-User License Agreement
        # (https://www.pgroup.com/doc/LICENSE.txt)
        self.__eula = kwargs.get('eula', False)

        self.__extended_environment = kwargs.get('extended_environment', False)
        self.__mpi = kwargs.get('mpi', False)
        self.__ospackages = kwargs.get('ospackages', [])
        self.__runtime_ospackages = [] # Filled in by __distro()
        self.__prefix = kwargs.get('prefix', '/opt/nvidia')
        self.__referer = r'https://www.pgroup.com/products/community.htm?utm_source=hpccm\&utm_medium=wgt\&utm_campaign=CE\&nvid=nv-int-14-39155'
        self.__system_cuda = kwargs.get('system_cuda', False)
        self.__tarball = kwargs.get('tarball', '')
        self.__url_template = 'https://www.pgroup.com/support/downloader.php?file=pgi-community-linux-{}'

        # The version is fragile since the latest version is
        # automatically downloaded, which may not match this default.
        self.__version = kwargs.get('version', '20.1')
        self.__wd = '/var/tmp' # working directory

        self.toolchain = toolchain(CC='nvc', CXX='nvc++', F77='nvfortran',
                                   F90='nvfortran', FC='nvfortran')

        # Set the CPU architecture specific parameters
        self.__cpu_arch()

        # Set the Linux distribution specific parameters
        self.__distro()

        # Set paths used extensively
        self.__basepath = posixpath.join(self.__prefix, self.__arch_directory,
                                         self.__version, 'compilers')
        self.__mpipath = posixpath.join(self.__prefix, self.__arch_directory,
                                        self.__version, 'mpi', 'openmpi-4.0.2')

        # Construct the series of steps to execute
        self.__setup()

        # Fill in container instructions
        self.__instructions()

    def __instructions(self):
        """Fill in container instructions"""

        self += comment('NVIDIA HPC SDK version {}'.format(self.__version))
        if self.__tarball:
            # Use tarball from local build context
            self += copy(src=self.__tarball,
                         dest=posixpath.join(self.__wd,
                                             posixpath.basename(self.__tarball)))
        else:
            # Downloading, so need wget
            self.__ospackages.append('wget')
        if self.__ospackages:
            self += packages(ospackages=self.__ospackages)
        self += shell(commands=self.__commands)
        self += environment(variables=self.environment_step())

    def __cpu_arch(self):
        """Based on the CPU architecture, set values accordingly.  A user
        specified value overrides any defaults."""

        if hpccm.config.g_cpu_arch == cpu_arch.AARCH64:
            self.__arch_directory = 'linuxarm64'
            self.__arch_pkg = 'arm64' # TODO: just a guess
        elif hpccm.config.g_cpu_arch == cpu_arch.PPC64LE:
            self.__arch_directory = 'linuxpower'
            self.__arch_pkg = 'openpower'
        elif hpccm.config.g_cpu_arch == cpu_arch.X86_64:
            self.__arch_directory = 'linux86-64-llvm'
            self.__arch_pkg = 'x64'
        else: # pragma: no cover
            raise RuntimeError('Unknown CPU architecture')

    def __distro(self):
        """Based on the Linux distribution, set values accordingly.  A user
        specified value overrides any defaults."""

        if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
            if not self.__ospackages:
                self.__ospackages = ['gcc', 'g++', 'gfortran', 'libnuma1']
                if self.__mpi:
                    self.__ospackages.append('openssh-client')
            self.__runtime_ospackages = ['libnuma1']
            if self.__mpi:
                self.__runtime_ospackages.append('openssh-client')
            self.__libnuma_path = '/usr/lib/x86_64-linux-gnu'
        elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
            if not self.__ospackages:
                self.__ospackages = ['gcc', 'gcc-c++', 'gcc-gfortran',
                                     'numactl-libs']
                if self.__mpi:
                    self.__ospackages.append('openssh-clients')
            self.__runtime_ospackages = ['numactl-libs']
            if self.__mpi:
                self.__runtime_ospackages.append('openssh-clients')
            self.__libnuma_path = '/usr/lib64'
        else:
            raise RuntimeError('Unknown Linux distribution')

    def __environment(self, runtime=False):
        """Define environment variables"""
        e = {}

        if runtime:
            # Runtime environment
            if self.__mpi:
                # MPI component is selected
                e['LD_LIBRARY_PATH'] = '{}:{}:$LD_LIBRARY_PATH'.format(
                    posixpath.join(self.__mpipath, 'lib'),
                    posixpath.join(self.__basepath, 'lib'))
                e['PATH'] = '{}:$PATH'.format(
                    posixpath.join(self.__mpipath, 'bin'))
            else:
                # MPI component is not selected
                e['LD_LIBRARY_PATH'] = '{}:$LD_LIBRARY_PATH'.format(
                    posixpath.join(self.__basepath, 'lib'))
        else:
            # Development environment
            if self.__extended_environment:
                # Mirror the environment defined by the environment module
                e = {'CC': posixpath.join(self.__basepath, 'bin', 'pgcc'),
                     'CPP': '"{} -Mcpp"'.format(
                         posixpath.join(self.__basepath, 'bin', 'nvc')),
                     'CXX': posixpath.join(self.__basepath, 'bin', 'nvc++'),
                     'F77': posixpath.join(self.__basepath, 'bin',
                                           'nvfortran'),
                     'F90': posixpath.join(self.__basepath, 'bin',
                                           'nvfortran'),
                     'FC': posixpath.join(self.__basepath, 'bin', 'nvfortran'),
                     'MODULEPATH': '{}:$MODULEPATH'.format(
                         posixpath.join(self.__prefix, 'modulefiles'))}
                if self.__mpi:
                    # MPI component is selected
                    e['LD_LIBRARY_PATH'] = '{}:{}:$LD_LIBRARY_PATH'.format(
                        posixpath.join(self.__mpipath, 'lib'),
                        posixpath.join(self.__basepath, 'lib'))
                    e['PATH'] = '{}:{}:$PATH'.format(
                        posixpath.join(self.__mpipath, 'bin'),
                        posixpath.join(self.__basepath, 'bin'))
                    e['PGI_OPTL_INCLUDE_DIRS'] = posixpath.join(
                        self.__mpipath, 'include')
                    e['PGI_OPTL_LIB_DIRS'] = posixpath.join(self.__mpipath,
                                                            'lib')
                else:
                    # MPI component is not selected
                    e['LD_LIBRARY_PATH'] = '{}:$LD_LIBRARY_PATH'.format(
                        posixpath.join(self.__basepath, 'lib'))
                    e['PATH'] = '{}:$PATH'.format(
                        posixpath.join(self.__basepath, 'bin'))
            else:
                # Basic environment only
                if self.__mpi:
                    e['LD_LIBRARY_PATH'] = '{}:{}:$LD_LIBRARY_PATH'.format(
                        posixpath.join(self.__mpipath, 'lib'),
                        posixpath.join(self.__basepath, 'lib'))
                    e['PATH'] = '{}:{}:$PATH'.format(
                        posixpath.join(self.__mpipath, 'bin'),
                        posixpath.join(self.__basepath, 'bin'))
                else:
                    # MPI component is not selected
                    e = {'PATH': '{}:$PATH'.format(
                        posixpath.join(self.__basepath, 'bin')),
                         'LD_LIBRARY_PATH': '{}:$LD_LIBRARY_PATH'.format(
                             posixpath.join(self.__basepath, 'lib'))}

        return e

    def __setup(self):
        """Construct the series of shell commands, i.e., fill in
           self.__commands"""

        if self.__tarball:
            # Use tarball from local build context
            tarball = posixpath.basename(self.__tarball)

            # Figure out the version from the tarball name
            match = re.match(r'nvlinux-\d+-(?P<year>\d\d)0?(?P<month>[1-9][0-9]?)',
                             tarball)
            if match and match.groupdict()['year'] and match.groupdict()['month']:
                self.__version = '{0}.{1}'.format(match.groupdict()['year'],
                                                  match.groupdict()['month'])
        else:
            raise RuntimeError('download not implemented yet')
            # The URL would normally result in a downloaded file with
            # the name 'downloader.php?file=nvcompiler-community-linux-x64'.
            # Also, the version downloaded cannot be controlled, it
            # will always be the 'latest'.  Use a synthetic tarball
            # filename.
            tarball = 'nvcompiler-community-linux-{}-latest.tar.gz'.format(
                self.__arch_pkg)

            self.__commands.append(self.download_step(
                url=self.__url_template.format(self.__arch_pkg),
                outfile=posixpath.join(self.__wd, tarball),
                referer=self.__referer, directory=self.__wd))

        self.__commands.append(self.untar_step(
            args=['--no-same-owner'], # TODO: workaround?
            tarball=posixpath.join(self.__wd, tarball),
            directory=posixpath.join(self.__wd, 'nvcompiler')))

        flags = {'NVCOMPILER_ACCEPT_EULA': 'accept',
                 'NVCOMPILER_INSTALL_DIR': self.__prefix,
                 'NVCOMPILER_INSTALL_MPI': 'false',
                 'NVCOMPILER_INSTALL_NVIDIA': 'true',
                 'NVCOMPILER_MPI_GPU_SUPPORT': 'false',
                 'NVCOMPILER_SILENT': 'true'}
        if not self.__eula:
            # This will fail when building the container
            logging.warning('NVIDIA HPC SDK EULA was not accepted')
            flags['NVCOMPILER_ACCEPT_EULA'] = 'decline'
            flags['NVCOMPILER_SILENT'] = 'false'
        if self.__system_cuda:
            flags['NVCOMPILER_INSTALL_NVIDIA'] = 'false'
        if self.__mpi:
            flags['NVCOMPILER_INSTALL_MPI'] = 'true'
            flags['NVCOMPILER_MPI_GPU_SUPPORT'] = 'true'
        flag_string = ' '.join('{0}={1}'.format(key, val)
                               for key, val in sorted(flags.items()))

        self.__commands.append('cd {0} && {1} ./install'.format(
            posixpath.join(self.__wd, 'nvcompiler'), flag_string))

        # Create siterc to specify use of the system CUDA
        siterc = posixpath.join(self.__basepath, 'bin', 'siterc')
        if self.__system_cuda:
            self.__commands.append(
                'echo "set CUDAROOT=/usr/local/cuda;" >> {}'.format(siterc))

        # Create siterc to respect LIBRARY_PATH
        # https://www.pgroup.com/support/faq.htm#lib_path_ldflags
        self.__commands.append(r'echo "variable LIBRARY_PATH is environment(LIBRARY_PATH);" >> {}'.format(siterc))
        self.__commands.append(r'echo "variable library_path is default(\$if(\$LIBRARY_PATH,\$foreach(ll,\$replace(\$LIBRARY_PATH,":",), -L\$ll)));" >> {}'.format(siterc))
        self.__commands.append(r'echo "append LDLIBARGS=\$library_path;" >> {}'.format(siterc))

        # TODO: temporary (?) workarounds
        if hpccm.config.g_cpu_arch == cpu_arch.X86_64:
            self.__commands.append('ln -sf {0} {1}'.format(
                'libnuma.so',
                posixpath.join(self.__basepath, 'lib', 'libnuma.so.1')))
        if hpccm.config.g_cpu_arch != cpu_arch.AARCH64:
            self.__commands.append('ln -sf {0} {1}'.format(
                posixpath.join('..', 'lib', 'libomp', 'libomptarget.so'),
                posixpath.join(self.__basepath, 'REDIST', 'libomptarget.so')))

        # Cleanup
        self.__commands.append(self.cleanup_step(
            items=[posixpath.join(self.__wd, tarball),
                   posixpath.join(self.__wd, 'nvcompiler')]))

        # libnuma.so and libnuma.so.1 must be symlinks to the system
        # libnuma library.  They are originally symlinks, but Docker
        # "COPY -from" copies the file pointed to by the symlink,
        # converting them to files, so recreate the symlinks.
        if hpccm.config.g_cpu_arch == cpu_arch.X86_64:
            self.__runtime_commands.append('ln -sf {0} {1}'.format(
                posixpath.join(self.__libnuma_path, 'libnuma.so.1'),
                posixpath.join(self.__basepath, 'lib', 'libnuma.so')))
            self.__runtime_commands.append('ln -sf {0} {1}'.format(
                posixpath.join(self.__libnuma_path, 'libnuma.so.1'),
                posixpath.join(self.__basepath, 'lib', 'libnuma.so.1')))

        # Set the environment
        self.environment_variables = self.__environment()
        self.runtime_environment_variables = self.__environment(runtime=True)

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples

        ```python
        n = nvcompiler(...)
        Stage0 += n
        Stage1 += n.runtime()
        ```
        """
        instructions = []
        instructions.append(comment('NVIDIA HPC SDK'))

        if self.__runtime_ospackages:
            instructions.append(packages(ospackages=self.__runtime_ospackages))

        instructions.append(copy(_from=_from,
                                 src=posixpath.join(self.__basepath,
                                                    'REDIST', '*.so*'),
                                 dest=posixpath.join(self.__basepath,
                                                     'lib', '')))

        if self.__mpi:
            instructions.append(copy(_from=_from,
                                     src=self.__mpipath, dest=self.__mpipath))

        if self.__runtime_commands:
            instructions.append(shell(commands=self.__runtime_commands))

        instructions.append(environment(variables=self.environment_step(
            runtime=True)))

        return '\n'.join(str(x) for x in instructions)
