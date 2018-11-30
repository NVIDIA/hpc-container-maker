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

"""FFTW building block"""

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

class fftw(ConfigureMake, rm, tar, wget):
    """The `fftw` building block downloads, configures, builds, and
    installs the [FFTW](http://www.fftw.org) component.  Depending on
    the parameters, the source will be downloaded from the web
    (default) or copied from a source directory in the local build
    context.

    As a side effect, this building block modifies `LD_LIBRARY_PATH`
    to include the FFTW build.

    # Parameters

    check: Boolean flag to specify whether the `make check` step
    should be performed.  The default is False.

    configure_opts: List of options to pass to `configure`.  The
    default values are `--enable-shared`, `--enable-openmp`,
    `--enable-threads`, and `--enable-sse2`.

    directory: Path to the unpackaged source directory relative to the
    local build context.  The default value is empty.  If this is
    defined, the source in the local build context will be used rather
    than downloading the source from the web.

    mpi: Boolean flag to specify whether to build with MPI support
    enabled.  The default is False.

    ospackages: List of OS packages to install prior to configuring
    and building.  The default values are `file`, `make`, and `wget`.

    prefix: The top level install location.  The default value is
    `/usr/local/fftw`.

    toolchain: The toolchain object.  This should be used if
    non-default compilers or other toolchain options are needed.  The
    default is empty.

    version: The version of FFTW source to download.  This value is
    ignored if `directory` is set.  The default value is `3.3.8`.

    # Examples

    ```python
    fftw(prefix='/opt/fftw/3.3.7', version='3.3.7')
    ```

    ```python
    fftw(directory='sources/fftw-3.3.7')
    ```

    ```python
    p = pgi(eula=True)
    fftw(toolchain=p.toolchain)
    ```

    ```python
    fftw(check=True, configure_opts=['--enable-shared', '--enable-threads',
                                     '--enable-sse2', '--enable-avx'])
    ```
    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        # Trouble getting MRO with kwargs working correctly, so just call
        # the parent class constructors manually for now.
        #super(fftw, self).__init__(**kwargs)
        ConfigureMake.__init__(self, **kwargs)
        rm.__init__(self, **kwargs)
        tar.__init__(self, **kwargs)
        wget.__init__(self, **kwargs)

        self.configure_opts = kwargs.get('configure_opts',
                                         ['--enable-shared', '--enable-openmp',
                                          '--enable-threads', '--enable-sse2'])
        self.prefix = kwargs.get('prefix', '/usr/local/fftw')

        self.__baseurl = kwargs.get('baseurl', 'ftp://ftp.fftw.org/pub/fftw')
        self.__check = kwargs.get('check', False)
        self.__directory = kwargs.get('directory', '')
        self.__mpi = kwargs.get('mpi', False)
        self.__ospackages = kwargs.get('ospackages', ['file', 'make', 'wget'])
        self.__toolchain = kwargs.get('toolchain', toolchain())
        self.__version = kwargs.get('version', '3.3.8')

        self.__commands = [] # Filled in by __setup()
        self.__environment_variables = {
            'LD_LIBRARY_PATH':
            '{}:$LD_LIBRARY_PATH'.format(os.path.join(self.prefix, 'lib'))}
        self.__wd = '/var/tmp' # working directory

        # Construct series of steps to execute
        self.__setup()

    def __str__(self):
        """String representation of the building block"""
        instructions = []
        if self.__directory:
            instructions.append(comment('FFTW'))
        else:
            instructions.append(
                comment('FFTW version {}'.format(self.__version)))
        instructions.append(packages(ospackages=self.__ospackages))
        if self.__directory:
            # Use source from local build context
            instructions.append(
                copy(src=self.__directory,
                     dest=os.path.join(self.__wd,
                                       self.__directory)))
        instructions.append(shell(commands=self.__commands))
        instructions.append(
            environment(variables=self.__environment_variables))

        return '\n'.join(str(x) for x in instructions)

    def __setup(self):
        """Construct the series of shell commands, i.e., fill in
           self.__commands"""

        tarball = 'fftw-{}.tar.gz'.format(self.__version)
        url = '{0}/{1}'.format(self.__baseurl, tarball)

        if self.__mpi:
            self.configure_opts.append('--enable-mpi')

        if self.__directory:
            # Use source from local build context
            self.__commands.append(self.configure_step(
                directory=os.path.join(self.__wd, self.__directory),
                toolchain=self.__toolchain))
        else:
            # Download source from web
            self.__commands.append(self.download_step(url=url,
                                                      directory=self.__wd))
            self.__commands.append(self.untar_step(
                tarball=os.path.join(self.__wd, tarball), directory=self.__wd))
            self.__commands.append(self.configure_step(
                directory=os.path.join(self.__wd,
                                       'fftw-{}'.format(self.__version)),
                toolchain=self.__toolchain))

        self.__commands.append(self.build_step())

        # Check the build
        if self.__check:
            # PGI compiler needs a larger stack size
            self.__commands.append('ulimit -s unlimited')
            self.__commands.append(self.check_step())

        self.__commands.append(self.install_step())

        if self.__directory:
            # Using source from local build context, cleanup directory
            self.__commands.append(self.cleanup_step(
                items=[os.path.join(self.__wd, self.__directory)]))
        else:
            # Using downloaded source, cleanup tarball and directory
            self.__commands.append(self.cleanup_step(
                items=[os.path.join(self.__wd, tarball),
                       os.path.join(self.__wd,
                                    'fftw-{}'.format(self.__version))]))

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples

        ```python
        f = fftw(...)
        Stage0 += f
        Stage1 += f.runtime()
        ```
        """
        instructions = []
        instructions.append(comment('FFTW'))
        instructions.append(copy(_from=_from, src=self.prefix,
                                 dest=self.prefix))
        instructions.append(environment(
            variables=self.__environment_variables))
        return '\n'.join(str(x) for x in instructions)
