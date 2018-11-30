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

import logging # pylint: disable=unused-import
import os

from hpccm.building_blocks.packages import packages
from hpccm.primitives.comment import comment
from hpccm.primitives.copy import copy
from hpccm.primitives.environment import environment
from hpccm.primitives.shell import shell
from hpccm.templates.rm import rm
from hpccm.templates.tar import tar
from hpccm.templates.wget import wget

class gdrcopy(rm, tar, wget):
    """The `gdrcopy` building block builds and installs the user space
    library from the [gdrcopy](https://github.com/NVIDIA/gdrcopy)
    component.

    As a side effect, this building block modifies `CPATH`,
    `LD_LIBRARY_PATH`, and `LIBRARY_PATH`.

    # Parameters

    ospackages: List of OS packages to install prior to building.  The
    default values are `make` and `wget`.

    prefix: The top level install location.  The default value is
    `/usr/local/gdrcopy`.

    version: The version of gdrcopy source to download.  The default
    value is `1.3`.

    # Examples

    ```python
    gdrcopy(prefix='/opt/gdrcopy/1.3', version='1.3')
    ```
    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        # Trouble getting MRO with kwargs working correctly, so just call
        # the parent class constructors manually for now.
        #super(gdrcopy, self).__init__(**kwargs)
        tar.__init__(self, **kwargs)
        rm.__init__(self, **kwargs)
        wget.__init__(self, **kwargs)


        self.__baseurl = kwargs.get('baseurl', 'https://github.com/NVIDIA/gdrcopy/archive')
        self.__ospackages = kwargs.get('ospackages', ['make', 'wget'])
        self.__prefix = kwargs.get('prefix', '/usr/local/gdrcopy')
        self.__version = kwargs.get('version', '1.3')

        self.__commands = [] # Filled in by __setup()
        self.__environment_variables = {
            'CPATH':
            '{}:$CPATH'.format(os.path.join(self.__prefix, 'include')),
            'LD_LIBRARY_PATH':
            '{}:$LD_LIBRARY_PATH'.format(os.path.join(self.__prefix, 'lib64')),
            'LIBRARY_PATH':
            '{}:$LIBRARY_PATH'.format(os.path.join(self.__prefix, 'lib64'))}
        self.__wd = '/var/tmp' # working directory

        # Construct the series of steps to execute
        self.__setup()

    def __str__(self):
        """String representation of the building block"""

        instructions = []
        instructions.append(comment(
            'GDRCOPY version {}'.format(self.__version)))
        instructions.append(packages(ospackages=self.__ospackages))
        instructions.append(shell(commands=self.__commands))
        instructions.append(
            environment(variables=self.__environment_variables))

        return '\n'.join(str(x) for x in instructions)

    def __setup(self):
        """Construct the series of shell commands, i.e., fill in
           self.__commands"""

        tarball = 'v{}.tar.gz'.format(self.__version)
        url = '{0}/{1}'.format(self.__baseurl, tarball)

        # Download source from web
        self.__commands.append(self.download_step(url=url,
                                                  directory=self.__wd))
        self.__commands.append(self.untar_step(
            tarball=os.path.join(self.__wd, tarball), directory=self.__wd))
        self.__commands.append('cd {}'.format(
            os.path.join(self.__wd, 'gdrcopy-{}'.format(self.__version))))

        # Work around "install -D" issue on CentOS
        self.__commands.append('mkdir -p {0}/include {0}/lib64'.format(self.__prefix))

        self.__commands.append('make PREFIX={} lib lib_install'.format(self.__prefix))

        # Cleanup tarball and directory
        self.__commands.append(self.cleanup_step(
            items=[os.path.join(self.__wd, tarball),
                   os.path.join(self.__wd,
                                'gdrcopy-{}'.format(self.__version))]))

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
        instructions.append(copy(_from=_from, src=self.__prefix,
                                 dest=self.__prefix))
        instructions.append(
            environment(variables=self.__environment_variables))
        return '\n'.join(str(x) for x in instructions)
