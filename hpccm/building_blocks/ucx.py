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

"""UCX building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from six import string_types

import logging # pylint: disable=unused-import
import os

import hpccm.config

from hpccm.building_blocks.packages import packages
from hpccm.common import linux_distro
from hpccm.primitives.comment import comment
from hpccm.primitives.copy import copy
from hpccm.primitives.environment import environment
from hpccm.primitives.shell import shell
from hpccm.templates.ConfigureMake import ConfigureMake
from hpccm.templates.rm import rm
from hpccm.templates.tar import tar
from hpccm.templates.wget import wget
from hpccm.toolchain import toolchain

class ucx(ConfigureMake, rm, tar, wget):
    """The `ucx` building block configures, builds, and installs the
    [UCX](https://github.com/openucx/ucx) component.

    An InfiniBand building block ([OFED](#ofed) or [Mellanox
    OFED](#mlnx_ofed)) should be installed prior to this building
    block.  One or all of the [gdrcopy](#gdrcopy), [KNEM](#knem), and
    [XPMEM](#xpmem) building blocks should also be installed prior to
    this building block.

    As a side effect, this building block modifies `PATH` and
    `LD_LIBRARY_PATH` to include the UCX build.

    # Parameters

    configure_opts: List of options to pass to `configure`.  The
    default values are `--enable-optimizations`, `--disable-logging`,
    `--disable-debug`, `--disable-assertions`,
    `--disable-params-check`, and `--disable-doxygen-doc`.

    cuda: Flag to control whether a CUDA aware build is performed.  If
    True, adds `--with-cuda=/usr/local/cuda` to the list of
    `configure` options.  If a string, uses the value of the string as
    the CUDA path.  If the toolchain specifies `CUDA_HOME`, then that
    path is used.  If False, adds `--without-cuda` to the list of
    `configure` options.  The default value is an empty string.

    gdrcopy: Flag to control whether gdrcopy is used by the build.  If
    True, adds `--with-gdrcopy` to the list of `configure` options.
    If a string, uses the value of the string as the gdrcopy path,
    e.g., `--with-gdrcopy=/path/to/gdrcopy`.  If False, adds
    `--without-gdrcopy` to the list of `configure` options.  The
    default is an empty string, i.e., include neither `--with-gdrcopy`
    not `--without-gdrcopy` and let `configure` try to automatically
    detect whether gdrcopy is present or not.

    knem: Flag to control whether KNEM is used by the build.  If True,
    adds `--with-knem` to the list of `configure` options.  If a
    string, uses the value of the string as the KNEM path, e.g.,
    `--with-knem=/path/to/knem`.  If False, adds `--without-knem` to
    the list of `configure` options.  The default is an empty string,
    i.e., include neither `--with-knem` not `--without-knem` and let
    `configure` try to automatically detect whether KNEM is present or
    not.

    ospackages: List of OS packages to install prior to configuring
    and building.  For Ubuntu, the default values are `binutils-dev`,
    `file`, `libnuma-dev`, `make`, and `wget`. For RHEL-based Linux
    distributions, the default values are `binutils-devel`, `file`,
    `make`, `numactl-devel`, and `wget`.

    prefix: The top level install location.  The default value is
    `/usr/local/ucx`.

    toolchain: The toolchain object.  This should be used if
    non-default compilers or other toolchain options are needed.  The
    default value is empty.

    version: The version of UCX source to download.  The default value
    is `1.4.0`.

    xpmem: Flag to control whether XPMEM is used by the build.  If
    True, adds `--with-xpmem` to the list of `configure` options.  If
    a string, uses the value of the string as the XPMEM path, e.g.,
    `--with-xpmem=/path/to/xpmem`.  If False, adds `--without-xpmem`
    to the list of `configure` options.  The default is an empty
    string, i.e., include neither `--with-xpmem` not `--without-xpmem`
    and let `configure` try to automatically detect whether XPMEM is
    present or not.

    # Examples

    ```python
    ucx(cuda=False, prefix='/opt/ucx/1.4.0', version='1.4.0')
    ```

    ```python
    ucx(cuda='/usr/local/cuda', gdrcopy='/usr/local/gdrcopy',
        knem='/usr/local/knem', xpmem='/usr/local/xpmem')
    ```
    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        # Trouble getting MRO with kwargs working correctly, so just call
        # the parent class constructors manually for now.
        #super(ucx, self).__init__(**kwargs)
        ConfigureMake.__init__(self, **kwargs)
        tar.__init__(self, **kwargs)
        rm.__init__(self, **kwargs)
        wget.__init__(self, **kwargs)

        self.configure_opts = kwargs.get('configure_opts',
                                         ['--enable-optimizations',
                                          '--disable-logging',
                                          '--disable-debug',
                                          '--disable-assertions',
                                          '--disable-params-check',
                                          '--disable-doxygen-doc'])
        self.prefix = kwargs.get('prefix', '/usr/local/ucx')

        self.__baseurl = kwargs.get('baseurl', 'https://github.com/openucx/ucx/releases/download')
        self.__cuda = kwargs.get('cuda', True)
        self.__gdrcopy = kwargs.get('gdrcopy', '')
        self.__knem = kwargs.get('knem', '')
        self.__ospackages = kwargs.get('ospackages', [])
        self.__toolchain = kwargs.get('toolchain', toolchain())
        self.__version = kwargs.get('version', '1.4.0')
        self.__xpmem = kwargs.get('xpmem', '')

        self.__commands = [] # Filled in by __setup()
        self.__environment_variables = {
            'LD_LIBRARY_PATH':
            '{}:$LD_LIBRARY_PATH'.format(os.path.join(self.prefix, 'lib')),
            'PATH': '{}:$PATH'.format(os.path.join(self.prefix, 'bin'))}
        self.__wd = '/var/tmp' # working directory

        # Set the Linux distribution specific parameters
        self.__distro()

        # Construct the series of steps to execute
        self.__setup()

    def __str__(self):
        """String representation of the building block"""

        instructions = []
        instructions.append(comment(
            'UCX version {}'.format(self.__version)))
        instructions.append(packages(ospackages=self.__ospackages))
        instructions.append(shell(commands=self.__commands))
        instructions.append(
            environment(variables=self.__environment_variables))

        return '\n'.join(str(x) for x in instructions)

    def __distro(self):
        """Based on the Linux distribution, set values accordingly.  A user
        specified value overrides any defaults."""

        if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
            if not self.__ospackages:
                self.__ospackages = ['binutils-dev', 'file', 'libnuma-dev',
                                     'make', 'wget']
        elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
            if not self.__ospackages:
                self.__ospackages = ['binutils-devel', 'file', 'make',
                                     'numactl-devel', 'wget']
        else: # pragma: no cover
            raise RuntimeError('Unknown Linux distribution')

    def __setup(self):
        """Construct the series of shell commands, i.e., fill in
           self.__commands"""

        tarball = 'ucx-{}.tar.gz'.format(self.__version)
        url = '{0}/v{1}/{2}'.format(self.__baseurl, self.__version, tarball)

        # CUDA
        if self.__cuda:
            if isinstance(self.__cuda, string_types):
                # Use specified path
                self.configure_opts.append(
                    '--with-cuda={}'.format(self.__cuda))
            elif self.__toolchain.CUDA_HOME:
                self.configure_opts.append(
                    '--with-cuda={}'.format(self.__toolchain.CUDA_HOME))
            else:
                # Default location
                self.configure_opts.append('--with-cuda=/usr/local/cuda')
        else:
            self.configure_opts.append('--without-cuda')

        # GDRCOPY
        if self.__gdrcopy:
            if isinstance(self.__gdrcopy, string_types):
                # Use specified path
                self.configure_opts.append(
                    '--with-gdrcopy={}'.format(self.__gdrcopy))
            else:
                # Boolean, let UCX try to figure out where to find it
                self.configure_opts.append('--with-gdrcopy')
        elif self.__gdrcopy == False:
            self.configure_opts.append('--without-gdrcopy')

        # KNEM
        if self.__knem:
            if isinstance(self.__knem, string_types):
                # Use specified path
                self.configure_opts.append(
                    '--with-knem={}'.format(self.__knem))
            else:
                # Boolean, let UCX try to figure out where to find it
                self.configure_opts.append('--with-knem')
        elif self.__knem == False:
            self.configure_opts.append('--without-knem')

        # XPMEM
        if self.__xpmem:
            if isinstance(self.__xpmem, string_types):
                # Use specified path
                self.configure_opts.append(
                    '--with-xpmem={}'.format(self.__xpmem))
            else:
                # Boolean, let UCX try to figure out where to find it
                self.configure_opts.append('--with-xpmem')
        elif self.__xpmem == False:
            self.configure_opts.append('--without-xpmem')

        # Download source from web
        self.__commands.append(self.download_step(url=url,
                                                  directory=self.__wd))
        self.__commands.append(self.untar_step(
            tarball=os.path.join(self.__wd, tarball), directory=self.__wd))

        # Configure and build
        self.__commands.append(self.configure_step(
            directory=os.path.join(self.__wd, 'ucx-{}'.format(
                self.__version)),
            toolchain=self.__toolchain))
        self.__commands.append(self.build_step())
        self.__commands.append(self.install_step())

        # Cleanup tarball and directory
        self.__commands.append(self.cleanup_step(
            items=[os.path.join(self.__wd, tarball),
                   os.path.join(self.__wd,
                                'ucx-{}'.format(self.__version))]))

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples

        ```python
        u = ucx(...)
        Stage0 += u
        Stage1 += u.runtime()
        ```
        """
        instructions = []
        instructions.append(comment('UCX'))
        instructions.append(copy(_from=_from, src=self.prefix,
                                 dest=self.prefix))
        instructions.append(
            environment(variables=self.__environment_variables))
        return '\n'.join(str(x) for x in instructions)
