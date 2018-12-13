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

"""PnetCDF building block"""

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
from hpccm.templates.ConfigureMake import ConfigureMake
from hpccm.templates.rm import rm
from hpccm.templates.tar import tar
from hpccm.templates.wget import wget
from hpccm.toolchain import toolchain

class pnetcdf(ConfigureMake, rm, tar, wget):
    """The `pnetcdf` building block downloads, configures, builds, and
    installs the
    [PnetCDF](http://cucis.ece.northwestern.edu/projects/PnetCDF/index.html)
    component.

    As a side effect, this building block modifies `PATH` and
    `LD_LIBRARY_PATH` to include the PnetCDF build.

    # Parameters

    check: Boolean flag to specify whether the `make check` step
    should be performed.  The default is False.

    configure_opts: List of options to pass to `configure`.  The
    default values are `--enable-shared`.

    ospackages: List of OS packages to install prior to configuring
    and building.  The default values are `m4`, `make`, `tar`, and
    `wget`.

    prefix: The top level install location.  The default value is
    `/usr/local/pnetcdf`.

    toolchain: The toolchain object.  A MPI compiler toolchain must be
    used.  The default is to use the standard MPI compiler wrappers,
    e.g., `CC=mpicc`, `CXX=mpicxx`, etc.

    version: The version of PnetCDF source to download.  The default
    value is `1.10.0`.

    # Examples

    ```python
    pnetcdf(prefix='/opt/pnetcdf/1.10.0', version='1.10.0')
    ```

    ```python
    ompi = openmpi(...)
    pnetcdf(toolchain=ompi.toolchain, ...)
    ```
    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        # Trouble getting MRO with kwargs working correctly, so just call
        # the parent class constructors manually for now.
        #super(pnetcdf, self).__init__(**kwargs)
        ConfigureMake.__init__(self, **kwargs)
        rm.__init__(self, **kwargs)
        tar.__init__(self, **kwargs)
        wget.__init__(self, **kwargs)

        self.configure_opts = kwargs.get('configure_opts', ['--enable-shared'])
        self.prefix = kwargs.get('prefix', '/usr/local/pnetcdf')

        self.__baseurl = kwargs.get('baseurl', 'http://cucis.ece.northwestern.edu/projects/PnetCDF/Release')
        self.__check = kwargs.get('check', False)
        self.__ospackages = kwargs.get('ospackages', ['m4', 'make', 'tar',
                                                      'wget'])
        self.__toolchain = kwargs.get('toolchain',
                                      toolchain(CC='mpicc', CXX='mpicxx',
                                                F77='mpif77', F90='mpif90',
                                                FC='mpifort'))
        self.__version = kwargs.get('version', '1.10.0')

        self.__commands = [] # Filled in by __setup()
        self.__environment_variables = {
            'PATH':
            '{}:$PATH'.format(os.path.join(self.prefix, 'bin')),
            'LD_LIBRARY_PATH':
            '{}:$LD_LIBRARY_PATH'.format(os.path.join(self.prefix, 'lib'))}
        self.__wd = '/var/tmp' # working directory

        # Construct the series of steps to execute
        self.__setup()

    def __str__(self):
        """String representation of the building block"""

        instructions = []
        instructions.append(comment(
            'PnetCDF version {}'.format(self.__version)))
        instructions.append(packages(ospackages=self.__ospackages))
        instructions.append(shell(commands=self.__commands))
        instructions.append(environment(
            variables=self.__environment_variables))

        return '\n'.join(str(x) for x in instructions)

    def __setup(self):
        """Construct the series of shell commands, i.e., fill in
           self.__commands"""

        tarball = 'parallel-netcdf-{}.tar.gz'.format(self.__version)
        url = '{0}/{1}'.format(self.__baseurl, tarball)

        # Download source from web
        self.__commands.append(self.download_step(url=url,
                                                  directory=self.__wd))
        self.__commands.append(self.untar_step(
            tarball=os.path.join(self.__wd, tarball), directory=self.__wd))
        self.__commands.append(self.configure_step(
            directory=os.path.join(self.__wd, 'parallel-netcdf-{}'.format(
                self.__version)),
            toolchain=self.__toolchain))

        # For some compilers, --enable-shared leads to the following error:
        #   GEN      libpnetcdf.la
        # /usr/bin/ld: .libs/libpnetcdf.lax/libf77.a/strerrnof.o: relocation R_X86_64_32 against `.data' can not be used when making a shared object; recompile with -fPIC
        # .libs/libpnetcdf.lax/libf77.a/strerrnof.o: error adding symbols: Bad value
        # Apply the workaround
        if '--enable-shared' in self.configure_opts:
          self.__commands.append('sed -i -e \'s#pic_flag=""#pic_flag=" -fpic -DPIC"#\' -e \'s#wl=""#wl="-Wl,"#\' {}'.format(os.path.join(self.__wd, 'parallel-netcdf-{}'.format(self.__version), 'libtool')))

        self.__commands.append(self.build_step())

        # Check the build
        if self.__check:
            self.__commands.append(self.check_step())

        self.__commands.append(self.install_step())

        # Cleanup tarball and directory
        self.__commands.append(self.cleanup_step(
            items=[os.path.join(self.__wd, tarball),
                   os.path.join(self.__wd,
                                'parallel-netcdf-{}'.format(self.__version))]))

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples

        ```python
        p = pnetcdf(...)
        Stage0 += p
        Stage1 += p.runtime()
        ```
        """
        instructions = []
        instructions.append(comment('PnetCDF'))
        instructions.append(copy(_from=_from, src=self.prefix,
                                 dest=self.prefix))
        instructions.append(environment(
            variables=self.__environment_variables))
        return '\n'.join(str(x) for x in instructions)
