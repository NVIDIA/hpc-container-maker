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
import posixpath

import hpccm.templates.envvars
import hpccm.templates.ldconfig
import hpccm.templates.rm
import hpccm.templates.tar
import hpccm.templates.wget

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.packages import packages
from hpccm.primitives.comment import comment
from hpccm.primitives.copy import copy
from hpccm.primitives.environment import environment
from hpccm.primitives.shell import shell

class gdrcopy(bb_base, hpccm.templates.envvars, hpccm.templates.ldconfig,
              hpccm.templates.rm, hpccm.templates.tar, hpccm.templates.wget):
    """The `gdrcopy` building block builds and installs the user space
    library from the [gdrcopy](https://github.com/NVIDIA/gdrcopy)
    component.

    # Parameters

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
    value is `1.3`.

    # Examples

    ```python
    gdrcopy(prefix='/opt/gdrcopy/1.3', version='1.3')
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(gdrcopy, self).__init__(**kwargs)

        self.__baseurl = kwargs.get('baseurl', 'https://github.com/NVIDIA/gdrcopy/archive')
        self.__ospackages = kwargs.get('ospackages', ['make', 'wget'])
        self.__prefix = kwargs.get('prefix', '/usr/local/gdrcopy')
        self.__version = kwargs.get('version', '1.3')

        self.__commands = [] # Filled in by __setup()
        self.__wd = '/var/tmp' # working directory

        # Construct the series of steps to execute
        self.__setup()

        # Fill in container instructions
        self.__instructions()

    def __instructions(self):
        """Fill in container instructions"""

        self += comment('GDRCOPY version {}'.format(self.__version))
        self += packages(ospackages=self.__ospackages)
        self += shell(commands=self.__commands)
        self += environment(variables=self.environment_step())

    def __setup(self):
        """Construct the series of shell commands, i.e., fill in
           self.__commands"""

        tarball = 'v{}.tar.gz'.format(self.__version)
        url = '{0}/{1}'.format(self.__baseurl, tarball)

        # Download source from web
        self.__commands.append(self.download_step(url=url,
                                                  directory=self.__wd))
        self.__commands.append(self.untar_step(
            tarball=posixpath.join(self.__wd, tarball), directory=self.__wd))
        self.__commands.append('cd {}'.format(
            posixpath.join(self.__wd, 'gdrcopy-{}'.format(self.__version))))

        # Work around "install -D" issue on CentOS
        self.__commands.append('mkdir -p {0}/include {0}/lib64'.format(self.__prefix))

        self.__commands.append('make PREFIX={} lib lib_install'.format(self.__prefix))

        # Set library path
        libpath = posixpath.join(self.__prefix, 'lib64')
        if self.ldconfig:
            self.__commands.append(self.ldcache_step(directory=libpath))
        else:
            self.environment_variables['LD_LIBRARY_PATH'] = '{}:$LD_LIBRARY_PATH'.format(libpath)

        # Cleanup tarball and directory
        self.__commands.append(self.cleanup_step(
            items=[posixpath.join(self.__wd, tarball),
                   posixpath.join(self.__wd,
                                  'gdrcopy-{}'.format(self.__version))]))

        # Set the environment
        self.environment_variables['CPATH'] = '{}:$CPATH'.format(
            posixpath.join(self.__prefix, 'include'))
        self.environment_variables['LIBRARY_PATH'] = '{}:$LIBRARY_PATH'.format(posixpath.join(self.__prefix, 'lib64'))

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
        if self.ldconfig:
            instructions.append(shell(
                commands=[self.ldcache_step(
                    directory=posixpath.join(self.__prefix, 'lib64'))]))
        instructions.append(environment(variables=self.environment_step()))
        return '\n'.join(str(x) for x in instructions)
