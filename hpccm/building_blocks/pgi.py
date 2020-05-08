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

"""PGI building block"""

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

class pgi(bb_base, hpccm.templates.envvars, hpccm.templates.rm,
          hpccm.templates.tar, hpccm.templates.wget):
    """The `pgi` building block downloads and installs the PGI compiler.
    Currently, the only option is to install the latest community
    edition.

    You must agree to the [PGI End-User License Agreement](https://www.pgroup.com/doc/LICENSE.txt) to use this
    building block.

    As a side effect, a toolchain is created containing the PGI
    compilers.  The tool can be passed to other operations that want
    to build using the PGI compilers.

    # Parameters

    environment: Boolean flag to specify whether the environment
    (`LD_LIBRARY_PATH`, `PATH`, and potentially other variables)
    should be modified to include the PGI compiler. The default is
    True.

    eula: By setting this value to `True`, you agree to the [PGI End-User License Agreement](https://www.pgroup.com/doc/LICENSE.txt).
    The default value is `False`.

    extended_environment: Boolean flag to specify whether an extended
    set of environment variables should be defined.  If True, the
    following environment variables will be defined: `CC`, `CPP`,
    `CXX`, `F77`, `F90`, `FC`, and `MODULEPATH`.  In addition, if the
    PGI MPI component is selected then `PGI_OPTL_INCLUDE_DIRS` and
    `PGI_OPTL_LIB_DIRS` will also be defined and `PATH` and
    `LD_LIBRARY_PATH` will include the PGI MPI component.  If False,
    then only `PATH` and `LD_LIBRARY_PATH` will be extended to include
    the PGI compiler.  The default value is `False`.

    mpi: Boolean flag to specify whether the MPI component should be
    installed.  If True, MPI will be installed.  The default value is
    False.

    ospackages: List of OS packages to install prior to installing the
    PGI compiler.  For Ubuntu, the default values are `gcc`, `g++`,
    `libnuma1` and `perl`, and also `wget` (if downloading the PGI
    compiler rather than using a tarball in the local build context).
    For RHEL-based Linux distributions, the default values are `gcc`,
    `gcc-c++`, `numactl-libs` and `perl`, and also `wget` (if
    downloading the PGI compiler rather than using a tarball in the
    local build context).

    prefix: The top level install prefix.  The default value is
    `/opt/pgi`.

    system_cuda: Boolean flag to specify whether the PGI compiler
    should use the system CUDA.  If False, the version(s) of CUDA
    bundled with the PGI compiler will be installed.  The default
    value is False.

    tarball: Path to the PGI compiler tarball relative to the local
    build context.  The default value is empty.  If this is defined,
    the tarball in the local build context will be used rather than
    downloading the tarball from the web.

    version: The version of the PGI compiler to use.  Note this value
    is currently only used when setting the environment and does not
    control the version of the compiler downloaded.  The default value
    is `19.10`.

    # Examples

    ```python
    pgi(eula=True)
    ```

    ```python
    pgi(eula=True, tarball='pgilinux-2017-1710-x86_64.tar.gz')
    ```

    ```python
    p = pgi(eula=True)
    openmpi(..., toolchain=p.toolchain, ...)
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(pgi, self).__init__(**kwargs)

        self.__arch_directory = None # Filled in __cpu_arch()
        self.__arch_pkg = None # Filled in by __cpu_arch()
        self.__commands = [] # Filled in by __setup()
        self.__libnuma_path = '' # Filled in __distro()
        self.__runtime_commands = [] # Filled in by __setup()

        # By setting this value to True, you agree to the PGI End-User
        # License Agreement (https://www.pgroup.com/doc/LICENSE.txt)
        self.__eula = kwargs.get('eula', False)

        self.__extended_environment = kwargs.get('extended_environment', False)
        self.__fix_ownership = kwargs.get('fix_ownership', False)
        self.__mpi = kwargs.get('mpi', False)
        self.__ospackages = kwargs.get('ospackages', [])
        self.__runtime_ospackages = [] # Filled in by __distro()
        self.__prefix = kwargs.get('prefix', '/opt/pgi')
        self.__referer = r'https://www.pgroup.com/products/community.htm?utm_source=hpccm\&utm_medium=wgt\&utm_campaign=CE\&nvid=nv-int-14-39155'
        self.__system_cuda = kwargs.get('system_cuda', False)
        self.__system_libnuma = kwargs.get('system_libnuma', True)
        self.__tarball = kwargs.get('tarball', '')
        self.__url_template = 'https://www.pgroup.com/support/downloader.php?file=pgi-community-linux-{}'

        # The version is fragile since the latest version is
        # automatically downloaded, which may not match this default.
        self.__version = kwargs.get('version', '19.10')
        self.__wd = '/var/tmp' # working directory

        self.toolchain = toolchain(CC='pgcc', CXX='pgc++', F77='pgfortran',
                                   F90='pgfortran', FC='pgfortran')

        # Set the CPU architecture specific parameters
        self.__cpu_arch()

        # Set the Linux distribution specific parameters
        self.__distro()

        self.__basepath = posixpath.join(self.__prefix, self.__arch_directory)
        self.__basepath_llvm = posixpath.join(self.__prefix,
                                              '{}-llvm'.format(
                                                  self.__arch_directory))

        # Construct the series of steps to execute
        self.__setup()

        # Fill in container instructions
        self.__instructions()

    def __instructions(self):
        """Fill in container instructions"""

        self += comment('PGI compiler version {}'.format(self.__version))
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

        if hpccm.config.g_cpu_arch == cpu_arch.PPC64LE:
            self.__arch_directory = 'linuxpower'
            self.__arch_pkg = 'openpower'
        elif hpccm.config.g_cpu_arch == cpu_arch.X86_64:
            self.__arch_directory = 'linux86-64'
            self.__arch_pkg = 'x64'
        else: # pragma: no cover
            raise RuntimeError('Unknown CPU architecture')

    def __distro(self):
        """Based on the Linux distribution, set values accordingly.  A user
        specified value overrides any defaults."""

        if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
            if not self.__ospackages:
                self.__ospackages = ['gcc', 'g++', 'libnuma1', 'perl']
                if self.__mpi:
                    self.__ospackages.append('openssh-client')
            self.__runtime_ospackages = ['libnuma1']
            if self.__mpi:
                self.__runtime_ospackages.append('openssh-client')
            self.__libnuma_path = '/usr/lib/x86_64-linux-gnu'
        elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
            if not self.__ospackages:
                self.__ospackages = ['gcc', 'gcc-c++', 'numactl-libs', 'perl']
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

        pgi_path = posixpath.join(self.__basepath, self.__version)
        mpi_path = posixpath.join(pgi_path, 'mpi', 'openmpi')
        if LooseVersion(self.__version) >= LooseVersion('19.4'):
            mpi_path = posixpath.join(pgi_path, 'mpi', 'openmpi-3.1.3')

        if runtime:
            # Runtime environment
            if self.__mpi:
                # PGI MPI component is selected
                e['LD_LIBRARY_PATH'] = '{}:{}:$LD_LIBRARY_PATH'.format(
                    posixpath.join(mpi_path, 'lib'),
                    posixpath.join(pgi_path, 'lib'))
                e['PATH'] = '{}:$PATH'.format(
                    posixpath.join(mpi_path, 'bin'))
            else:
                # PGI MPI component is not selected
                e['LD_LIBRARY_PATH'] = '{}:$LD_LIBRARY_PATH'.format(
                    posixpath.join(pgi_path, 'lib'))
        else:
            # Development environment
            if self.__extended_environment:
                # Mirror the environment defined by the pgi environment module
                e = {'CC': posixpath.join(pgi_path, 'bin', 'pgcc'),
                     'CPP': '"{} -Mcpp"'.format(
                         posixpath.join(pgi_path, 'bin', 'pgcc')),
                     'CXX': posixpath.join(pgi_path, 'bin', 'pgc++'),
                     'F77': posixpath.join(pgi_path, 'bin', 'pgf77'),
                     'F90': posixpath.join(pgi_path, 'bin', 'pgf90'),
                     'FC': posixpath.join(pgi_path, 'bin', 'pgfortran'),
                     'MODULEPATH': '{}:$MODULEPATH'.format(
                         posixpath.join(self.__prefix, 'modulefiles'))}
                if self.__mpi:
                    # PGI MPI component is selected
                    e['LD_LIBRARY_PATH'] = '{}:{}:$LD_LIBRARY_PATH'.format(
                        posixpath.join(mpi_path, 'lib'),
                        posixpath.join(pgi_path, 'lib'))
                    e['PATH'] = '{}:{}:$PATH'.format(
                        posixpath.join(mpi_path, 'bin'),
                        posixpath.join(pgi_path, 'bin'))
                    e['PGI_OPTL_INCLUDE_DIRS'] = posixpath.join(
                        mpi_path, 'include')
                    e['PGI_OPTL_LIB_DIRS'] = posixpath.join(mpi_path, 'lib')
                else:
                    # PGI MPI component is not selected
                    e['LD_LIBRARY_PATH'] = '{}:$LD_LIBRARY_PATH'.format(
                        posixpath.join(pgi_path, 'lib'))
                    e['PATH'] = '{}:$PATH'.format(
                        posixpath.join(pgi_path, 'bin'))
            else:
                # Basic environment only
                if self.__mpi:
                    e['LD_LIBRARY_PATH'] = '{}:{}:$LD_LIBRARY_PATH'.format(
                        posixpath.join(mpi_path, 'lib'),
                        posixpath.join(pgi_path, 'lib'))
                    e['PATH'] = '{}:{}:$PATH'.format(
                        posixpath.join(mpi_path, 'bin'),
                        posixpath.join(pgi_path, 'bin'))
                else:
                    # PGI MPI component is not selected
                    e = {'PATH': '{}:$PATH'.format(posixpath.join(pgi_path,
                                                                'bin')),
                         'LD_LIBRARY_PATH': '{}:$LD_LIBRARY_PATH'.format(
                             posixpath.join(pgi_path, 'lib'))}

        return e

    def __setup(self):
        """Construct the series of shell commands, i.e., fill in
           self.__commands"""

        if self.__tarball:
            # Use tarball from local build context
            tarball = posixpath.basename(self.__tarball)

            # Figure out the version from the tarball name
            match = re.match(r'pgilinux-\d+-(?P<year>\d\d)0?(?P<month>[1-9][0-9]?)',
                             tarball)
            if match and match.groupdict()['year'] and match.groupdict()['month']:
                self.__version = '{0}.{1}'.format(match.groupdict()['year'],
                                                  match.groupdict()['month'])
        else:
            # The URL would normally result in a downloaded file with
            # the name 'downloader.php?file=pgi-community-linux-x64'.
            # Also, the version downloaded cannot be controlled, it
            # will always be the 'latest'.  Use a synthetic tarball
            # filename.
            tarball = 'pgi-community-linux-{}-latest.tar.gz'.format(
                self.__arch_pkg)

            self.__commands.append(self.download_step(
                url=self.__url_template.format(self.__arch_pkg),
                outfile=posixpath.join(self.__wd, tarball),
                referer=self.__referer, directory=self.__wd))

        self.__commands.append(self.untar_step(
            tarball=posixpath.join(self.__wd, tarball),
            directory=posixpath.join(self.__wd, 'pgi')))

        flags = {'PGI_ACCEPT_EULA': 'accept',
                 'PGI_INSTALL_DIR': self.__prefix,
                 'PGI_INSTALL_MPI': 'false',
                 'PGI_INSTALL_NVIDIA': 'true',
                 'PGI_MPI_GPU_SUPPORT': 'false',
                 'PGI_SILENT': 'true'}
        if not self.__eula:
            # This will fail when building the container
            logging.warning('PGI EULA was not accepted')
            flags['PGI_ACCEPT_EULA'] = 'decline'
            flags['PGI_SILENT'] = 'false'
        if self.__system_cuda:
            flags['PGI_INSTALL_NVIDIA'] = 'false'
        if self.__mpi:
            flags['PGI_INSTALL_MPI'] = 'true'
            flags['PGI_MPI_GPU_SUPPORT'] = 'true'
        flag_string = ' '.join('{0}={1}'.format(key, val)
                               for key, val in sorted(flags.items()))

        self.__commands.append('cd {0} && {1} ./install'.format(
            posixpath.join(self.__wd, 'pgi'), flag_string))

        # Create siterc to specify use of the system CUDA
        siterc = posixpath.join(self.__basepath, self.__version, 'bin', 'siterc')
        if self.__system_cuda:
            self.__commands.append('echo "set CUDAROOT=/usr/local/cuda;" >> {}'.format(siterc))

        # Create siterc to respect LIBRARY_PATH
        # https://www.pgroup.com/support/faq.htm#lib_path_ldflags
        self.__commands.append(r'echo "variable LIBRARY_PATH is environment(LIBRARY_PATH);" >> {}'.format(siterc))
        self.__commands.append(r'echo "variable library_path is default(\$if(\$LIBRARY_PATH,\$foreach(ll,\$replace(\$LIBRARY_PATH,":",), -L\$ll)));" >> {}'.format(siterc))
        self.__commands.append(r'echo "append LDLIBARGS=\$library_path;" >> {}'.format(siterc))

        # Override the installer behavior and force the use of the
        # system libnuma library
        if self.__system_libnuma:
            self.__commands.append('ln -sf {0} {1}'.format(
                posixpath.join(self.__libnuma_path, 'libnuma.so.1'),
                posixpath.join(self.__basepath, self.__version, 'lib',
                               'libnuma.so')))
            self.__commands.append('ln -sf {0} {1}'.format(
                posixpath.join(self.__libnuma_path, 'libnuma.so.1'),
                posixpath.join(self.__basepath, self.__version, 'lib',
                               'libnuma.so.1')))

        # Some installed files are owned by uid 921 / gid 1004.
        # Fix it so that all files are owned by root.
        if self.__fix_ownership:
            self.__commands.append('chown -R root.root {}'.format(
                self.__prefix))

        # Cleanup
        self.__commands.append(self.cleanup_step(
            items=[posixpath.join(self.__wd, tarball),
                   posixpath.join(self.__wd, 'pgi')]))

        # libnuma.so and libnuma.so.1 must be symlinks to the system
        # libnuma library.  They are originally symlinks, but Docker
        # "COPY -from" copies the file pointed to by the symlink,
        # converting them to files, so recreate the symlinks.
        self.__runtime_commands.append('ln -sf {0} {1}'.format(
            posixpath.join(self.__libnuma_path, 'libnuma.so.1'),
            posixpath.join(self.__basepath, self.__version, 'lib',
                           'libnuma.so')))
        self.__runtime_commands.append('ln -sf {0} {1}'.format(
            posixpath.join(self.__libnuma_path, 'libnuma.so.1'),
            posixpath.join(self.__basepath, self.__version, 'lib',
                           'libnuma.so.1')))

        # Set the environment
        self.environment_variables = self.__environment()
        self.runtime_environment_variables = self.__environment(runtime=True)

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples

        ```python
        p = pgi(...)
        Stage0 += p
        Stage1 += p.runtime()
        ```
        """
        instructions = []
        instructions.append(comment('PGI compiler'))

        if self.__runtime_ospackages:
            instructions.append(packages(ospackages=self.__runtime_ospackages))

        pgi_path = posixpath.join(self.__basepath, self.__version)
        src_path = pgi_path
        if (LooseVersion(self.__version) >= LooseVersion('19.4') and
            hpccm.config.g_cpu_arch == cpu_arch.X86_64):
            # Too many levels of symlinks for the Docker builder to
            # handle, so use the real path
            src_path = posixpath.join(self.__basepath_llvm, self.__version)
        instructions.append(copy(_from=_from,
                                 src=posixpath.join(src_path,
                                                    'REDIST', '*.so*'),
                                 dest=posixpath.join(pgi_path,
                                                     'lib', '')))

        # REDIST workaround for incorrect libcudaforwrapblas.so
        # symlink
        if (LooseVersion(self.__version) >= LooseVersion('18.10') and
            LooseVersion(self.__version) < LooseVersion('19.10') and
            hpccm.config.g_cpu_arch == cpu_arch.X86_64):
            instructions.append(
                copy(_from=_from,
                     src=posixpath.join(pgi_path, 'lib',
                                        'libcudaforwrapblas.so'),
                     dest=posixpath.join(pgi_path, 'lib',
                                         'libcudaforwrapblas.so')))

        if self.__mpi:
            mpi_path = posixpath.join(pgi_path, 'mpi', 'openmpi')
            if LooseVersion(self.__version) >= LooseVersion('19.4'):
                mpi_path = posixpath.join(pgi_path, 'mpi', 'openmpi-3.1.3')
            instructions.append(copy(_from=_from,
                                     src=mpi_path, dest=mpi_path))

        if self.__runtime_commands:
            instructions.append(shell(commands=self.__runtime_commands))

        instructions.append(environment(variables=self.environment_step(
            runtime=True)))
        return '\n'.join(str(x) for x in instructions)
