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

import logging # pylint: disable=unused-import
import re
import os

import hpccm.config

from hpccm.building_blocks.packages import packages
from hpccm.common import linux_distro
from hpccm.primitives.comment import comment
from hpccm.primitives.copy import copy
from hpccm.primitives.environment import environment
from hpccm.primitives.shell import shell
from hpccm.templates.rm import rm
from hpccm.templates.tar import tar
from hpccm.templates.wget import wget
from hpccm.toolchain import toolchain

class pgi(rm, tar, wget):
    """The `pgi` building block downloads and installs the PGI compiler.
    Currently, the only option is to install the latest community
    edition.

    You must agree to the [PGI End-User License Agreement](https://www.pgroup.com/doc/LICENSE.txt) to use this
    building block.

    As a side effect, this building block modifies `PATH` and
    `LD_LIBRARY_PATH` to include the PGI compiler.

    As a side effect, a toolchain is created containing the PGI
    compilers.  The tool can be passed to other operations that want
    to build using the PGI compilers.

    # Parameters

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
    is `18.10`.

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

        # Trouble getting MRO with kwargs working correctly, so just call
        # the parent class constructors manually for now.
        #super(pgi, self).__init__(**kwargs)
        rm.__init__(self, **kwargs)
        tar.__init__(self, **kwargs)
        wget.__init__(self, **kwargs)

        self.__commands = [] # Filled in by __setup()
        self.__runtime_commands = [] # Filled in by __setup()

        # By setting this value to True, you agree to the PGI End-User
        # License Agreement (https://www.pgroup.com/doc/LICENSE.txt)
        self.__eula = kwargs.get('eula', False)

        self.__extended_environment = kwargs.get('extended_environment', False)
        self.__mpi = kwargs.get('mpi', False)
        self.__ospackages = kwargs.get('ospackages', [])
        self.__runtime_ospackages = [] # Filled in by __distro()
        self.__prefix = kwargs.get('prefix', '/opt/pgi')
        self.__referer = r'https://www.pgroup.com/products/community.htm?utm_source=hpccm\&utm_medium=wgt\&utm_campaign=CE\&nvid=nv-int-14-39155'
        self.__system_cuda = kwargs.get('system_cuda', False)
        self.__tarball = kwargs.get('tarball', '')
        self.__url = 'https://www.pgroup.com/support/downloader.php?file=pgi-community-linux-x64'

        # The version is fragile since the latest version is
        # automatically downloaded, which may not match this default.
        self.__version = kwargs.get('version', '18.10')
        self.__wd = '/var/tmp' # working directory

        self.__basepath = os.path.join(self.__prefix, 'linux86-64')

        self.toolchain = toolchain(CC='pgcc', CXX='pgc++', F77='pgfortran',
                                   F90='pgfortran', FC='pgfortran')

        # Set the Linux distribution specific parameters
        self.__distro()

        # Construct the series of steps to execute
        self.__setup()

    def __str__(self):
        """String representation of the building block"""

        instructions = []
        instructions.append(comment(
            'PGI compiler version {}'.format(self.__version)))
        if self.__tarball:
            # Use tarball from local build context
            instructions.append(
                copy(src=self.__tarball,
                     dest=os.path.join(self.__wd,
                                       os.path.basename(self.__tarball))))
        else:
            # Downloading, so need wget
            self.__ospackages.append('wget')

        if self.__ospackages:
            instructions.append(packages(ospackages=self.__ospackages))

        instructions.append(shell(commands=self.__commands))

        instructions.append(environment(variables=self.__environment()))

        return '\n'.join(str(x) for x in instructions)

    def __distro(self):
        """Based on the Linux distribution, set values accordingly.  A user
        specified value overrides any defaults."""

        if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
            if not self.__ospackages:
                self.__ospackages = ['gcc', 'g++', 'libnuma1', 'perl']
                self.__runtime_ospackages = ['libnuma1']
        elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
            if not self.__ospackages:
                self.__ospackages = ['gcc', 'gcc-c++', 'numactl-libs', 'perl']
                self.__runtime_ospackages = ['numactl-libs']
        else:
            raise RuntimeError('Unknown Linux distribution')

    def __environment(self, runtime=False):
        """Define environment variables"""
        e = {}

        pgi_path = os.path.join(self.__basepath, self.__version)
        mpi_path = os.path.join(pgi_path, 'mpi', 'openmpi')

        if runtime:
            # Runtime environment
            e = {'LD_LIBRARY_PATH': '{}:$LD_LIBRARY_PATH'.format(
                os.path.join(pgi_path, 'lib'))}
        else:
            # Development environment
            if self.__extended_environment:
                # Mirror the environment defined by the pgi environment module
                e = {'CC': os.path.join(pgi_path, 'bin', 'pgcc'),
                     'CPP': '"{} -Mcpp"'.format(
                         os.path.join(pgi_path, 'bin', 'pgcc')),
                     'CXX': os.path.join(pgi_path, 'bin', 'pgc++'),
                     'F77': os.path.join(pgi_path, 'bin', 'pgf77'),
                     'F90': os.path.join(pgi_path, 'bin', 'pgf90'),
                     'FC': os.path.join(pgi_path, 'bin', 'pgfortran'),
                     'MODULEPATH': '{}:$MODULEPATH'.format(
                         os.path.join(self.__prefix, 'modulefiles'))}
                if self.__mpi:
                    # PGI MPI component is selected
                    e['LD_LIBRARY_PATH'] = '{}:{}:$LD_LIBRARY_PATH'.format(
                        os.path.join(mpi_path, 'lib'),
                        os.path.join(pgi_path, 'lib'))
                    e['PATH'] = '{}:{}:$PATH'.format(
                        os.path.join(mpi_path, 'bin'),
                        os.path.join(pgi_path, 'bin'))
                    e['PGI_OPTL_INCLUDE_DIRS'] = os.path.join(
                        mpi_path, 'include')
                    e['PGI_OPTL_LIB_DIRS'] = os.path.join(mpi_path, 'lib')
                else:
                    # PGI MPI component is not selected
                    e['LD_LIBRARY_PATH'] = '{}:$LD_LIBRARY_PATH'.format(
                        os.path.join(pgi_path, 'lib'))
                    e['PATH'] = '{}:$PATH'.format(
                        os.path.join(pgi_path, 'bin'))
            else:
                # Basic environment only
                e = {'PATH': '{}:$PATH'.format(os.path.join(pgi_path, 'bin')),
                     'LD_LIBRARY_PATH': '{}:$LD_LIBRARY_PATH'.format(
                         os.path.join(pgi_path, 'lib'))}

        return e

    def __setup(self):
        """Construct the series of shell commands, i.e., fill in
           self.__commands"""

        if self.__tarball:
            # Use tarball from local build context
            tarball = os.path.basename(self.__tarball)

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
            tarball = 'pgi-community-linux-x64-latest.tar.gz'

            self.__commands.append(self.download_step(
                url=self.__url, outfile=os.path.join(self.__wd, tarball),
                referer=self.__referer, directory=self.__wd))

        self.__commands.append(self.untar_step(
            tarball=os.path.join(self.__wd, tarball),
            directory=os.path.join(self.__wd, 'pgi')))

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
            os.path.join(self.__wd, 'pgi'), flag_string))

        # Create siterc to specify use of the system CUDA
        siterc = os.path.join(self.__basepath, self.__version, 'bin', 'siterc')
        if self.__system_cuda:
            self.__commands.append('echo "set CUDAROOT=/usr/local/cuda;" >> {}'.format(siterc))

        # Create siterc to respect LIBRARY_PATH
        # https://www.pgroup.com/support/faq.htm#lib_path_ldflags
        self.__commands.append(r'echo "variable LIBRARY_PATH is environment(LIBRARY_PATH);" >> {}'.format(siterc))
        self.__commands.append(r'echo "variable library_path is default(\$if(\$LIBRARY_PATH,\$foreach(ll,\$replace(\$LIBRARY_PATH,":",), -L\$ll)));" >> {}'.format(siterc))
        self.__commands.append(r'echo "append LDLIBARGS=\$library_path;" >> {}'.format(siterc))

        self.__commands.append(self.cleanup_step(
            items=[os.path.join(self.__wd, tarball),
                   os.path.join(self.__wd, 'pgi')]))

        # Runtime workaround for libnuma issue impacting version 18.4
        # on Ubuntu
        if (self.__version == '18.4' and
            hpccm.config.g_linux_distro == linux_distro.UBUNTU):
            self.__runtime_commands.append('ln -s {0} {1}'.format(
                '/usr/lib/x86_64-linux-gnu/libnuma.so.1',
                os.path.join(self.__basepath, self.__version, 'lib',
                             'libnuma.so')))


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
        instructions.append(copy(_from=_from,
                                 src=os.path.join(self.__basepath,
                                                  self.__version,
                                                  'REDIST', '*.so'),
                                 dest=os.path.join(self.__basepath,
                                                   self.__version,
                                                   'lib', '')))
        if self.__runtime_commands:
            instructions.append(shell(commands=self.__runtime_commands))

        instructions.append(environment(
            variables=self.__environment(runtime=True)))
        return '\n'.join(str(x) for x in instructions)
