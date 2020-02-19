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

"""Julia building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import posixpath
import re

import hpccm.config
import hpccm.templates.envvars
import hpccm.templates.ldconfig
import hpccm.templates.rm
import hpccm.templates.tar
import hpccm.templates.wget

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.packages import packages
from hpccm.common import cpu_arch
from hpccm.primitives.comment import comment
from hpccm.primitives.environment import environment
from hpccm.primitives.shell import shell

class julia(bb_base, hpccm.templates.envvars, hpccm.templates.ldconfig,
            hpccm.templates.rm, hpccm.templates.tar, hpccm.templates.wget):
    """The `julia` building block downloads and installs the
    [Julia](https://julialang.org) programming environment.

    # Parameters

    cuda: Boolean flag to specify whether the JuliaGPU packages should
    be installed.  If True, the `CUDAapi`, `CUDAdrv`, `CUDAnative`,
    and `CuArrays` packages are installed. Note that the `CUDAdrv`
    package must be rebuilt when the container is running to align
    with the host CUDA driver. The default is False.

    depot: Path to the location of "user" Julia package depot. The
    default is an empty string, i.e., `~/.julia`. The depot location
    needs to be writable by the user running the container.

    environment: Boolean flag to specify whether the environment
    (`LD_LIBRARY_PATH` and `PATH`) should be modified to include
    Julia. The default is True.

    history: Path to the Julia history file. The default value is an
    empty string, i.e., `~/.julia/logs/repl_history.jl`. The history
    location needs to be writable by the user running the container.

    ldconfig: Boolean flag to specify whether the Julia library
    directory should be added dynamic linker cache.  If False, then
    `LD_LIBRARY_PATH` is modified to include the Julia library
    directory. The default value is False.

    ospackages: List of OS packages to install prior to building. The
    default values are `tar` and `wget`.

    packages: List of Julia packages to install. The default is an
    empty list.

    prefix: The top level installation location.  The default value
    is `/usr/local/julia`.

    version: The version of Julia to install.  The default value is
    `1.3.1`.

    # Examples

    ```python
    julia(prefix='/usr/local/julia', version='1.3.1')
    ```

    ```python
    julia(depot='/tmp', history='/tmp/repl_history.jl')
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(julia, self).__init__(**kwargs)

        self.__arch_directory = None # Filled in by __cpu_arch()
        self.__arch_pkg = None # Filled in by __cpu_arch()
        self.__baseurl = kwargs.get('baseurl',
                                    'https://julialang-s3.julialang.org/bin/linux')
        self.__cuda = kwargs.get('cuda', False)
        self.__depot = kwargs.get('depot', None)
        self.__history = kwargs.get('history', None)
        self.__ospackages = kwargs.get('ospackages', ['tar', 'wget'])
        self.__packages = kwargs.get('packages', [])
        self.__prefix = kwargs.get('prefix', '/usr/local/julia')
        self.__version = kwargs.get('version', '1.3.1')

        self.__commands = [] # Filled in by __setup()
        self.__wd = '/var/tmp' # working directory

        # Set the CPU architecture specific parameters
        self.__cpu_arch()

        # Construct the series of steps to execute
        self.__setup()

        # Fill in container instructions
        self.__instructions()

    def __instructions(self):
        """Fill in container instructions"""

        self += comment('Julia version {}'.format(self.__version))
        self += packages(ospackages=self.__ospackages)
        self += shell(commands=self.__commands)
        self += environment(variables=self.environment_step())

    def __cpu_arch(self):
        """Based on the CPU architecture, set values accordingly.  A user
        specified value overrides any defaults."""

        if hpccm.config.g_cpu_arch == cpu_arch.AARCH64:
            self.__arch_directory = 'aarch64'
            self.__arch_pkg = 'aarch64'
        elif hpccm.config.g_cpu_arch == cpu_arch.X86_64:
            self.__arch_directory = 'x64'
            self.__arch_pkg = 'x86_64'
        else: # pragma: no cover
            raise RuntimeError('Unknown CPU architecture')

    def __setup(self):
        """Construct the series of shell commands, i.e., fill in
           self.__commands"""

        # The download URL has the format MAJOR.MINOR in the path and
        # the tarball contains MAJOR.MINOR.REVISION, so pull apart the
        # full version to get the individual components.
        match = re.match(r'(?P<major>\d+)\.(?P<minor>\d+)\.(?P<revision>\d+)',
                         self.__version)
        major_minor = '{0}.{1}'.format(match.groupdict()['major'],
                                       match.groupdict()['minor'])

        tarball = 'julia-{0}-linux-{1}.tar.gz'.format(self.__version,
                                                      self.__arch_pkg)
        url = '{0}/{1}/{2}/{3}'.format(self.__baseurl, self.__arch_directory,
                                       major_minor, tarball)

        # Download source from web
        self.__commands.append(self.download_step(url=url, directory=self.__wd))
        self.__commands.append(self.untar_step(
            tarball=posixpath.join(self.__wd, tarball), directory=self.__wd))

        # "Install"
        self.__commands.append('cp -a {0} {1}'.format(
            posixpath.join(self.__wd, 'julia-{}'.format(self.__version)),
            self.__prefix))

        # Install packages
        if self.__cuda:
            self.__packages.extend(['CUDAapi', 'CUDAdrv', 'CUDAnative',
                                    'CuArrays'])
        if self.__packages:
            # remove duplicates
            self.__packages = sorted(list(set(self.__packages)))
            # convert into PackageSpec() entries
            self.__packages = map(
                lambda pkg: 'PackageSpec(name="{0}")'.format(pkg)
                if not pkg.startswith('PackageSpec')
                else pkg, self.__packages)
            # Comma separated list of package
            packages_csv = ', '.join('{}'.format(pkg)
                                     for pkg in self.__packages)
            julia = posixpath.join(self.__prefix, 'bin', 'julia')
            # Install packages in the default location alongside Julia
            # itself.
            julia = 'JULIA_DEPOT_PATH={0} {1}'.format(
                posixpath.join(self.__prefix, 'share', 'julia'), julia)
            self.__commands.append(
                '{0} -e \'using Pkg; Pkg.add([{1}])\''.format(julia,
                                                              packages_csv))

        # Startup file
        if self.__depot:
            # The "user" depot path mist be writable by the user
            # running the container.  Modify the Julia startup file to
            # modify the "user" depot from ~/.julia to another
            # location.
            startup = posixpath.join(self.__prefix, 'etc', 'julia',
                                     'startup.jl')
            self.__commands.append('echo "DEPOT_PATH[1] = \\"{0}\\"" >> {1}'.format(
                self.__depot, startup))

        # Set library path
        libpath = posixpath.join(self.__prefix, 'lib')
        if self.ldconfig:
            self.__commands.append(self.ldcache_step(directory=libpath))
        else:
            self.environment_variables['LD_LIBRARY_PATH'] = '{}:$LD_LIBRARY_PATH'.format(libpath)

        # Cleanup tarball and directory
        self.__commands.append(self.cleanup_step(
            items=[posixpath.join(self.__wd, tarball),
                   posixpath.join(self.__wd, 'julia-{}'.format(self.__version))]))

        # Setup environment
        self.environment_variables['PATH'] = '{}:$PATH'.format(
            posixpath.join(self.__prefix, 'bin'))
        if self.__history:
            self.environment_variables['JULIA_HISTORY'] = self.__history

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples

        ```python
        j = julia(...)
        Stage0 += j
        Stage1 += j.runtime()
        ```
        """
        return str(self)
