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

"""Charm++ building block"""

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
from hpccm.templates.sed import sed
from hpccm.templates.tar import tar
from hpccm.templates.wget import wget

class charm(rm, sed, tar, wget):
    """The `charm` building block downloads and install the
    [Charm++](http://charm.cs.illinois.edu/research/charm) component.

    As a side effect, this building block modifies `LD_LIBRARY_PATH`
    and `PATH` to include the Charm++ build.  It also sets the
    `CHARMBASE` environment variable to the top level install
    directory.

    # Parameters

    check: Boolean flag to specify whether the test cases should be
    run.  The default is False.

    options: List of additional options to use when building Charm++.
    The default values are `--build-shared`, and `--with-production`.

    ospackages: List of OS packages to install prior to configuring
    and building.  The default values are `git`, `make`, and `wget`.

    prefix: The top level install prefix.  The default value is
    `/usr/local`.

    target: The target Charm++ framework to build.  The default value
    is `charm++`.

    target_architecture: The target machine architecture to build.
    The default value is `multicore-linux-x86_64`.

    version: The version of Charm++ to download.  The default value is
    `6.8.2`.

    # Examples

    ```python
    charm(prefix='/opt', version='6.8.2')
    ```

    ```python
    charm(target_architecture='mpi-linux-x86_64')
    ```
    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        # Trouble getting MRO with kwargs working correctly, so just call
        # the parent class constructors manually for now.
        #super(charm, self).__init__(**kwargs)
        rm.__init__(self, **kwargs)
        sed.__init__(self, **kwargs)
        tar.__init__(self, **kwargs)
        wget.__init__(self, **kwargs)

        self.__baseurl = kwargs.get('baseurl',
                                    'http://charm.cs.illinois.edu/distrib')
        self.__check = kwargs.get('check', False)
        self.__options = kwargs.get('options', ['--build-shared',
                                                '--with-production'])
        self.__ospackages = kwargs.get('ospackages', ['git', 'make', 'wget'])
        self.__parallel = kwargs.get('parallel', 4)
        self.__prefix = kwargs.get('prefix', '/usr/local')
        self.__target = kwargs.get('target', 'charm++')
        self.__target_architecture = kwargs.get('target_architecture',
                                                'multicore-linux-x86_64')
        self.__version = kwargs.get('version', '6.8.2')

        self.__installdir = os.path.join(self.__prefix,
                                         'charm-v{}'.format(self.__version))
        self.__wd = '/var/tmp' # working directory

        self.__commands = [] # Filled in by __setup()
        self.__environment_variables = {
            'CHARMBASE': self.__installdir,
            'PATH': '{}:$PATH'.format(os.path.join(self.__installdir, 'bin')),
            'LD_LIBRARY_PATH': '{}:$LD_LIBRARY_PATH'.format(
                os.path.join(self.__installdir, 'lib_so'))}

        # Construct series of steps to execute
        self.__setup()

    def __str__(self):
        """String representation of the building block"""
        instructions = []
        instructions.append(
            comment('Charm++ version {}'.format(self.__version)))
        instructions.append(packages(ospackages=self.__ospackages))
        instructions.append(shell(commands=self.__commands))
        instructions.append(
            environment(variables=self.__environment_variables))

        return '\n'.join(str(x) for x in instructions)

    def __setup(self):
        """Construct the series of shell commands, i.e., fill in
           self.__commands"""

        tarball = 'charm-{}.tar.gz'.format(self.__version)
        url = '{0}/{1}'.format(self.__baseurl, tarball)

        # Download source from web
        self.__commands.append(self.download_step(url=url,
                                                  directory=self.__wd))

        # Charm++ does not install nicely into a separate directory,
        # even with "--destination".  So just untar it into the
        # destination directory prefix.
        self.__commands.append(self.untar_step(
            tarball=os.path.join(self.__wd, tarball), directory=self.__prefix))

        # Charm++ is hard-coded to use pgCC rather than pgc++ when the
        # PGI compiler is selected.  Replace pgCC with pgc++.
        # But... PGI is not really supported by Charm++:
        # https://charm.cs.illinois.edu/redmine/issues/234
        if 'pgcc' in self.__options:
            self.__commands.append(
                self.sed_step(
                    file=os.path.join(self.__installdir, 'src', 'arch',
                                      'common', 'cc-pgcc.sh'),
                    patterns=[r's/pgCC/pgc++/g']))

        # Build
        self.__commands.append('cd {} && ./build {} {} {} -j{}'.format(
            self.__installdir, self.__target, self.__target_architecture,
            ' '.join(self.__options), self.__parallel))

        # Check the build
        if self.__check:
            self.__commands.append('cd {} && make test'.format(
                os.path.join(self.__installdir, 'tests', 'charm++')))

        # Cleanup tarball and directory
        self.__commands.append(self.cleanup_step(
            items=[os.path.join(self.__wd, tarball)]))

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Example

        ```python
        c = charm(...)
        Stage0 += c
        Stage1 += c.runtime()
        ```
        """
        instructions = []
        instructions.append(comment('Charm++'))
        instructions.append(copy(_from=_from, src=self.__installdir,
                                 dest=self.__installdir))
        instructions.append(environment(
            variables=self.__environment_variables))
        return '\n'.join(str(x) for x in instructions)
