# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
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

"""NVSHMEM building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import posixpath
from six import string_types

import hpccm.templates.envvars
import hpccm.templates.rm
import hpccm.templates.tar
import hpccm.templates.wget

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.packages import packages
from hpccm.primitives.comment import comment
from hpccm.primitives.copy import copy
from hpccm.primitives.environment import environment
from hpccm.primitives.shell import shell

class nvshmem(bb_base, hpccm.templates.envvars,
              hpccm.templates.rm, hpccm.templates.tar, hpccm.templates.wget):
    """The `nvshmem` building block builds and installs the
    [NVSHMEM](https://developer.nvidia.com/nvshmem) component.

    # Parameters

    cuda: Flag to specify the CUDA path.  The default value is
    `/usr/local/cuda`.

    environment: Boolean flag to specify whether the environment
    (`CPATH`, `LIBRARY_PATH`, and `PATH`) should be modified to
    include NVSHMEM. The default is True.

    hydra: Boolean flag to specify whether the Hydra process launcher
    should be installed.  If True, adds `automake` to the list of OS
    packages.  The default is True.

    make_variables: List of environment variables and values, in `A=B`
    format, to set when building NVSHMEM.  The default is an empty
    list.

    mpi: Flag to specify the path to the MPI installation.  The
    default is empty, i.e., do not build NVSHMEM with MPI support.

    ospackages: List of OS packages to install prior to building.  The
    default values are `make` and `wget`.

    perftests: Boolean flag to specify whether the performance test
    programs should be built and installed.  The default is False.

    prefix: The top level install location.  The default value is
    `/usr/local/nvshmem`.

    tests: Boolean flag to specify whether the functionality test
    programs should be built and installed.  The default is False.

    version: The version of NVSHMEM source to download.  The default
    value is `x.y`.

    # Examples

    ```python
    nvshmem(prefix='/opt/nvshmem/x.y', version='x.y')
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(nvshmem, self).__init__(**kwargs)

        self.__baseurl = kwargs.get('baseurl', None)
        self.__cuda = kwargs.get('cuda', '/usr/local/cuda')
        self.__hydra = kwargs.get('hydra', True)
        self.__make_variables = kwargs.get('make_variables', [])
        self.__mpi = kwargs.get('mpi', None)
        self.__ospackages = kwargs.get('ospackages', ['make', 'wget'])
        self.__perftests = kwargs.get('perftests', False)
        self.__prefix = kwargs.get('prefix', '/usr/local/nvshmem')
        self.__tests = kwargs.get('tests', False)
        self.__version = kwargs.get('version', 'x.y')

        self.__commands = [] # Filled in by __setup()
        self.__wd = '/var/tmp' # working directory

        # Construct the series of steps to execute
        self.__setup()

        # Fill in container instructions
        self.__instructions()

    def __instructions(self):
        """Fill in container instructions"""

        self += comment('NVSHMEM version {}'.format(self.__version))
        self += packages(ospackages=self.__ospackages)
        self += shell(commands=self.__commands)
        self += environment(variables=self.environment_step())

    def __setup(self):
        """Construct the series of shell commands, i.e., fill in
           self.__commands"""

        # Download source from web
        # FIXME: remove baseurl guard and fixup url and tarball
        # details when install details are known
        if self.__baseurl:
            tarball = 'v{}.tar.gz'.format(self.__version)
            url = '{0}/{1}'.format(self.__baseurl, tarball)

            self.__commands.append(self.download_step(url=url,
                                                      directory=self.__wd))
            self.__commands.append(self.untar_step(
                tarball=posixpath.join(self.__wd, tarball),
                directory=self.__wd))

        # Configure
        env = ['NVSHMEM_PREFIX={}'.format(self.__prefix)]

        if self.__mpi:
          env.append('NVSHMEM_MPI_SUPPORT=1')
          env.append('MPI_HOME={}'.format(self.__mpi))

        if self.__make_variables:
          env.extend(self.__make_variables)

        env_string = ' '.join(sorted(env))

        # Build and install
        self.__commands.append('cd {}'.format(
            posixpath.join(self.__wd, 'nvshmem')))
        self.__commands.append('{} make -j$(nproc) install'.format(env_string))

        # Install Hydra process launcher
        if self.__hydra:
          self.__ospackages.append('automake')
          self.__commands.append(
              './scripts/install_hydra.sh $(pwd) {}'.format(self.__prefix))

        # Install performance tests
        if self.__perftests:
          perftests = 'NVSHMEM_PERFTEST_INSTALL={} make -C perftest -j$(nproc) install'.format(posixpath.join(self.__prefix, 'perftest'))
          if self.__mpi:
            self.__commands.append(
                'MPI_HOME={0} NVSHMEM_MPI_SUPPORT=1 {1}'.format(
                    self.__mpi, perftests))
          else:
            self.__commands.append(perftests)

        # Install functionality tests
        if self.__tests:
          tests = 'CUDA_HOME={0} NVSHMEM_HOME={1} TEST_INSTALL={2} make -C test -j$(nproc) install'.format(
              self.__cuda, self.__prefix,
              posixpath.join(self.__prefix, 'test'))
          if self.__mpi:
            self.__commands.append(
                'MPI_HOME={0} NVSHMEM_MPI_SUPPORT=1 {1}'.format(
                    self.__mpi, tests))
          else:
            self.__commands.append(tests)

        # Cleanup tarball and directory
        self.__commands.append(self.cleanup_step(
            items=[#posixpath.join(self.__wd, tarball), # FIXME
                   posixpath.join(self.__wd,
                                  'nvshmem')]))

        # Set the environment
        self.environment_variables['CPATH'] = '{}:$CPATH'.format(
            posixpath.join(self.__prefix, 'include'))
        self.environment_variables['LIBRARY_PATH'] = '{}:$LIBRARY_PATH'.format(
            posixpath.join(self.__prefix, 'lib'))
        self.environment_variables['PATH'] = '{}:$PATH'.format(
            posixpath.join(self.__prefix, 'bin'))

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples

        ```python
        n = nvshmem(...)
        Stage0 += n
        Stage1 += n.runtime()
        ```
        """
        instructions = []
        instructions.append(comment('NVSHMEM'))
        instructions.append(copy(_from=_from, src=self.__prefix,
                                 dest=self.__prefix))
        instructions.append(environment(variables=self.environment_step()))
        return '\n'.join(str(x) for x in instructions)
