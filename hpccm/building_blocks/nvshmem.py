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
import os
import posixpath

import hpccm.templates.envvars
import hpccm.templates.rm
import hpccm.templates.tar

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.generic_build import generic_build
from hpccm.building_blocks.packages import packages
from hpccm.primitives.comment import comment
from hpccm.primitives.copy import copy
from hpccm.primitives.environment import environment
from hpccm.primitives.shell import shell

class nvshmem(bb_base, hpccm.templates.envvars, hpccm.templates.rm,
              hpccm.templates.tar):
    """The `nvshmem` building block builds and installs the
    [NVSHMEM](https://developer.nvidia.com/nvshmem) component.

    # Parameters

    binary_tarball: Path to NVSHMEM binary tarball relative to the
    build context. The default value is empty. Either this parameter
    or `package` must be specified.

    environment: Boolean flag to specify whether the environment
    (`CPATH`, `LIBRARY_PATH`, and `PATH`) should be modified to
    include NVSHMEM. The default is True.

    gdrcopy: Flag to specify the path to the GDRCOPY installation.
    The default is empty.

    hydra: Boolean flag to specify whether the Hydra process launcher
    should be installed.  If True, adds `automake` to the list of OS
    packages.  The default is False.

    make_variables: Dictionary of environment variables and values to
    set when building NVSHMEM.  The default is an empty dictionary.

    mpi: Flag to specify the path to the MPI installation.  The
    default is empty, i.e., do not build NVSHMEM with MPI support.

    ospackages: List of OS packages to install prior to building.  The
    default values are `make` and `wget`.

    package: Path to the NVSHMEM source package relative to the build
    context. The default value is empty. Either this parameter or
    `binary_tarball` must be specified.

    prefix: The top level install location.  The default value is
    `/usr/local/nvshmem`.

    shmem: Flag to specify the path to the SHMEM installation.  The
    default is empty, i.e., do not build NVSHMEM with SHMEM support.

    # Examples

    ```python
    nvshmem(binary_tarball='nvshmem_0.4.1-0+cuda10_x86_64.txz')
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(nvshmem, self).__init__(**kwargs)

        self.__binary_tarball = kwargs.pop('binary_tarball', None)
        self.__gdrcopy = kwargs.pop('gdrcopy', None)
        self.__hydra = kwargs.pop('hydra', False)
        self.__make_variables = kwargs.pop('make_variables', {})
        self.__mpi = kwargs.pop('mpi', None)
        self.__ospackages = kwargs.pop('ospackages', ['make', 'wget'])
        self.__prefix = kwargs.pop('prefix', '/usr/local/nvshmem')
        self.__shmem = kwargs.pop('shmem', None)
        self.__wd = '/var/tmp' # working directory

        # Setup the environment variables
        self.environment_variables['CPATH'] = '{}:$CPATH'.format(
            posixpath.join(self.__prefix, 'include'))
        self.environment_variables['LIBRARY_PATH'] = '{}:$LIBRARY_PATH'.format(
            posixpath.join(self.__prefix, 'lib'))
        self.environment_variables['PATH'] = '{}:$PATH'.format(
            posixpath.join(self.__prefix, 'bin'))

        # Add packages
        if self.__hydra:
            self.__ospackages.append('automake')

        self += comment('NVSHMEM')
        self += packages(ospackages=self.__ospackages)

        if self.__binary_tarball:
            # Shorthand for the tarball file inside the container
            tarball = posixpath.join(self.__wd,
                                     os.path.basename(self.__binary_tarball))

            self += copy(src=self.__binary_tarball, dest=tarball)
            self += shell(commands=[
                # Untar binary package
                self.untar_step(
                    tarball=tarball,
                    # remove the leading directory, e.g., install in
                    # /usr/local/nvshmem not
                    # /usr/local/nvshmem/nvshmem_<version>_<arch>.
                    args=['--strip-components=1'],
                    directory=self.__prefix),
                # Install Hydra process launcher
                '{0}/scripts/install_hydra.sh {1} {0}'.format(
                    self.__prefix, self.__wd) if self.__hydra else None,
                # Remove temporary files and cleanup
                self.cleanup_step(items=[tarball])])
            self += environment(variables=self.environment_variables)

        else:
            # Build from source

            # Set the build options
            self.__configure()

            self.__bb = generic_build(
                build = [
                    '{} make -j$(nproc) install'.format(
                        self.__build_environment),
                    './scripts/install_hydra.sh {1} {0}'.format(
                        self.__prefix, self.__wd) if self.__hydra else None],
                comment=False,
                devel_environment=self.environment_variables,
                prefix=self.__prefix,
                runtime_environment=self.environment_variables,
                **kwargs)
            self += self.__bb

    def __configure(self):
        """Setup build options based on user parameters"""

        e = {}

        e['NVSHMEM_PREFIX'] = self.__prefix

        if self.__gdrcopy:
            e['GDRCOPY_HOME'] = self.__gdrcopy

        if self.__mpi:
            e['NVSHMEM_MPI_SUPPORT'] = 1
            e['MPI_HOME'] = self.__mpi

        if self.__shmem:
            e['NVSHMEM_SHMEM_SUPPORT'] = 1
            e['SHMEM_HOME'] = self.__shmem

        if self.__make_variables:
          e.update(self.__make_variables)

        l = []
        if e:
            for key, val in sorted(e.items()):
                l.append('{0}={1}'.format(key, val))

        self.__build_environment = ' '.join(l)

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
        if self.__binary_tarball:
            instructions.append(copy(_from=_from, src=self.__prefix,
                                     dest=self.__prefix))
            instructions.append(environment(variables=self.environment_step()))
        else:
            instructions.append(self.__bb.runtime(_from=_from))
        return '\n'.join(str(x) for x in instructions)
