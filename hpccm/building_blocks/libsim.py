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

"""libsim building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import posixpath

import hpccm.config
import hpccm.templates.envvars
import hpccm.templates.ldconfig
import hpccm.templates.rm
import hpccm.templates.wget

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.packages import packages
from hpccm.common import cpu_arch, linux_distro
from hpccm.primitives.comment import comment
from hpccm.primitives.copy import copy
from hpccm.primitives.environment import environment
from hpccm.primitives.shell import shell

class libsim(bb_base, hpccm.templates.envvars, hpccm.templates.ldconfig,
             hpccm.templates.rm, hpccm.templates.wget):
    """The `libsim` building block configures, builds, and installs the
    [VisIt
    Libsim](http://www.visitusers.org/index.php?title=Libsim_Batch)
    component.

    If GPU rendering will be used then a
    [cudagl](https://hub.docker.com/r/nvidia/cudagl) base image is
    recommended.

    # Parameters

    build_opts: List of VisIt build script options. The default values
    are `--xdb` and `--server-components-only`.

    environment: Boolean flag to specify whether the environment
    (`LD_LIBRARY_PATH` and `PATH`) should be modified to include
    Libsim. The default is True.

    ldconfig: Boolean flag to specify whether the Libsim library
    directories should be added dynamic linker cache.  If False, then
    `LD_LIBRARY_PATH` is modified to include the Libsim library
    directories. The default value is False.

    mpi: Boolean flag to specify whether Libsim should be built with
    MPI support.  VisIt uses MPI-1 routines that have been removed
    from the MPI standard; the MPI library may need to be built with
    special compatibility options, e.g., `--enable-mpi1-compatibility`
    for OpenMPI.  If True, then the build script options `--parallel`
    and `--no-icet` are added and the environment variable
    `PAR_COMPILER` is set to `mpicc`. If True, a MPI library building
    block should be installed prior this building block.  The default
    value is True.

    ospackages: List of OS packages to install prior to configuring
    and building.  For Ubuntu, the default values are `gzip`, `make`,
    `patch`, `tar`, `wget`, `zlib1g-dev`, `libxt-dev`,
    `libgl1-mesa-dev`, and `libglu1-mesa-dev`.  For RHEL-based Linux
    distributions, the default values are `gzip`, `make`, `patch`,
    `tar`, `wget`, `which`, `zlib-devel`, `libXt-devel`,
    `libglvnd-devel`, `mesa-libGL-devel`, and `mesa-libGLU-devel`.

    prefix: The top level install location.  The default value is
    `/usr/local/visit`.

    system_cmake: Boolean flag to specify whether the system provided
    cmake should be used.  If False, then the build script downloads a
    private copy of cmake.  If True, then the build script option
    `--system-cmake` is added.  If True, then the [cmake](#cmake)
    building block should be installed prior to this building block.
    The default is True.

    system_python: Boolean flag to specify whether the system provided
    python should be used.  If False, then the build script downloads
    a private copy of python.  If True, then the build script option
    `--system-python` is added.  If True, then the [Python](#python)
    building block should be installed with development libraries
    prior to this building block.  The default is True.

    thirdparty: Boolean flag to specify whether third-party components
    included by the build script should be retained.  If True, then
    the build script option `--thirdparty-path` is added and set to
    `<prefix>/third-party`.  The default is True.

    version: The version of Libsim source to download.  The default
    value is `2.13.3`.

    # Examples

    ```python
    libsim(prefix='/opt/libsim', version='2.13.3')
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(libsim, self).__init__(**kwargs)

        self.__arch = None # Filled in by __cpu_arch()
        self.__buildscript = r'build_visit{0}'
        self.__mpi = kwargs.get('mpi', True)
        self.__opts = kwargs.get('build_opts',
                                 ['--xdb', '--server-components-only'])
        self.__ospackages = kwargs.get('ospackages', [])
        self.__parallel = kwargs.get('parallel', '$(nproc)')
        self.__prefix = kwargs.get('prefix', '/usr/local/visit')
        self.__runtime_ospackages = [] # Filled in by __distro()
        self.__system_cmake = kwargs.get('system_cmake', True)
        self.__system_python = kwargs.get('system_python', True)
        self.__thirdparty = kwargs.get('thirdparty', True)
        self.__version = kwargs.get('version', '2.13.3')
        self.__url = r'http://portal.nersc.gov/project/visit/releases/{0}/{1}'

        self.__commands = [] # Filled in by __setup()
        self.__wd = '/var/tmp/visit' # working directory

        # Set the CPU architecture specific parameters
        self.__cpu_arch()

        # Set the Linux distribution specific parameters
        self.__distro()

        # Construct the series of steps to execute
        self.__setup()

        # Fill in container instructions
        self.__instructions()

    def __instructions(self):
        """Fill in container instructions"""

        self += comment('VisIt libsim version {}'.format(self.__version))
        self += packages(ospackages=self.__ospackages)
        self += shell(commands=self.__commands)
        self += environment(variables=self.environment_step())

    def __cpu_arch(self):
        """Based on the CPU architecture, set values accordingly.  A user
        specified value overrides any defaults."""

        if hpccm.config.g_cpu_arch == cpu_arch.AARCH64:
            # Bug in the VisIt build config
            self.__arch = 'linux-intel'
        elif hpccm.config.g_cpu_arch == cpu_arch.X86_64:
            self.__arch = 'linux-x86_64'
        else: # pragma: no cover
            raise RuntimeError('Unknown CPU architecture')

    def __distro(self):
        """Based on the Linux distribution, set values accordingly.  A user
        specified value overrides any defaults."""

        if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
            if not self.__ospackages:
                self.__ospackages = ['gzip', 'make', 'patch', 'tar', 'wget',
                                     'zlib1g-dev', 'libxt-dev',
                                     'libgl1-mesa-dev', 'libglu1-mesa-dev']
            self.__runtime_ospackages = ['libxt6', 'libgl1-mesa-glx',
                                         'libglu1-mesa', 'zlib1g']
        elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
            if not self.__ospackages:
                self.__ospackages = ['gzip', 'make', 'patch', 'tar', 'wget',
                                     'which', 'zlib-devel', 'libXt-devel',
                                     'libglvnd-devel', 'mesa-libGL-devel',
                                     'mesa-libGLU-devel']
            self.__runtime_ospackages = ['libXt', 'libglvnd', 'mesa-libGL',
                                         'mesa-libGLU', 'zlib']
        else: # pragma: no cover
            raise RuntimeError('Unknown Linux distribution')

    def __setup(self):
        """Construct the series of shell commands, i.e., fill in
           self.__commands"""

        # The download URL format contains MAJOR.MINOR.REVSION and
        # MAJOR_MINOR_REVISION
        buildscript = self.__buildscript.format(
            self.__version.replace('.', '_'))
        url = self.__url.format(self.__version, buildscript)

        # Download source from web
        self.__commands.append(self.download_step(url=url, directory=self.__wd))

        # Set options
        env = []
        opts = self.__opts
        if self.__mpi:
            env.append('PAR_COMPILER=mpicc')
            opts.extend(['--parallel', '--no-icet'])
        if self.__parallel:
            opts.append('--makeflags -j{}'.format(self.__parallel))
        if self.__prefix:
            opts.append('--prefix {}'.format(self.__prefix))
        if self.__system_cmake:
            opts.append('--system-cmake')
        if self.__system_python:
            opts.append('--system-python')
        if self.__thirdparty:
            thirdparty_path = posixpath.join(self.__prefix, 'third-party')
            opts.append('--thirdparty-path {}'.format(thirdparty_path))
            self.__commands.append('mkdir -p {}'.format(thirdparty_path))

        # Build
        self.__commands.append('cd {0} && {1} bash {2} {3}'.format(
            self.__wd, ' '.join(env), buildscript, ' '.join(opts)))

        # Set library path
        libpath = posixpath.join(self.__prefix, self.__version, self.__arch)
        suffix1 = 'lib'
        suffix2 = posixpath.join('libsim', 'V2', 'lib')
        if self.ldconfig:
            self.__commands.append(self.ldcache_step(
                directory=posixpath.join(libpath, suffix1)))
            self.__commands.append(self.ldcache_step(
                directory=posixpath.join(libpath, suffix2)))
        else:
            self.environment_variables['LD_LIBRARY_PATH'] = '{0}:{1}:$LD_LIBRARY_PATH'.format(posixpath.join(libpath, suffix1), posixpath.join(libpath, suffix2))

        # Cleanup
        self.__commands.append(self.cleanup_step(
            items=[posixpath.join(self.__wd)]))

        # Set the environment
        self.environment_variables['PATH'] = '{}:$PATH'.format(
            posixpath.join(self.__prefix, 'bin'))

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples
        ```python
        l = libsim(...)
        Stage0 += l
        Stage1 += l.runtime()
        ```
        """
        instructions = []
        instructions.append(comment('VisIt libsim'))
        if self.__runtime_ospackages:
            instructions.append(packages(ospackages=self.__runtime_ospackages))
        instructions.append(copy(_from=_from, src=self.__prefix,
                                 dest=self.__prefix))
        if self.ldconfig:
            libpath = posixpath.join(self.__prefix, self.__version,
                                     self.__arch)
            suffix1 = 'lib'
            suffix2 = posixpath.join('libsim', 'V2', 'lib')
            instructions.append(shell(
                commands=[self.ldcache_step(directory=posixpath.join(libpath,
                                                                     suffix1)),
                          self.ldcache_step(
                              directory=posixpath.join(libpath, suffix2))]))
        instructions.append(environment(variables=self.environment_step()))
        return '\n'.join(str(x) for x in instructions)
