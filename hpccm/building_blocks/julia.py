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

import logging # pylint: disable=unused-import
import posixpath
import re

import hpccm.config
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

class julia(bb_base, hpccm.templates.ldconfig, hpccm.templates.rm,
            hpccm.templates.tar, hpccm.templates.wget):
    """The `julia` building block downloads and installs the
    [Julia](https://julialang.org) programming environment.

    # Parameters

    cuda: Boolean flag to specify whether the JuliaGPU packages should
    be installed.  If True, the `CUDAnative`, `CuArrays`, and
    `GPUArrays` packages are installed. Note that the `CUDAdrv`
    package must be rebuilt when container the container to align with
    the host CUDA driver. The default is False.

    depot: Path to the location of Julia packages. The default value
    is an empty string.

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
    `1.1.0`.

    # Examples

    ```python
    julia(prefix='/usr/local/julia', version='1.1.0')
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(julia, self).__init__(**kwargs)

        self.__baseurl = kwargs.get('baseurl',
                                    'https://julialang-s3.julialang.org/bin/linux/x64')
        self.__cuda = kwargs.get('cuda', False)
        self.__depot = kwargs.get('depot', None)
        self.__ospackages = kwargs.get('ospackages', ['tar', 'wget'])
        self.__packages = kwargs.get('packages', [])
        self.__prefix = kwargs.get('prefix', '/usr/local/julia')
        self.__version = kwargs.get('version', '1.1.0')

        self.__commands = [] # Filled in by __setup()
        self.__environment_variables = {
            'PATH': '{}:$PATH'.format(posixpath.join(self.__prefix, 'bin'))}
        self.__wd = '/var/tmp' # working directory

        # Construct the series of steps to execute
        self.__setup()

        # Fill in container instructions
        self.__instructions()

    def __instructions(self):
        """Fill in container instructions"""

        self += comment('Julia version {}'.format(self.__version))
        self += packages(ospackages=self.__ospackages)
        self += shell(commands=self.__commands)
        if self.__environment_variables:
            self += environment(variables=self.__environment_variables)

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

        tarball = 'julia-{}-linux-x86_64.tar.gz'.format(self.__version)
        url = '{0}/{1}/{2}'.format(self.__baseurl, major_minor, tarball)

        # Download source from web
        self.__commands.append(self.download_step(url=url,
                                                  directory=self.__wd))
        self.__commands.append(self.untar_step(
            tarball=posixpath.join(self.__wd, tarball), directory=self.__wd))

        # "Install"
        self.__commands.append('cp -a {0} {1}'.format(
            posixpath.join(self.__wd, 'julia-{}'.format(self.__version)),
            self.__prefix))

        # Install packages
        if self.__cuda:
            self.__packages.extend(['CUDAnative', 'CuArrays', 'GPUArrays'])
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
            if self.__depot:
                julia = 'JULIA_DEPOT_PATH={0} '.format(self.__depot) + julia
            self.__commands.append(
                '{0} -e \'using Pkg; Pkg.add([{1}])\''.format(julia,
                                                              packages_csv))

        # Set library path
        libpath = posixpath.join(self.__prefix, 'lib')
        if self.ldconfig:
            self.__commands.append(self.ldcache_step(directory=libpath))
        else:
            self.__environment_variables['LD_LIBRARY_PATH'] = '{}:$LD_LIBRARY_PATH'.format(libpath)

        # Cleanup tarball and directory
        self.__commands.append(self.cleanup_step(
            items=[posixpath.join(self.__wd, tarball),
                   posixpath.join(self.__wd, 'julia-{}'.format(self.__version))]))

        # Setup environment
        if self.__depot:
            self.__environment_variables['JULIA_DEPOT_PATH'] = self.__depot

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
