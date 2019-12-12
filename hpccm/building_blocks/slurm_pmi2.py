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

"""SLURM PMI2 building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from six import string_types

import logging # pylint: disable=unused-import
import posixpath

import hpccm.templates.ConfigureMake
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
from hpccm.toolchain import toolchain

class slurm_pmi2(bb_base, hpccm.templates.ConfigureMake,
                 hpccm.templates.envvars,
                 hpccm.templates.ldconfig, hpccm.templates.rm,
                 hpccm.templates.tar, hpccm.templates.wget):
    """The `slurm_pmi2` building block configures, builds, and installs
    the PMI2 component from SLURM.

    Note: this building block does not install SLURM itself.

    # Parameters

    configure_opts: List of options to pass to `configure`.  The
    default is an empty list.

    environment: Boolean flag to specify whether the environment
    (`CPATH` and `LD_LIBRARY_PATH`) should be modified to include
    PMI2. The default is False.

    ldconfig: Boolean flag to specify whether the PMI2 library
    directory should be added dynamic linker cache.  If False, then
    `LD_LIBRARY_PATH` is modified to include the PMI2 library
    directory. The default value is False.

    ospackages: List of OS packages to install prior to configuring
    and building.  The default values are `bzip2`, `file`, `make`,
    `perl`, `tar`, and `wget`.

    prefix: The top level install location.  The default value is
    `/usr/local/slurm-pmi2`.

    toolchain: The toolchain object.  This should be used if
    non-default compilers or other toolchain options are needed.  The
    default value is empty.

    version: The version of SLURM source to download.  The default
    value is `19.05.4`.

    # Examples

    ```python
    slurm_pmi2(prefix='/opt/pmi', version='19.05.4')
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(slurm_pmi2, self).__init__(**kwargs)

        self.__baseurl = kwargs.get('baseurl', 'https://download.schedmd.com/slurm')
        self.configure_opts = kwargs.get('configure_opts', [])
        self.environment = kwargs.get('environment', False)
        self.__ospackages = kwargs.get('ospackages', ['bzip2', 'file', 'make',
                                                      'perl', 'tar', 'wget'])
        self.prefix = kwargs.get('prefix', '/usr/local/slurm-pmi2')
        self.__toolchain = kwargs.get('toolchain', toolchain())
        self.__version = kwargs.get('version', '19.05.4')

        self.__commands = [] # Filled in by __setup()
        self.__wd = '/var/tmp' # working directory

        # Construct the series of steps to execute
        self.__setup()

        # Fill in container instructions
        self.__instructions()

    def __instructions(self):
        """Fill in container instructions"""

        self += comment('SLURM PMI2 version {}'.format(self.__version))
        self += packages(ospackages=self.__ospackages)
        self += shell(commands=self.__commands)
        self += environment(variables=self.environment_step())

    def __setup(self):
        """Construct the series of shell commands, i.e., fill in
           self.__commands"""

        tarball = 'slurm-{}.tar.bz2'.format(self.__version)
        url = '{0}/{1}'.format(self.__baseurl, tarball)

        # Download source from web
        self.__commands.append(self.download_step(url=url,
                                                  directory=self.__wd))
        self.__commands.append(self.untar_step(
            tarball=posixpath.join(self.__wd, tarball), directory=self.__wd))

        # Configure, but do not build SLURM itself
        self.__commands.append(self.configure_step(
            directory=posixpath.join(self.__wd, 'slurm-{}'.format(
                self.__version)),
            toolchain=self.__toolchain))

        # Build and install PMI2
        self.__commands.append('make -C contribs/pmi2 install')

        # Set library path
        libpath = posixpath.join(self.prefix, 'lib')
        if self.ldconfig:
            self.__commands.append(self.ldcache_step(directory=libpath))
        else:
            self.environment_variables['LD_LIBRARY_PATH'] = '{}:$LD_LIBRARY_PATH'.format(libpath)

        # Set the environment
        self.environment_variables['CPATH'] = '{}:$CPATH'.format(
            posixpath.join(self.prefix, 'include', 'slurm'))

        # Cleanup tarball and directory
        self.__commands.append(self.cleanup_step(
            items=[posixpath.join(self.__wd, tarball),
                   posixpath.join(self.__wd,
                                  'slurm-{}'.format(self.__version))]))

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples

        ```python
        p = slurm_pmi2(...)
        Stage0 += p
        Stage1 += p.runtime()
        ```
        """
        instructions = []
        instructions.append(comment('SLURM PMI2'))
        instructions.append(copy(_from=_from, src=self.prefix,
                                 dest=self.prefix))
        if self.ldconfig:
            instructions.append(shell(
                commands=[self.ldcache_step(
                    directory=posixpath.join(self.prefix, 'lib'))]))
        instructions.append(environment(variables=self.environment_step()))
        return '\n'.join(str(x) for x in instructions)
