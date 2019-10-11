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

"""Kokkos building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from six import string_types

from distutils.version import StrictVersion
import logging # pylint: disable=unused-import
import posixpath

import hpccm.config
import hpccm.templates.envvars
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

class kokkos(bb_base, hpccm.templates.envvars, hpccm.templates.rm,
             hpccm.templates.tar, hpccm.templates.wget):
    """The `kokkos` building block downloads and installs the
    [Kokkos](https://github.com/kokkos/kokkos) component.

    # Parameters

    arch: Flag to set the target architecture. If set adds
    `--arch=value` to the list of `generate_makefile.bash` options.
    The default value is `Pascal60`, i.e., sm_60.  If a cuda aware
    build is not selected, then a non-default value should be used.

    cuda: Flag to control whether a CUDA aware build is performed.  If
    True, adds `--with-cuda` to the list of `generate_makefile.bash`
    options.  If a string, uses the value of the string as the CUDA
    path.  If False, does nothing.  The default value is True.

    environment: Boolean flag to specify whether the environment
    (`LD_LIBRARY_PATH` and `PATH`) should be modified to include
    Kokkos. The default is True.

    hwloc: Flag to control whether a hwloc aware build is performed.
    If True, adds `--with-hwloc` to the list of
    `generate_makefile.bash` options.  If a string, uses the value of
    the string as the hwloc path.  If False, does nothing.  The
    default value is True.

    opts: List of options to pass to `generate_makefile.bash`.  The
    default is an empty list.

    ospackages: List of OS packages to install prior to building.  For
    Ubuntu, the default values are `bc`, `gzip`, `libhwloc-dev`,
    `make`, `tar`, and `wget`.  For RHEL-based Linux distributions the
    default values are `bc`, `gzip`, `hwloc-devel`, `make`, `tar`,
    `wget`, and `which`.

    prefix: The top level installation location.  The default value
    is `/usr/local/kokkos`.

    version: The version of Kokkos source to download.  The default
    value is `2.9.00`.

    # Examples

    ```python
    kokkos(prefix='/opt/kokkos/2.8.00', version='2.8.00')
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(kokkos, self).__init__(**kwargs)

        self.__arch = kwargs.get('arch', 'Pascal60')
        self.__baseurl = kwargs.get('baseurl',
                                    'https://github.com/kokkos/kokkos/archive')
        self.__bootstrap_opts = kwargs.get('bootstrap_opts', [])
        self.__cuda = kwargs.get('cuda', True)
        self.__hwloc = kwargs.get('hwloc', True)
        self.__opts = kwargs.get('opts', [])
        self.__ospackages = kwargs.get('ospackages', [])
        self.__parallel = kwargs.get('parallel', '$(nproc)')
        self.__powertools = False # enable the CentOS PowerTools repo
        self.__prefix = kwargs.get('prefix', '/usr/local/kokkos')
        self.__version = kwargs.get('version', '2.9.00')

        self.__commands = [] # Filled in by __setup()
        self.__wd = '/var/tmp' # working directory

        # Set the Linux distribution specific parameters
        self.__distro()

        # Construct the series of steps to execute
        self.__setup()

        # Fill in container instructions
        self.__instructions()

    def __instructions(self):
        """Fill in container instructions"""

        self += comment('Kokkos version {}'.format(self.__version))
        self += packages(ospackages=self.__ospackages,
                         powertools=self.__powertools)
        self += shell(commands=self.__commands)
        self += environment(variables=self.environment_step())

    def __distro(self):
        """Based on the Linux distribution, set values accordingly.  A user
        specified value overrides any defaults."""

        if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
            if not self.__ospackages:
                self.__ospackages = ['bc', 'gzip', 'libhwloc-dev', 'make',
                                     'tar', 'wget']
        elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
            if not self.__ospackages:
                self.__ospackages = ['bc', 'gzip', 'hwloc-devel', 'make',
                                     'tar', 'wget', 'which']

            if hpccm.config.g_linux_version >= StrictVersion('8.0'):
                # hwloc-devel is in the CentOS powertools repository
                self.__powertools = True
        else: # pragma: no cover
            raise RuntimeError('Unknown Linux distribution')

    def __setup(self):
        """Construct the series of shell commands, i.e., fill in
           self.__commands"""

        tarball = '{}.tar.gz'.format(self.__version)
        url = '{0}/{1}'.format(self.__baseurl, tarball)

        # Download source from web
        self.__commands.append(self.download_step(url=url,
                                                  directory=self.__wd))
        self.__commands.append(self.untar_step(
            tarball=posixpath.join(self.__wd, tarball), directory=self.__wd))

        # Set options
        opts = self.__opts
        if self.__arch:
            opts.append('--arch={}'.format(self.__arch))
        if self.__cuda:
            if isinstance(self.__cuda, string_types):
                # Use specified path
                self.__opts.append(
                    '--with-cuda={}'.format(self.__cuda))
            else:
                # Let it figure it out
                self.__opts.append('--with-cuda')
        if self.__hwloc:
            if isinstance(self.__hwloc, string_types):
                # Use specified path
                self.__opts.append(
                    '--with-hwloc={}'.format(self.__hwloc))
            else:
                # Let it figure it out
                self.__opts.append('--with-hwloc')
        if self.__prefix:
            opts.append('--prefix={}'.format(self.__prefix))

        # Configure
        src_dir = posixpath.join(self.__wd, 'kokkos-{}'.format(self.__version))
        build_dir = posixpath.join(src_dir, 'build')
        self.__commands.append('mkdir -p {0} && cd {0}'.format(build_dir))
        self.__commands.append(
            '{0}/generate_makefile.bash {1}'.format(src_dir, ' '.join(opts)))

        # Build and install
        self.__commands.append('make kokkoslib -j{}'.format(self.__parallel))
        self.__commands.append('make install -j{}'.format(self.__parallel))

        # Cleanup tarball and directory
        self.__commands.append(self.cleanup_step(
            items=[posixpath.join(self.__wd, tarball),
                   posixpath.join(self.__wd,
                                  'kokkos-{}'.format(self.__version))]))

        # Set the environment
        self.environment_variables['PATH'] = '{}/bin:$PATH'.format(
            self.__prefix)

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples

        ```python
        k = kokkos(...)
        Stage0 += k
        Stage1 += k.runtime()
        ```
        """
        instructions = []
        instructions.append(comment('Kokkos'))
        instructions.append(copy(_from=_from, src=self.__prefix,
                                 dest=self.__prefix))
        instructions.append(environment(variables=self.environment_step()))
        return '\n'.join(str(x) for x in instructions)
