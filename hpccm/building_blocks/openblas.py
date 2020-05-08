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

"""OpenBLAS building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import posixpath

import hpccm.config
import hpccm.templates.envvars
import hpccm.templates.ldconfig

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.generic_build import generic_build
from hpccm.building_blocks.packages import packages
from hpccm.common import cpu_arch
from hpccm.primitives.comment import comment
from hpccm.toolchain import toolchain

class openblas(bb_base, hpccm.templates.envvars, hpccm.templates.ldconfig):
    """The `openblas` building block builds and installs the
    [OpenBLAS](https://www.openblas.net) component.

    # Parameters

    annotate: Boolean flag to specify whether to include annotations
    (labels).  The default is False.

    environment: Boolean flag to specify whether the environment
    (`LD_LIBRARY_PATH` and `PATH`) should be modified to include
    OpenBLAS. The default is True.

    ldconfig: Boolean flag to specify whether the OpenBLAS library
    directory should be added dynamic linker cache.  If False, then
    `LD_LIBRARY_PATH` is modified to include the OpenBLAS library
    directory. The default value is False.

    make_opts: List of options to pass to `make`.  For aarch64
    processors, the default values are `TARGET=ARMV8` and
    `USE_OPENMP=1`.  For ppc64le processors, the default values are
    `TARGET=POWER8` and `USE_OPENMP=1`.  For x86_64 processors, the
    default value is `USE_OPENMP=1`.

    ospackages: List of OS packages to install prior to building.  The
    default values are `make`, `perl`, `tar`, and `wget`.

    prefix: The top level installation location.  The default value is
    `/usr/local/openblas`.

    toolchain: The toolchain object.  This should be used if
    non-default compilers or other toolchain options are needed.  The
    default is empty.

    version: The version of OpenBLAS source to download.  The default
    value is `0.3.7`.

    # Examples

    ```python
    openblas(prefix='/opt/openblas/0.3.1', version='0.3.1')
    ```

    ```python
    p = pgi(eula=True)
    openblas(toolchain=p.toolchain)
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(openblas, self).__init__(**kwargs)

        self.__baseurl = kwargs.pop('baseurl', 'https://github.com/xianyi/OpenBLAS/archive')
        self.__make_opts = kwargs.pop('make_opts',
                                      []) # Filled in by __cpu_arch()
        self.__ospackages = kwargs.pop('ospackages', ['make', 'perl', 'tar',
                                                      'wget'])
        self.__prefix = kwargs.pop('prefix', '/usr/local/openblas')
        self.__toolchain = kwargs.pop('toolchain', toolchain())
        self.__version = kwargs.pop('version', '0.3.7')

        # Set the make options
        self.__make()

        # Setup the environment variables
        if not self.ldconfig:
            self.environment_variables['LD_LIBRARY_PATH'] = '{}:$LD_LIBRARY_PATH'.format(posixpath.join(self.__prefix, 'lib'))

        # Setup build configuration
        self.__bb = generic_build(
            annotations={'version': self.__version},
            base_annotation=self.__class__.__name__,
            build=['make {}'.format(' '.join(self.__make_opts))],
            comment=False,
            directory='OpenBLAS-{}'.format(self.__version),
            devel_environment=self.environment_variables,
            install=['make install PREFIX={}'.format(self.__prefix)],
            prefix=self.__prefix,
            runtime_environment=self.environment_variables,
            url='{0}/v{1}.tar.gz'.format(self.__baseurl, self.__version),
            **kwargs)

        # Container instructions
        self += comment('OpenBLAS version {}'.format(self.__version))
        self += packages(ospackages=self.__ospackages)
        self += self.__bb

    def __make(self):
        """Based on the CPU architecture, set values accordingly.  A user
        specified value overrides any defaults."""

        if not self.__make_opts:
            if self.__toolchain.CC:
                self.__make_opts.append('CC={}'.format(self.__toolchain.CC))
            if self.__toolchain.FC:
                self.__make_opts.append('FC={}'.format(self.__toolchain.FC))

            if hpccm.config.g_cpu_arch == cpu_arch.AARCH64:
                self.__make_opts.extend(['TARGET=ARMV8', 'USE_OPENMP=1'])
            elif hpccm.config.g_cpu_arch == cpu_arch.PPC64LE:
                self.__make_opts.extend(['TARGET=POWER8', 'USE_OPENMP=1'])
            elif hpccm.config.g_cpu_arch == cpu_arch.X86_64:
                self.__make_opts.extend(['USE_OPENMP=1'])
            else: # pragma: no cover
                raise RuntimeError('Unknown CPU architecture')

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples

        ```python
        o = openblas(...)
        Stage0 += o
        Stage1 += o.runtime()
        ```
        """
        instructions = []
        instructions.append(comment('OpenBLAS'))
        instructions.append(self.__bb.runtime(_from=_from))
        return '\n'.join(str(x) for x in instructions)
