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

import hpccm.config
import hpccm.templates.envvars

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.generic_build import generic_build
from hpccm.building_blocks.packages import packages
from hpccm.common import linux_distro
from hpccm.primitives.comment import comment

class kokkos(bb_base, hpccm.templates.envvars):
    """The `kokkos` building block downloads and installs the
    [Kokkos](https://github.com/kokkos/kokkos) component.

    # Parameters

    annotate: Boolean flag to specify whether to include annotations
    (labels).  The default is False.

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

        self.__arch = kwargs.pop('arch', 'Pascal60')
        self.__baseurl = kwargs.pop('baseurl',
                                    'https://github.com/kokkos/kokkos/archive')
        self.__bootstrap_opts = kwargs.pop('bootstrap_opts', [])
        self.__cuda = kwargs.pop('cuda', True)
        self.__hwloc = kwargs.pop('hwloc', True)
        self.__opts = kwargs.pop('opts', [])
        self.__ospackages = kwargs.pop('ospackages', [])
        self.__parallel = kwargs.pop('parallel', '$(nproc)')
        self.__powertools = False # enable the CentOS PowerTools repo
        self.__prefix = kwargs.pop('prefix', '/usr/local/kokkos')
        self.__version = kwargs.pop('version', '2.9.00')

        # Set the makefile generator options
        self.__generate()

        # Set the Linux distribution specific parameters
        self.__distro()

        # Setup the environment variables
        self.environment_variables['PATH'] = '{}/bin:$PATH'.format(
            self.__prefix)

        # Setup build configuration
        self.__bb = generic_build(
            annotations={'version': self.__version},
            base_annotation=self.__class__.__name__,
            build=['mkdir build',
                   'cd build',
                   '../generate_makefile.bash {}'.format(
                       ' '.join(self.__opts)),
                   'make kokkoslib -j{}'.format(self.__parallel)],
            comment=False,
            devel_environment=self.environment_variables,
            directory='kokkos-{}'.format(self.__version),
            install=['cd build',
                     'make install -j{}'.format(self.__parallel)],
            prefix=self.__prefix,
            runtime_environment=self.environment_variables,
            url='{0}/{1}.tar.gz'.format(self.__baseurl, self.__version),
            **kwargs)

        # Container instructions
        self += comment('Kokkos version {}'.format(self.__version))
        self += packages(ospackages=self.__ospackages,
                         powertools=self.__powertools)
        self += self.__bb

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

    def __generate(self):
        """Setup makefile generator options based on user parameters"""

        # Set options
        if self.__arch:
            self.__opts.append('--arch={}'.format(self.__arch))
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
            self.__opts.append('--prefix={}'.format(self.__prefix))

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
        instructions.append(self.__bb.runtime(_from=_from))
        return '\n'.join(str(x) for x in instructions)
