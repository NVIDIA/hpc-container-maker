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

"""Catalyst building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import posixpath
import re

import hpccm.config
import hpccm.templates.CMakeBuild
import hpccm.templates.envvars
import hpccm.templates.ldconfig
import hpccm.templates.rm
import hpccm.templates.tar
import hpccm.templates.wget

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.packages import packages
from hpccm.common import linux_distro
from hpccm.primitives.comment import comment
from hpccm.primitives.copy import copy
from hpccm.primitives.environment import environment
from hpccm.primitives.shell import shell
from hpccm.toolchain import toolchain

class catalyst(bb_base, hpccm.templates.CMakeBuild, hpccm.templates.envvars,
               hpccm.templates.ldconfig, hpccm.templates.rm,
               hpccm.templates.tar, hpccm.templates.wget):
    """The `catalyst` building block configures, builds, and installs the
    [ParaView Catalyst](https://www.paraview.org/in-situ/) component.

    The [CMake](#cmake) building block should be installed prior to
    this building block.

    A MPI building block should be installed prior to this building
    block.

    If GPU rendering will be used then a
    [cudagl](https://hub.docker.com/r/nvidia/cudagl) base image is
    recommended.

    # Parameters

    cmake_opts: List of options to pass to `cmake`.  The default is an
    empty list.

    edition: The Catalyst edition to use. Valid choices are `Base`,
    `Base-Essentials`, `Base-Essentials-Extras`,
    `Base-Essentials-Extras-Rendering-Base`, `Base-Enable-Python`,
    `Base-Enable-Python-Essentials`,
    `Base-Enable-Python-Essentials-Extras`, and
    `Base-Enable-Python-Essentials-Extras-Rendering-Base`.  If a
    Python edition is selected, then the [Python](#python) building
    block should be installed with development libraries prior to this
    building block. The default value is
    `Base-Enable-Python-Essentials-Extras-Rendering-Base`.

    environment: Boolean flag to specify whether the environment
    (`LD_LIBRARY_PATH` and `PATH`) should be modified to include
    ParaView Catalyst. The default is True.

    ldconfig: Boolean flag to specify whether the Catalyst library
    directory should be added dynamic linker cache.  If False, then
    `LD_LIBRARY_PATH` is modified to include the Catalyst library
    directory. The default value is False.

    ospackages: List of OS packages to install prior to configuring
    and building.  For Ubuntu, the default values are `git`, `gzip`,
    `make`, `tar`, and `wget`.  If a rendering edition is selected
    then `libxau-dev`, `libxext-dev`, `libxt-dev`, `libice-dev`,
    `libsm-dev`, `libx11-dev`, `libgl1-mesa-dev` are also included.
    For RHEL-based Linux distributions, the default values are `git`,
    `gzip`, `make`, `tar`, `wget`, and `which`.  If a rendering
    edition is selected then `libX11-devel`, `libXau-devel`,
    `libXext-devel`, `libXt-devel`, `libICE-devel`, `libSM-devel`,
    `libglvnd-devel`, `mesa-libGL-devel` are also included.

    prefix: The top level install location.  The default value is
    `/usr/local/catalyst`.

    toolchain: The toolchain object.  This should be used if
    non-default compilers or other toolchain options are needed.  The
    default is empty.

    version: The version of Catalyst source to download.  The default
    value is `5.6.1`.

    # Examples

    ```python
    catalyst(prefix='/opt/catalyst/5.6.0', version='5.6.0')
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(catalyst, self).__init__(**kwargs)

        self.cmake_opts = kwargs.get('cmake_opts', [])
        self.__edition = kwargs.get('edition', 'Base-Enable-Python-Essentials-Extras-Rendering-Base')
        self.__ospackages = kwargs.get('ospackages', [])
        self.prefix = kwargs.get('prefix', '/usr/local/catalyst')
        self.__runtime_ospackages = [] # Filled in by __distro()
        # Input toolchain, i.e., what to use when building
        self.__toolchain = kwargs.get('toolchain', toolchain())
        self.__version = kwargs.get('version', '5.6.1')
        self.__url = r'https://www.paraview.org/paraview-downloads/download.php?submit=Download\&version={0}\&type=catalyst\&os=Sources\&downloadFile={1}'

        self.__commands = [] # Filled in by __setup()
        self.__wd = '/var/tmp' # working directory

        # Validate edition choice
        if self.__edition not in [
                'Base', 'Base-Essentials', 'Base-Essentials-Extras',
                'Base-Essentials-Extras-Rendering-Base',
                'Base-Enable-Python', 'Base-Enable-Python-Essentials',
                'Base-Enable-Python-Essentials-Extras',
                'Base-Enable-Python-Essentials-Extras-Rendering-Base']:
            logging.warning('Invalid Catalyst edition "{0}", defaulting to '
                            'Base-Essentials'.format(self.__edition))
            self.__edition = 'Base-Essentials'

        self.__basename = 'Catalyst-v{0}-{1}'.format(self.__version,
                                                     self.__edition)

        # Set the Linux distribution specific parameters
        self.__distro()

        # Construct the series of steps to execute
        self.__setup()

        # Fill in container instructions
        self.__instructions()

    def __instructions(self):
        """Fill in container instructions"""

        self += comment('ParaView Catalyst version {}'.format(self.__version))
        self += packages(ospackages=self.__ospackages)
        self += shell(commands=self.__commands)
        self += environment(variables=self.environment_step())

    def __distro(self):
        """Based on the Linux distribution, set values accordingly.  A user
        specified value overrides any defaults."""

        if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
            if not self.__ospackages:
                self.__ospackages = ['git', 'gzip', 'make', 'tar', 'wget']
                if 'Rendering' in self.__edition:
                    self.__ospackages.extend([
                        'libxau-dev', 'libxext-dev', 'libxt-dev',
                        'libice-dev', 'libsm-dev', 'libx11-dev',
                        'libgl1-mesa-dev'])
            if 'Rendering' in self.__edition:
                self.__runtime_ospackages.extend([
                    'libxau6', 'libxext6', 'libxt6', 'libice6', 'libsm6',
                    'libx11-6', 'libgl1-mesa-glx'])
        elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
            if not self.__ospackages:
                self.__ospackages = ['git', 'gzip', 'make', 'tar', 'wget',
                                     'which']
                if 'Rendering' in self.__edition:
                    self.__ospackages.extend([
                        'libX11-devel', 'libXau-devel', 'libXext-devel',
                        'libXt-devel', 'libICE-devel', 'libSM-devel',
                        'libglvnd-devel', 'mesa-libGL-devel'])
            if 'Rendering' in self.__edition:
                self.__runtime_ospackages.extend([
                    'libX11', 'libXau', 'libXext', 'libXt', 'libICE', 'libSM',
                    'libglvnd', 'libglvnd-opengl', 'mesa-libGL'])
        else: # pragma: no cover
            raise RuntimeError('Unknown Linux distribution')

    def __setup(self):
        """Construct the series of shell commands, i.e., fill in
           self.__commands"""

        # The download URL has the format contains vMAJOR.MINOR in the
        # path and the tarball contains MAJOR.MINOR.REVISION, so pull
        # apart the full version to get the MAJOR and MINOR components.
        match = re.match(r'(?P<major>\d+)\.(?P<minor>\d+)', self.__version)
        major_minor = 'v{0}.{1}'.format(match.groupdict()['major'],
                                        match.groupdict()['minor'])

        tarball = self.__basename + '.tar.gz'
        url = self.__url.format(major_minor, tarball)

        # Download source from web
        self.__commands.append(self.download_step(
            url=url,
            directory=self.__wd,
            outfile=posixpath.join(self.__wd, tarball)))
        self.__commands.append(self.untar_step(
            tarball=posixpath.join(self.__wd, tarball), directory=self.__wd))

        # Configure
        # Catalyst has a cmake.sh shell script that sets configuration
        # options.  Use that in place of cmake.
        configure = self.configure_step(
            directory=posixpath.join(self.__wd, self.__basename),
            opts=self.cmake_opts, toolchain=self.__toolchain)
        configure = configure.replace('cmake', '{}/cmake.sh'.format(posixpath.join(self.__wd, self.__basename)))
        self.__commands.append(configure)

        # Build
        self.__commands.append(self.build_step())

        # Install
        self.__commands.append(self.build_step(target='install'))

        # Set library path
        libpath = posixpath.join(self.prefix, 'lib')
        if self.ldconfig:
            self.__commands.append(self.ldcache_step(directory=libpath))
        else:
            self.environment_variables['LD_LIBRARY_PATH'] = '{}:$LD_LIBRARY_PATH'.format(libpath)

        # Cleanup
        self.__commands.append(self.cleanup_step(
            items=[posixpath.join(self.__wd, tarball),
                   posixpath.join(self.__wd, self.__basename)]))

        # Set the environment
        self.environment_variables['PATH'] = '{}:$PATH'.format(
            posixpath.join(self.prefix, 'bin'))

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples
        ```python
        c = catalyst(...)
        Stage0 += c
        Stage1 += c.runtime()
        ```
        """
        instructions = []
        instructions.append(comment('ParaView Catalyst'))
        if self.__runtime_ospackages:
            instructions.append(packages(ospackages=self.__runtime_ospackages))
        instructions.append(copy(_from=_from, src=self.prefix,
                                 dest=self.prefix))
        if self.ldconfig:
            instructions.append(shell(
                commands=[self.ldcache_step(
                    directory=posixpath.join(self.prefix, 'lib'))]))
        instructions.append(environment(variables=self.environment_step()))
        return '\n'.join(str(x) for x in instructions)
