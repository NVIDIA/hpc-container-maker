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

"""MPICH building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import posixpath
import re
from six import string_types

import hpccm.config
import hpccm.templates.ConfigureMake
import hpccm.templates.envvars
import hpccm.templates.ldconfig
import hpccm.templates.rm
import hpccm.templates.tar
import hpccm.templates.wget

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.packages import packages
from hpccm.common import linux_distro
from hpccm.primitives.comment import comment
from hpccm.primitives.copy import copy
from hpccm.primitives.environment import environment
from hpccm.primitives.shell import shell
from hpccm.toolchain import toolchain

class mpich(bb_base, hpccm.templates.ConfigureMake, hpccm.templates.envvars,
            hpccm.templates.ldconfig, hpccm.templates.rm, hpccm.templates.tar,
            hpccm.templates.wget):
    """The `mpich` building block configures, builds, and installs the
    [MPICH](https://www.mpich.org) component.

    As a side effect, a toolchain is created containing the MPI
    compiler wrappers.  The tool can be passed to other operations
    that want to build using the MPI compiler wrappers.

    # Parameters

    check: Boolean flag to specify whether the `make check` and `make
    testing` steps should be performed.  The default is False.

    configure_opts: List of options to pass to `configure`.  The
    default is an empty list.

    environment: Boolean flag to specify whether the environment
    (`LD_LIBRARY_PATH` and `PATH`) should be modified to include
    MPICH. The default is True.

    ldconfig: Boolean flag to specify whether the MPICH library
    directory should be added dynamic linker cache.  If False, then
    `LD_LIBRARY_PATH` is modified to include the MPICH library
    directory. The default value is False.

    ospackages: List of OS packages to install prior to configuring
    and building.  For Ubuntu, the default values are `file`, `gzip`,
    `make`, `openssh-client`, `perl`, `tar`, and `wget`.  For
    RHEL-based Linux distributions, the default values are `file`,
    `gzip`, `make`, `openssh-clients`, `perl`, `tar`, and `wget`.

    prefix: The top level install location.  The default value is
    `/usr/local/mpich`.

    toolchain: The toolchain object.  This should be used if
    non-default compilers or other toolchain options are needed.  The
    default is empty.

    version: The version of MPICH source to download.  The default
    value is `3.3.1`.

    # Examples

    ```python
    mpich(prefix='/opt/mpich/3.3', version='3.3')
    ```

    ```python
    p = pgi(eula=True)
    mpich(toolchain=p.toolchain)
    ```
    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(mpich, self).__init__(**kwargs)

        self.__baseurl = kwargs.get('baseurl',
                                    'https://www.mpich.org/static/downloads')
        self.__check = kwargs.get('check', False)
        self.configure_opts = kwargs.get('configure_opts', [])
        self.__ospackages = kwargs.get('ospackages', [])
        self.prefix = kwargs.get('prefix', '/usr/local/mpich')
        self.__runtime_ospackages = [] # Filled in by __distro()
        # Input toolchain, i.e., what to use when building
        self.__toolchain = kwargs.get('toolchain', toolchain())
        # MPICH does not accept F90
        self.toolchain_control = {'CC': True, 'CXX': True, 'F77': True,
                                  'F90': False, 'FC': True}
        self.version = kwargs.get('version', '3.3.1')

        self.__commands = [] # Filled in by __setup()
        self.__wd = '/var/tmp' # working directory

        # Output toolchain
        self.toolchain = toolchain(CC='mpicc', CXX='mpicxx', F77='mpif77',
                                   F90='mpif90', FC='mpifort')

        # Set the Linux distribution specific parameters
        self.__distro()

        # Construct the series of steps to execute
        self.__setup()

        # Fill in container instructions
        self.__instructions()

    def __instructions(self):
        """Fill in container instructions"""

        self += comment('MPICH version {}'.format(self.version))
        self += packages(ospackages=self.__ospackages)
        self += shell(commands=self.__commands)
        self += environment(variables=self.environment_step())

    def __distro(self):
        """Based on the Linux distribution, set values accordingly.  A user
        specified value overrides any defaults."""

        if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
            if not self.__ospackages:
                self.__ospackages = ['file', 'gzip', 'make', 'openssh-client',
                                     'perl', 'tar', 'wget']
            self.__runtime_ospackages = ['openssh-client']
        elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
            if not self.__ospackages:
                self.__ospackages = ['file', 'gzip', 'make',
                                     'openssh-clients', 'perl', 'tar', 'wget']
            self.__runtime_ospackages = ['openssh-clients']
        else: # pragma: no cover
            raise RuntimeError('Unknown Linux distribution')

    def __setup(self):
        """Construct the series of shell commands, i.e., fill in
           self.__commands"""

        build_environment = []

        tarball = 'mpich-{}.tar.gz'.format(self.version)
        url = '{0}/{1}/{2}'.format(self.__baseurl, self.version, tarball)

        # Workaround issue with the PGI compiler
        # https://lists.mpich.org/pipermail/discuss/2017-July/005235.html
        if self.__toolchain.CC and re.match('.*pgcc', self.__toolchain.CC):
            self.configure_opts.append('--disable-fast')

        # Download source from web
        self.__commands.append(self.download_step(url=url,
                                                  directory=self.__wd))
        self.__commands.append(self.untar_step(
            tarball=posixpath.join(self.__wd, tarball), directory=self.__wd))

        # Configure
        self.__commands.append(self.configure_step(
            directory=posixpath.join(self.__wd,
                                     'mpich-{}'.format(self.version)),
            environment=build_environment,
            toolchain=self.__toolchain))

        # Build
        self.__commands.append(self.build_step())

        # Check
        if self.__check:
            self.__commands.append(self.check_step())

        # Install
        self.__commands.append(self.install_step())

        # Run test suite (must be after install)
        if self.__check:
            self.__commands.append('RUNTESTS_SHOWPROGRESS=1 make testing')

        # Set library path
        libpath = posixpath.join(self.prefix, 'lib')
        if self.ldconfig:
            self.__commands.append(self.ldcache_step(directory=libpath))
        else:
            self.environment_variables['LD_LIBRARY_PATH'] = '{}:$LD_LIBRARY_PATH'.format(libpath)

        # Cleanup
        self.__commands.append(self.cleanup_step(
            items=[posixpath.join(self.__wd, tarball),
                   posixpath.join(self.__wd,
                                  'mpich-{}'.format(self.version))]))

        # Set the environment
        self.environment_variables['PATH'] = '{}:$PATH'.format(
            posixpath.join(self.prefix, 'bin'))

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples
        ```python
        m = mpich(...)
        Stage0 += m
        Stage1 += m.runtime()
        ```
        """
        instructions = []
        instructions.append(comment('MPICH'))
        instructions.append(packages(ospackages=self.__runtime_ospackages))
        instructions.append(copy(_from=_from, src=self.prefix,
                                 dest=self.prefix))
        if self.ldconfig:
            instructions.append(shell(
                commands=[self.ldcache_step(
                    directory=posixpath.join(self.prefix, 'lib'))]))
        instructions.append(environment(variables=self.environment_step()))
        return '\n'.join(str(x) for x in instructions)
