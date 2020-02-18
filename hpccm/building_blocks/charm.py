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

"""Charm++ building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from distutils.version import LooseVersion
import posixpath

import hpccm.config
import hpccm.templates.envvars
import hpccm.templates.ldconfig
import hpccm.templates.rm
import hpccm.templates.sed
import hpccm.templates.tar
import hpccm.templates.wget

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.packages import packages
from hpccm.common import cpu_arch
from hpccm.primitives.comment import comment
from hpccm.primitives.copy import copy
from hpccm.primitives.environment import environment
from hpccm.primitives.shell import shell

class charm(bb_base, hpccm.templates.envvars, hpccm.templates.ldconfig,
            hpccm.templates.rm, hpccm.templates.sed, hpccm.templates.tar,
            hpccm.templates.wget):
    """The `charm` building block downloads and install the
    [Charm++](http://charm.cs.illinois.edu/research/charm) component.

    # Parameters

    basedir: List of additional include and library paths for building
    Charm++.  The default is an empty list.

    check: Boolean flag to specify whether the test cases should be
    run.  The default is False.

    environment: Boolean flag to specify whether the environment
    (`LD_LIBRARY_PATH`, `PATH`, and other variables) should be
    modified to include Charm++. The default is True.

    ldconfig: Boolean flag to specify whether the Charm++ library
    directory should be added dynamic linker cache.  If False, then
    `LD_LIBRARY_PATH` is modified to include the Charm++ library
    directory. The default value is False.

    options: List of additional options to use when building Charm++.
    The default values are `--build-shared`, and `--with-production`.

    ospackages: List of OS packages to install prior to configuring
    and building.  The default values are `autoconf`, `automake`,
    `git`, `libtool`, `make`, and `wget`.

    prefix: The top level install prefix.  The default value is
    `/usr/local`.

    target: The target Charm++ framework to build.  The default value
    is `charm++`.

    target_architecture: The target machine architecture to build.
    For x86_64 processors, the default value is
    `multicore-linux-x86_64`.  For aarch64 processors, the default
    value is `multicore-arm8`.  For ppc64le processors, the default is
    `multicore-linux-ppc64le`.

    version: The version of Charm++ to download.  The default value is
    `6.9.0`.

    # Examples

    ```python
    charm(prefix='/opt', version='6.8.2')
    ```

    ```python
    charm(target_architecture='mpi-linux-x86_64')
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(charm, self).__init__(**kwargs)

        self.__basedir = kwargs.get('basedir', [])
        self.__baseurl = kwargs.get('baseurl',
                                    'https://github.com/UIUC-PPL/charm/archive')
        self.__check = kwargs.get('check', False)
        self.__options = kwargs.get('options', ['--build-shared',
                                                '--with-production'])
        self.__ospackages = kwargs.get('ospackages',
                                       ['autoconf', 'automake', 'git',
                                        'libtool', 'make', 'wget'])
        self.__parallel = kwargs.get('parallel', '$(nproc)')
        self.__prefix = kwargs.get('prefix', '/usr/local')
        self.__target = kwargs.get('target', 'charm++')
        self.__target_architecture = kwargs.get('target_architecture', '')
        self.__version = kwargs.get('version', '6.9.0')

        # Version 6.9.0 dropped the 'v' from directory name
        if LooseVersion(self.__version) >= LooseVersion('6.9.0'):
            self.__installdir = posixpath.join(
                self.__prefix, 'charm-{}'.format(self.__version))
        else:
            self.__installdir = posixpath.join(
                self.__prefix, 'charm-v{}'.format(self.__version))

        self.__wd = '/var/tmp' # working directory

        self.__commands = [] # Filled in by __setup()

        # Set the CPU architecture specific parameters
        self.__cpu_arch()

        # Construct series of steps to execute
        self.__setup()

        # Fill in container instructions
        self.__instructions()

    def __instructions(self):
        """Fill in container instructions"""

        self += comment('Charm++ version {}'.format(self.__version))
        self += packages(ospackages=self.__ospackages)
        self += shell(commands=self.__commands)
        self += environment(variables=self.environment_step())

    def __cpu_arch(self):
        """Based on the CPU architecture, set values accordingly.  A user
        specified value overrides any defaults."""

        if hpccm.config.g_cpu_arch == cpu_arch.AARCH64:
            if not self.__target_architecture:
                self.__target_architecture = 'multicore-arm8'
        elif hpccm.config.g_cpu_arch == cpu_arch.PPC64LE:
            if not self.__target_architecture:
                self.__target_architecture = 'multicore-linux-ppc64le'
        elif hpccm.config.g_cpu_arch == cpu_arch.X86_64:
            if not self.__target_architecture:
                self.__target_architecture = 'multicore-linux-x86_64'
        else: # pragma: no cover
            raise RuntimeError('Unknown CPU architecture')

    def __setup(self):
        """Construct the series of shell commands, i.e., fill in
           self.__commands"""

        tarball = 'v{}.tar.gz'.format(self.__version)
        url = '{0}/{1}'.format(self.__baseurl, tarball)

        # Download source from web
        self.__commands.append(self.download_step(url=url, directory=self.__wd))

        # Charm++ does not install nicely into a separate directory,
        # even with "--destination".  So just untar it into the
        # destination directory prefix.
        self.__commands.append(self.untar_step(
            tarball=posixpath.join(self.__wd, tarball),
            directory=self.__prefix))

        # Charm++ is hard-coded to use pgCC rather than pgc++ when the
        # PGI compiler is selected.  Replace pgCC with pgc++.
        # But... PGI is not really supported by Charm++:
        # https://charm.cs.illinois.edu/redmine/issues/234
        if 'pgcc' in self.__options:
            self.__commands.append(
                self.sed_step(
                    file=posixpath.join(self.__installdir, 'src', 'arch',
                                        'common', 'cc-pgcc.sh'),
                    patterns=[r's/pgCC/pgc++/g']))

        # Construct options string
        options = []
        if self.__options:
            options.extend(self.__options)
        if self.__basedir:
            options.extend(['--basedir={}'.format(x) for x in self.__basedir])

        # Build
        self.__commands.append('cd {} && ./build {} {} {} -j{}'.format(
            self.__installdir, self.__target, self.__target_architecture,
            ' '.join(options), self.__parallel))

        # Set library path
        libpath = posixpath.join(self.__installdir, 'lib_so')
        if self.ldconfig:
            self.__commands.append(self.ldcache_step(directory=libpath))
        else:
            self.environment_variables['LD_LIBRARY_PATH'] = '{}:$LD_LIBRARY_PATH'.format(libpath)

        # Check the build
        if self.__check:
            self.__commands.append('cd {} && make test'.format(
                posixpath.join(self.__installdir, 'tests', 'charm++')))

        # Cleanup tarball and directory
        self.__commands.append(self.cleanup_step(
            items=[posixpath.join(self.__wd, tarball)]))

        # Set the environment
        self.environment_variables['CHARMBASE'] = self.__installdir
        self.environment_variables['PATH'] = '{}:$PATH'.format(
            posixpath.join(self.__installdir, 'bin'))

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Example

        ```python
        c = charm(...)
        Stage0 += c
        Stage1 += c.runtime()
        ```
        """
        instructions = []
        instructions.append(comment('Charm++'))
        instructions.append(copy(_from=_from, src=self.__installdir,
                                 dest=self.__installdir))
        if self.ldconfig:
            instructions.append(shell(
                commands=[self.ldcache_step(
                    directory=posixpath.join(self.__prefix, 'lib_so'))]))
        instructions.append(environment(variables=self.environment_step()))
        return '\n'.join(str(x) for x in instructions)
