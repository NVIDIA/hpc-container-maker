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

"""CMake building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import posixpath
import re

import hpccm.config
import hpccm.templates.rm
import hpccm.templates.tar
import hpccm.templates.wget

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.packages import packages
from hpccm.common import cpu_arch, linux_distro
from distutils.version import LooseVersion
from hpccm.primitives.comment import comment
from hpccm.primitives.shell import shell
from hpccm.primitives.environment import environment

class cmake(bb_base, hpccm.templates.rm, hpccm.templates.tar,
            hpccm.templates.wget):
    """The `cmake` building block downloads and installs the
    [CMake](https://cmake.org) component.

    # Parameters

    bootstrap_opts: List of options to pass to `bootstrap` when
    building from source.  The default is an empty list.

    eula: By setting this value to `True`, you agree to the [CMake End-User License Agreement](https://gitlab.kitware.com/cmake/cmake/raw/master/Copyright.txt).
    The default value is `False`.

    ospackages: List of OS packages to install prior to installing.
    The default values are `make` and `wget`.

    prefix: The top level install location.  The default value is
    `/usr/local`.

    source: Boolean flag to specify whether to build CMake from
    source.  If True, includes the `libssl-dev` package in the list of
    OS packages for Ubuntu, and `openssl-devel` for RHEL-based
    distributions.  For x86_64 processors, the default is False, i.e.,
    use the available pre-compiled package.  For all other processors,
    the default is True.

    version: The version of CMake to download.  The default value is
    `3.22.2`.

    # Examples

    ```python
    cmake(eula=True)
    ```

    ```python
    cmake(eula=True, version='3.10.3')
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(cmake, self).__init__(**kwargs)

        self.__baseurl = kwargs.get('baseurl', 'https://github.com/Kitware/CMake/releases/download')
        self.__bootstrap_opts = kwargs.get('bootstrap_opts', [])

        # By setting this value to True, you agree to the CMake
        # End-User License Agreement
        # (https://gitlab.kitware.com/cmake/cmake/raw/master/Copyright.txt)
        self.__eula = kwargs.get('eula', False)

        self.__ospackages = kwargs.get('ospackages', ['make', 'wget'])
        self.__parallel = kwargs.get('parallel', '$(nproc)')
        self.__prefix = kwargs.get('prefix', '/usr/local')
        self.__source = kwargs.get('source', False)
        self.__version = kwargs.get('version', '3.22.2')

        self.__commands = [] # Filled in by __setup()
        self.__wd = kwargs.get('wd', hpccm.config.g_wd) # working directory

        # Construct the series of steps to execute
        self.__setup()

        # Fill in container instructions
        self.__instructions()

    def __instructions(self):
        """Fill in container instructions"""

        self += comment('CMake version {}'.format(self.__version))
        self += packages(ospackages=self.__ospackages)
        self += shell(commands=self.__commands)
        self += environment(variables={'PATH': '{}:$PATH'.format(
            posixpath.join(self.__prefix, 'bin'))})

    def __setup(self):
        """Construct the series of shell commands, i.e., fill in
           self.__commands"""
        if not self.__source and hpccm.config.g_cpu_arch == cpu_arch.X86_64:
            # Use the pre-compiled x86_64 binary
            self.__binary()
        else:
            # Build from source
            self.__build()

    def __binary(self):
        """Install the pre-compiled binary"""

        runfile = 'cmake-{}-linux-x86_64.sh'
        if LooseVersion(self.__version) < LooseVersion('3.20'):
            runfile = 'cmake-{}-Linux-x86_64.sh'

        runfile = runfile.format(self.__version)
        if LooseVersion(self.__version) < LooseVersion('3.1'):
            runfile = 'cmake-{}-Linux-i386.sh'.format(self.__version)
            # CMake releases of versions < 3.1 are only include 32-bit
            # binaries:
            if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
                self.__ospackages.append('libc6-i386')
            elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
                self.__ospackages.append('glibc.i686')
            else: # pragma: no cover
                raise RuntimeError('Unknown Linux distribution')

        url = '{0}/v{1}/{2}'.format(self.__baseurl, self.__version, runfile)

        # Download source from web
        self.__commands.append(self.download_step(url=url, directory=self.__wd))

        self.__commands.append('mkdir -p {}'.format(self.__prefix))
        # Run the runfile
        if self.__eula:
            self.__commands.append(
                '/bin/sh {0} --prefix={1} --skip-license'.format(
                    posixpath.join(self.__wd, runfile), self.__prefix))
        else:
            # This will fail when building the container
            logging.warning('CMake EULA was not accepted')
            self.__commands.append(
                '/bin/sh {0} --prefix={1}'.format(
                    posixpath.join(self.__wd, runfile), self.__prefix))
                    
        # Cleanup runfile
        self.__commands.append(self.cleanup_step(
            items=[posixpath.join(self.__wd, runfile)]))

    def __build(self):
        """Build from source"""

        tarball = 'cmake-{}.tar.gz'.format(self.__version)
        url = '{0}/v{1}/{2}'.format(self.__baseurl, self.__version, tarball)

        # Include SSL packages
        if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
            self.__ospackages.append('libssl-dev')
        elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
            self.__ospackages.append('openssl-devel')
        else: # pragma: no cover
            raise RuntimeError('Unknown Linux distribution')

        # Download source from web
        self.__commands.append(self.download_step(url=url, directory=self.__wd))
        self.__commands.append(self.untar_step(
            tarball=posixpath.join(self.__wd, tarball), directory=self.__wd))

        # Build and install
        if not self.__bootstrap_opts:
            self.__bootstrap_opts.append(
                '--parallel={}'.format(self.__parallel))
        self.__commands.append('cd {} && ./bootstrap --prefix={} {}'.format(
            posixpath.join(self.__wd, 'cmake-{}'.format(self.__version)),
            self.__prefix,
            ' '.join(self.__bootstrap_opts)))
        self.__commands.append('make -j{}'.format(self.__parallel))
        self.__commands.append('make install')

        # Cleanup tarball and directory
        self.__commands.append(self.cleanup_step(
            items=[posixpath.join(self.__wd, tarball),
                   posixpath.join(self.__wd,
                                  'cmake-{}'.format(self.__version))]))
