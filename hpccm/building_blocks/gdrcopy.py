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

"""GDRCOPY building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import posixpath

import hpccm.templates.envvars
import hpccm.templates.ldconfig

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.generic_build import generic_build
from hpccm.building_blocks.packages import packages
from hpccm.primitives.comment import comment

class gdrcopy(bb_base, hpccm.templates.envvars, hpccm.templates.ldconfig):
    """The `gdrcopy` building block builds and installs the user space
    library from the [gdrcopy](https://github.com/NVIDIA/gdrcopy)
    component.

    # Parameters

    annotate: Boolean flag to specify whether to include annotations
    (labels).  The default is False.

    environment: Boolean flag to specify whether the environment
    (`CPATH`, `LIBRARY_PATH`, and `LD_LIBRARY_PATH`) should be
    modified to include the gdrcopy. The default is True.

    ldconfig: Boolean flag to specify whether the gdrcopy library
    directory should be added dynamic linker cache.  If False, then
    `LD_LIBRARY_PATH` is modified to include the gdrcopy library
    directory. The default value is False.

    ospackages: List of OS packages to install prior to building.  The
    default values are `make` and `wget`.

    prefix: The top level install location.  The default value is
    `/usr/local/gdrcopy`.

    version: The version of gdrcopy source to download.  The default
    value is `2.0`.

    # Examples

    ```python
    gdrcopy(prefix='/opt/gdrcopy/1.3', version='1.3')
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(gdrcopy, self).__init__(**kwargs)

        # Parameters
        self.__baseurl = kwargs.pop('baseurl', 'https://github.com/NVIDIA/gdrcopy/archive')
        self.__ospackages = kwargs.pop('ospackages', ['make', 'wget'])
        self.__prefix = kwargs.pop('prefix', '/usr/local/gdrcopy')
        self.__version = kwargs.pop('version', '2.0')

        # Setup the environment variables
        self.environment_variables['CPATH'] = '{}:$CPATH'.format(
            posixpath.join(self.__prefix, 'include'))
        self.environment_variables['LIBRARY_PATH'] = '{}:$LIBRARY_PATH'.format(
            posixpath.join(self.__prefix, 'lib64'))
        if not self.ldconfig:
            self.environment_variables['LD_LIBRARY_PATH'] = '{}:$LD_LIBRARY_PATH'.format(
                posixpath.join(self.__prefix, 'lib64'))

        # Setup build configuration
        self.__bb = generic_build(
            annotations={'version': self.__version},
            base_annotation=self.__class__.__name__,
            # Work around "install -D" issue on CentOS
            build=['mkdir -p {0}/include {0}/lib64'.format(self.__prefix),
                   'make PREFIX={} lib lib_install'.format(self.__prefix)],
            comment=False,
            devel_environment=self.environment_variables,
            directory='gdrcopy-{}'.format(self.__version),
            libdir='lib64',
            prefix=self.__prefix,
            runtime_environment=self.environment_variables,
            url='{0}/v{1}.tar.gz'.format(self.__baseurl, self.__version),
            **kwargs)

        # Container instructions
        self += comment('GDRCOPY version {}'.format(self.__version))
        self += packages(ospackages=self.__ospackages)
        self += self.__bb

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples

        ```python
        g = gdrcopy(...)
        Stage0 += g
        Stage1 += g.runtime()
        ```
        """

        instructions = []
        instructions.append(comment('GDRCOPY'))
        instructions.append(self.__bb.runtime(_from=_from))
        return '\n'.join(str(x) for x in instructions)
