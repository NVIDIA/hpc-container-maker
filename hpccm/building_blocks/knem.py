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

"""KNEM building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import posixpath

import hpccm.templates.envvars

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.generic_build import generic_build
from hpccm.building_blocks.packages import packages
from hpccm.primitives.comment import comment

class knem(bb_base, hpccm.templates.envvars):
    """The `knem` building block install the headers from the
    [KNEM](http://knem.gforge.inria.fr) component.

    # Parameters

    annotate: Boolean flag to specify whether to include annotations
    (labels).  The default is False.

    environment: Boolean flag to specify whether the environment
    (`CPATH`) should be modified to include knem. The default is True.

    ospackages: List of OS packages to install prior to installing.
    The default values are `ca-certificates` and `git`.

    prefix: The top level install location.  The default value is
    `/usr/local/knem`.

    version: The version of KNEM source to download.  The default
    value is `1.1.3`.

    # Examples

    ```python
    knem(prefix='/opt/knem/1.1.3', version='1.1.3')
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(knem, self).__init__(**kwargs)

        self.__ospackages = kwargs.pop('ospackages',
                                       ['ca-certificates', 'git'])
        self.__prefix = kwargs.pop('prefix', '/usr/local/knem')
        self.__repository = kwargs.pop('repository', 'https://gforge.inria.fr/git/knem/knem.git')
        self.__version = kwargs.pop('version', '1.1.3')

        # Setup the environment variables
        self.environment_variables['CPATH'] = '{}:$CPATH'.format(
            posixpath.join(self.__prefix, 'include'))

        # Setup build configuration
        self.__bb = generic_build(
            base_annotation=self.__class__.__name__,
            branch='knem-{}'.format(self.__version),
            comment=False,
            devel_environment=self.environment_variables,
            install=['mkdir -p {}/include'.format(self.__prefix),
                     'cp common/*.h {}/include'.format(self.__prefix)],
            runtime_environment=self.environment_variables,
            prefix=self.__prefix,
            repository=self.__repository,
            **kwargs)

        # Container instructions
        self += comment('KNEM version {}'.format(self.__version))
        self += packages(ospackages=self.__ospackages)
        self += self.__bb

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples

        ```python
        k = knem(...)
        Stage0 += k
        Stage1 += k.runtime()
        ```
        """
        instructions = []
        instructions.append(comment('KNEM'))
        instructions.append(self.__bb.runtime(_from=_from))
        return '\n'.join(str(x) for x in instructions)
