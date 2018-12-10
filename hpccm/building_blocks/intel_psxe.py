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

"""Intel Parallel Studio XE building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import os
import re

from hpccm.building_blocks.packages import packages
from hpccm.primitives.comment import comment
from hpccm.primitives.copy import copy
from hpccm.primitives.environment import environment
from hpccm.primitives.shell import shell
from hpccm.templates.rm import rm
from hpccm.templates.sed import sed
from hpccm.templates.tar import tar
from hpccm.toolchain import toolchain

class intel_psxe(rm, sed, tar):
    """The `intel_psxe` building block installs [Intel Parallel Studio
    XE](https://software.intel.com/en-us/parallel-studio-xe).

    You must agree to the [Intel End User License Agreement](https://software.intel.com/en-us/articles/end-user-license-agreement)
    to use this building block.

    As a side effect, this building block modifies `PATH` and
    `LD_LIBRARY_PATH`.

    # Parameters

    components: List of Intel Parallel Studio XE components to
    install.  The default values are `intel-icc__x86_64` and
    `intel-ifort__x86_64`, i.e., install the Intel C++ and Fortran
    compilers only.  Please note that the values are not consistent
    between versions; for a list of components, extract
    `pset/mediaconfig.xml` from the tarball and grep for `Abbr`.  The
    default values correspond to Intel Parallel Studio XE 2018.

    eula: By setting this value to `True`, you agree to the [Intel End User License Agreement](https://software.intel.com/en-us/articles/end-user-license-agreement).
    The default value is `False`.

    license: The license to use to activate Intel Parallel Studio XE.
    If the string contains a `@` the license is interpreted as a
    network license, e.g., `12345@lic-server`.  Otherwise, the string
    is interpreted as the path to the license file relative to the
    local build context.  The default value is empty.  While this
    value is not required, the installation is unlikely to be
    successful without a valid license.

    ospackages: List of OS packages to install prior to installing
    Intel Parallel Studio XE.  The default value is `cpio`.

    prefix: The top level install location.  The default value is
    `/opt/intel`.

    tarball: Path to the Intel Parallel Studio XE tarball relative to
    the local build context.  The default value is empty.  This
    parameter is required.

    # Examples

    ```python
    intel_psxe(eula=True, license='XXXXXXXX.lic',
               tarball='parallel_studio_xe_2018_update1_professional_edition.tgz')
    ```

    ```python
    i = intel_psxe(...)
    openmpi(..., toolchain=i.toolchain, ...)
    ```
    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        # Trouble getting MRO with kwargs working correctly, so just call
        # the parent class constructors manually for now.
        #super(intel_psxe, self).__init__(**kwargs)
        rm.__init__(self, **kwargs)
        sed.__init__(self, **kwargs)
        tar.__init__(self, **kwargs)

        # By setting this value to True, you agree to the
        # corresponding Intel End User License Agreement
        # (https://software.intel.com/en-us/articles/end-user-license-agreement)
        self.__eula = kwargs.get('eula', False)

        self.__components = kwargs.get('components', ['intel-icc__x86_64',
                                                      'intel-ifort__x86_64'])
        self.__license = kwargs.get('license', None)
        self.__ospackages = kwargs.get('ospackages', ['cpio'])
        self.__prefix = kwargs.get('prefix', '/opt/intel')
        self.__tarball = kwargs.get('tarball', None)
        self.__wd = '/var/tmp' # working directory

        self.toolchain = toolchain(CC='icc', CXX='icpc', F77='ifort',
                                   F90='ifort', FC='ifort')

        self.__commands = [] # Filled in by __setup()
        self.__environment_variables = {
            'PATH': '{}:$PATH'.format(os.path.join(self.__prefix, 'bin')),
            'LD_LIBRARY_PATH': '{}:$LD_LIBRARY_PATH'.format(
                os.path.join(self.__prefix, 'lib', 'intel64'))}

        # Construct the series of steps to execute
        self.__setup()

    def __str__(self):
        """String representation of the building block"""
        instructions = []
        instructions.append(comment('Intel Parallel Studio XE'))
        instructions.append(packages(ospackages=self.__ospackages))
        instructions.append(copy(src=self.__tarball,
                                 dest=os.path.join(self.__wd, self.__tarball)))
        if self.__license and not '@' in self.__license:
            # License file
            instructions.append(
                copy(src=self.__license,
                     dest=os.path.join(self.__wd, 'license.lic')))
        instructions.append(shell(commands=self.__commands))
        instructions.append(
            environment(variables=self.__environment_variables))

        return '\n'.join(str(x) for x in instructions)

    def __setup(self):
        """Construct the series of shell commands, i.e., fill in
           self.__commands"""

        # tarball must be specified
        if not self.__tarball:
            raise RuntimeError('Intel PSXE tarball not specified')

        # Get the name of the directory that created when the tarball
        # is extracted.  Assume it is the same as the basename of the
        # tarball.
        basedir = os.path.splitext(self.__tarball)[0]

        # Untar
        self.__commands.append(self.untar_step(
            tarball=os.path.join(self.__wd, self.__tarball),
            directory=(self.__wd)))

        # Configure silent install
        silent_cfg=[r's/^#\?\(COMPONENTS\)=.*/\1={}/g'.format(
            ';'.join(self.__components)),
                    r's|^#\?\(PSET_INSTALL_DIR\)=.*|\1={}|g'.format(
                        self.__prefix)]

        # EULA acceptance
        if self.__eula:
            silent_cfg.append(r's/^#\?\(ACCEPT_EULA\)=.*/\1=accept/g')

        # License activation
        if self.__license and '@' in self.__license:
            # License server
            silent_cfg.append(r's/^#\?\(ACTIVATION_TYPE\)=.*/\1=license_server/g')
            silent_cfg.append(r's/^#\?\(ACTIVATION_LICENSE_FILE\)=.*/\1={}/g'.format(self.__license))
        elif self.__license:
            # License file
            silent_cfg.append(r's/^#\?\(ACTIVATION_TYPE\)=.*/\1=license_file/g')
            silent_cfg.append(r's|^#\?\(ACTIVATION_LICENSE_FILE\)=.*|\1={}|g'.format(os.path.join(self.__wd, 'license.lic')))
        else:
            # No license, will most likely not work
            logging.warning('No Intel Parallel Studio XE license specified')

        # Update the silent config file
        self.__commands.append(self.sed_step(
            file=os.path.join(self.__wd, basedir, 'silent.cfg'),
            patterns=silent_cfg))

        # Install
        self.__commands.append(
            'cd {} && ./install.sh --silent=silent.cfg'.format(
                os.path.join(self.__wd, basedir)))

        # Extract the redistributable runtime libraries so they can be
        # copied later into the runtime container layer.  Docker
        # cannot handle the combination of symlink directories and
        # wildcards, so cannot copy this directly from
        # /opt/intel/lib/intel64.
        self.__commands.append('mkdir -p {0} && cp -a {1} {0}'.format(
            os.path.join(self.__wd, 'intel_psxe_runtime'),
            os.path.join(self.__prefix, 'lib', 'intel64', '*.so*')))

        # Cleanup runfile
        self.__commands.append(self.cleanup_step(
            items=[os.path.join(self.__wd, self.__tarball),
                   os.path.join(self.__wd, basedir)]))

    def runtime(self, _from='0'):
        """Install the runtime from a full build in a previous stage"""
        instructions = []
        instructions.append(comment('Intel Parallel Studio XE'))
        instructions.append(
            copy(_from=_from,
                 src=os.path.join(self.__wd, 'intel_psxe_runtime/*'),
                 dest=os.path.join(self.__prefix, 'lib', 'intel64', '')))
        instructions.append(environment(
            variables={'LD_LIBRARY_PATH': '{}:$LD_LIBRARY_PATH'.format(
                os.path.join(self.__prefix, 'lib', 'intel64'))}))
        return '\n'.join(str(x) for x in instructions)
