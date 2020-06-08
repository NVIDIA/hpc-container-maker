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

import logging
import posixpath

import hpccm.config
import hpccm.templates.envvars
import hpccm.templates.rm
import hpccm.templates.sed
import hpccm.templates.tar

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.intel_psxe_runtime import intel_psxe_runtime
from hpccm.building_blocks.packages import packages
from hpccm.common import cpu_arch, linux_distro
from hpccm.primitives.comment import comment
from hpccm.primitives.copy import copy
from hpccm.primitives.environment import environment
from hpccm.primitives.shell import shell
from hpccm.toolchain import toolchain

class intel_psxe(bb_base, hpccm.templates.envvars, hpccm.templates.rm,
                 hpccm.templates.sed, hpccm.templates.tar):
    """The `intel_psxe` building block installs [Intel Parallel Studio
    XE](https://software.intel.com/en-us/parallel-studio-xe).

    You must agree to the [Intel End User License Agreement](https://software.intel.com/en-us/articles/end-user-license-agreement)
    to use this building block.

    # Parameters

    components: List of Intel Parallel Studio XE components to
    install.  The default values is `DEFAULTS`.  If only the Intel C++
    and Fortran compilers are desired, then use `intel-icc__x86_64`
    and `intel-ifort__x86_64`.  Please note that the values are not
    consistent between versions; for a list of components, extract
    `pset/mediaconfig.xml` from the tarball and grep for `Abbr`.

    daal: Boolean flag to specify whether the Intel Data Analytics
    Acceleration Library environment should be configured when
    `psxevars` is False.  This flag also controls whether to install
    the corresponding runtime in the `runtime` method.  Note: this
    flag does not control whether the developer environment is
    installed; see `components`.  The default is True.

    environment: Boolean flag to specify whether the environment
    (`LD_LIBRARY_PATH`, `PATH`, and others) should be modified to
    include Intel Parallel Studio XE. `psxevars` has precedence. The
    default is True.

    eula: By setting this value to `True`, you agree to the [Intel End User License Agreement](https://software.intel.com/en-us/articles/end-user-license-agreement).
    The default value is `False`.

    icc: Boolean flag to specify whether the Intel C++ Compiler
    environment should be configured when `psxevars` is False.  This
    flag also controls whether to install the corresponding runtime in
    the `runtime` method.  Note: this flag does not control whether
    the developer environment is installed; see `components`.  The
    default is True.

    ifort: Boolean flag to specify whether the Intel Fortran Compiler
    environment should be configured when `psxevars` is False.  This
    flag also controls whether to install the corresponding runtime in
    the `runtime` method.  Note: this flag does not control whether
    the developer environment is installed; see `components`.  The
    default is True.

    ipp: Boolean flag to specify whether the Intel Integrated
    Performance Primitives environment should be configured when
    `psxevars` is False.  This flag also controls whether to install
    the corresponding runtime in the `runtime` method.  Note: this
    flag does not control whether the developer environment is
    installed; see `components`.  The default is True.

    license: The license to use to activate Intel Parallel Studio XE.
    If the string contains a `@` the license is interpreted as a
    network license, e.g., `12345@lic-server`.  Otherwise, the string
    is interpreted as the path to the license file relative to the
    local build context.  The default value is empty.  While this
    value is not required, the installation is unlikely to be
    successful without a valid license.

    mkl: Boolean flag to specify whether the Intel Math Kernel Library
    environment should be configured when `psxevars` is False.  This
    flag also controls whether to install the corresponding runtime in
    the `runtime` method.  Note: this flag does not control whether
    the developer environment is installed; see `components`.  The
    default is True.

    mpi: Boolean flag to specify whether the Intel MPI Library
    environment should be configured when `psxevars` is False.  This
    flag also controls whether to install the corresponding runtime in
    the `runtime` method.  Note: this flag does not control whether
    the developer environment is installed; see `components`.  The
    default is True.

    ospackages: List of OS packages to install prior to installing
    Intel MPI.  For Ubuntu, the default values are `build-essential`
    and `cpio`.  For RHEL-based Linux distributions, the default
    values are `gcc`, `gcc-c++`, `make`, and `which`.

    prefix: The top level install location.  The default value is
    `/opt/intel`.

    psxevars: Intel Parallel Studio XE provides an environment script
    (`compilervars.sh`) to setup the environment.  If this value is
    `True`, the bashrc is modified to automatically source this
    environment script.  However, the Intel runtime environment is not
    automatically available to subsequent container image build steps;
    the environment is available when the container image is run.  To
    set the Intel Parallel Studio XE environment in subsequent build
    steps you can explicitly call `source
    /opt/intel/compilers_and_libraries/linux/bin/compilervars.sh
    intel64` in each build step.  If this value is to set `False`,
    then the environment is set such that the environment is visible
    to both subsequent container image build steps and when the
    container image is run.  However, the environment may differ
    slightly from that set by `compilervars.sh`. This option will be
    used with the `runtime` method. The default value is
    `True`.

    runtime_version: The version of Intel Parallel Studio XE runtime
    to install via the `runtime` method.  The runtime is installed
    using the [intel_psxe_runtime](#intel_psxe_runtime) building
    block.  This value is passed as its `version` parameter.  In
    general, the major version of the runtime should correspond to the
    tarball version.  The default value is `2020.1-12`.

    tarball: Path to the Intel Parallel Studio XE tarball relative to
    the local build context.  The default value is empty.  This
    parameter is required.

    tbb: Boolean flag to specify whether the Intel Threading Building
    Blocks environment should be configured when `psxevars` is False.
    This flag also controls whether to install the corresponding
    runtime in the `runtime` method.  Note: this flag does not control
    whether the developer environment is installed; see `components`.
    The default is True.

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

        super(intel_psxe, self).__init__(**kwargs)

        # By setting this value to True, you agree to the
        # corresponding Intel End User License Agreement
        # (https://software.intel.com/en-us/articles/end-user-license-agreement)
        self.__eula = kwargs.get('eula', False)

        self.__components = kwargs.get('components', ['DEFAULTS'])
        self.__daal = kwargs.get('daal', True)
        self.__icc = kwargs.get('icc', True)
        self.__ifort = kwargs.get('ifort', True)
        self.__ipp = kwargs.get('ipp', True)
        self.__license = kwargs.get('license', None)
        self.__mkl = kwargs.get('mkl', True)
        self.__mpi = kwargs.get('mpi', True)
        self.__ospackages = kwargs.get('ospackages', [])
        self.__prefix = kwargs.get('prefix', '/opt/intel')
        self.__psxevars = kwargs.get('psxevars', True)
        self.__runtime_version = kwargs.get('runtime_version', '2020.1-12')
        self.__tarball = kwargs.get('tarball', None)
        self.__tbb = kwargs.get('tbb', True)
        self.__wd = '/var/tmp' # working directory

        self.toolchain = toolchain(CC='icc', CXX='icpc', F77='ifort',
                                   F90='ifort', FC='ifort')

        self.__bashrc = ''   # Filled in by __distro()
        self.__commands = [] # Filled in by __setup()

        if hpccm.config.g_cpu_arch != cpu_arch.X86_64: # pragma: no cover
            logging.warning('Using intel_psxe on a non-x86_64 processor')

        # Set the Linux distribution specific parameters
        self.__distro()

        # Construct the series of steps to execute
        self.__setup()

        # Fill in container instructions
        self.__instructions()

    def __instructions(self):
        """Fill in container instructions"""

        self += comment('Intel Parallel Studio XE')
        self += packages(ospackages=self.__ospackages)
        self += copy(src=self.__tarball,
                     dest=posixpath.join(self.__wd, self.__tarball_name))
        if self.__license and not '@' in self.__license:
            # License file
            self += copy(src=self.__license,
                         dest=posixpath.join(self.__wd, 'license.lic'))
        self += shell(commands=self.__commands)

        if self.__psxevars:
            # Source the mpivars environment script when starting the
            # container, but the variables not be available for any
            # subsequent build steps.
            self += shell(commands=['echo "source {0}/compilers_and_libraries/linux/bin/compilervars.sh intel64" >> {1}'.format(self.__prefix, self.__bashrc)])
        else:
            self += environment(variables=self.environment_step())

    def __distro(self):
        """Based on the Linux distribution, set values accordingly.  A user
        specified value overrides any defaults."""

        if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
            if not self.__ospackages:
                self.__ospackages = ['build-essential', 'cpio']
            self.__bashrc = '/etc/bash.bashrc'
        elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
            if not self.__ospackages:
                self.__ospackages = ['gcc', 'gcc-c++', 'make', 'which']
            self.__bashrc = '/etc/bashrc'
        else: # pragma: no cover
            raise RuntimeError('Unknown Linux distribution')

    def __environment(self):
        basepath = posixpath.join(self.__prefix, 'compilers_and_libraries',
                                  'linux')
        cpath = []
        ld_library_path = []
        library_path = []
        path = []
        env = {}

        if self.__daal:
            env['DAALROOT'] = posixpath.join(basepath, 'daal')
            cpath.append(posixpath.join(basepath, 'daal', 'include'))
            ld_library_path.append(posixpath.join(basepath, 'daal', 'lib',
                                                  'intel64'))
            library_path.append(posixpath.join(basepath, 'daal', 'lib',
                                               'intel64'))

        if self.__icc:
            cpath.append(posixpath.join(basepath, 'pstl', 'include'))
            ld_library_path.append(posixpath.join(basepath, 'compiler', 'lib',
                                                  'intel64'))
            path.append(posixpath.join(basepath, 'bin', 'intel64'))

        if self.__ifort:
            ld_library_path.append(posixpath.join(basepath, 'compiler', 'lib',
                                                  'intel64'))
            path.append(posixpath.join(basepath, 'bin', 'intel64'))

        if self.__ipp:
            env['IPPROOT' ] = posixpath.join(basepath, 'ipp')
            cpath.append(posixpath.join(basepath, 'ipp', 'include'))
            ld_library_path.append(posixpath.join(basepath, 'ipp', 'lib',
                                                  'intel64'))
            library_path.append(posixpath.join(basepath, 'ipp', 'lib',
                                               'intel64'))

        if self.__mkl:
            env['MKLROOT'] = posixpath.join(basepath, 'mkl')
            cpath.append(posixpath.join(basepath, 'mkl', 'include'))
            ld_library_path.append(posixpath.join(basepath, 'mkl', 'lib',
                                                'intel64'))
            library_path.append(posixpath.join(basepath, 'mkl', 'lib',
                                               'intel64'))

        if self.__mpi:
            # Handle libfabics case
            env['I_MPI_ROOT' ] = posixpath.join(basepath, 'mpi')
            cpath.append(posixpath.join(basepath, 'mpi', 'include'))
            ld_library_path.append(posixpath.join(basepath, 'mpi', 'intel64',
                                                  'lib'))
            path.append(posixpath.join(basepath, 'mpi', 'intel64', 'bin'))

        if self.__tbb:
            cpath.append(posixpath.join(basepath, 'tbb', 'include'))
            ld_library_path.append(posixpath.join(basepath, 'tbb', 'lib',
                                                  'intel64', 'gcc4.7'))
            library_path.append(posixpath.join(basepath, 'tbb', 'lib',
                                               'intel64', 'gcc4.7'))

        if cpath:
            cpath.append('$CPATH')
            env['CPATH'] = ':'.join(cpath)

        if library_path:
            library_path.append('$LIBRARY_PATH')
            env['LIBRARY_PATH'] = ':'.join(library_path)

        if ld_library_path:
            ld_library_path.append('$LD_LIBRARY_PATH')
            env['LD_LIBRARY_PATH'] = ':'.join(ld_library_path)

        if path:
            path.append('$PATH')
            env['PATH'] = ':'.join(path)

        return env

    def __setup(self):
        """Construct the series of shell commands, i.e., fill in
           self.__commands"""

        # tarball must be specified
        if not self.__tarball:
            raise RuntimeError('Intel PSXE tarball not specified')

        # Get the name of the directory that created when the tarball
        # is extracted.  Assume it is the same as the basename of the
        # tarball.
        self.__tarball_name = posixpath.basename(self.__tarball)
        basedir = posixpath.splitext(self.__tarball_name)[0]

        # Untar
        self.__commands.append(self.untar_step(
            tarball=posixpath.join(self.__wd, self.__tarball_name),
            directory=(self.__wd)))

        # Configure silent install
        silent_cfg=[
            r's/^#\?\(COMPONENTS\)=.*/\1={}/g'.format(
                ';'.join(self.__components)),
            r's|^#\?\(PSET_INSTALL_DIR\)=.*|\1={}|g'.format(self.__prefix)]

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
            silent_cfg.append(r's|^#\?\(ACTIVATION_LICENSE_FILE\)=.*|\1={}|g'.format(posixpath.join(self.__wd, 'license.lic')))
        else:
            # No license, will most likely not work
            logging.warning('No Intel Parallel Studio XE license specified')

        # Update the silent config file
        self.__commands.append(self.sed_step(
            file=posixpath.join(self.__wd, basedir, 'silent.cfg'),
            patterns=silent_cfg))

        # Install
        self.__commands.append(
            'cd {} && ./install.sh --silent=silent.cfg'.format(
                posixpath.join(self.__wd, basedir)))

        # Cleanup runfile
        self.__commands.append(self.cleanup_step(
            items=[posixpath.join(self.__wd, self.__tarball_name),
                   posixpath.join(self.__wd, basedir)]))

        # Set the environment
        self.environment_variables = self.__environment()

    def runtime(self, _from='0'):
        """Install the runtime from a full build in a previous stage"""
        return str(intel_psxe_runtime(daal=self.__daal,
                                      eula=self.__eula,
                                      icc=self.__icc,
                                      ifort=self.__ifort,
                                      ipp=self.__ipp,
                                      mkl=self.__mkl,
                                      mpi=self.__mpi,
                                      psxevars=self.__psxevars,
                                      tbb=self.__tbb,
                                      version=self.__runtime_version))
