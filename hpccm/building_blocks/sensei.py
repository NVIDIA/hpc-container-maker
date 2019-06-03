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

"""SENSEI building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import posixpath
import re

import hpccm.templates.CMakeBuild
import hpccm.templates.git
import hpccm.templates.rm

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.packages import packages
from hpccm.primitives.comment import comment
from hpccm.primitives.copy import copy
from hpccm.primitives.shell import shell
from hpccm.toolchain import toolchain

class sensei(bb_base, hpccm.templates.CMakeBuild, hpccm.templates.git,
             hpccm.templates.rm):
    """The `sensei` building block configures, builds, and installs the
    [SENSEI](https://sensei-insitu.org) component.

    The [CMake](#cmake) building block should be installed prior to
    this building block.

    In most cases, one or both of the [Catalyst](#catalyst) or
    [Libsim](#libsim) building blocks should be installed.

    If GPU rendering will be used then a
    [cudagl](https://hub.docker.com/r/nvidia/cudagl) base image is
    recommended.

    # Parameters

    branch: The branch of SENSEI to use.  The default value is
    `v2.1.1`.

    catalyst: Flag to specify the location of the ParaView/Catalyst
    installation, e.g., `/usr/local/catalyst`.  If set, then the
    [Catalyst](#catalyst) building block should be installed prior to
    this building block.  The default value is empty.

    cmake_opts: List of options to pass to `cmake`.  The default value
    is `-DENABLE_SENSEI=ON`.

    libsim: Flag to specify the location of the VisIt/Libsim
    installation, e.g., `/usr/local/visit`.  If set, then the
    [Libsim](#libsim) building block should be installed prior to this
    building block.  The `vtk` option should also be set.  The default
    value is empty.

    miniapps: Boolean flag to specify whether the SENSEI mini-apps
    should be built and installed.  The default is False.

    ospackages: List of OS packages to install prior to configuring
    and building.  The default values are `ca-certificates`, `git`,
    and `make`.

    prefix: The top level install location.  The default value is
    `/usr/local/sensei`.

    toolchain: The toolchain object.  This should be used if
    non-default compilers or other toolchain options are needed.  The
    default is empty.

    vtk: Flag to specify the location of the VTK installation.  If
    `libsim` is defined, this option must be set to the Libsim VTK
    location, e.g.,
    `/usr/local/visit/third-party/vtk/6.1.0/linux-x86_64_gcc-5.4/lib/cmake/vtk-6.1`. Note
    that the compiler version is embedded in the Libsim VTK path.  The
    compiler version may differ depending on which base image is used;
    version 5.4 corresponds to Ubuntu 16.04. The default value is
    empty.

    # Examples

    ```python
    sensei(branch='v2.1.1', catalyst='/usr/local/catalyst',
           prefix='/opt/sensei')
    ```

    ```python
    sensei(libsim='/usr/local/visit',
           vtk='/usr/local/visit/third-party/vtk/6.1.0/linux-x86_64_gcc-5.4/lib/cmake/vtk-6.1')
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(sensei, self).__init__(**kwargs)

        self.__branch = kwargs.get('branch', 'v2.1.1')
        self.__catalyst = kwargs.get('catalyst', '')
        self.cmake_opts = kwargs.get('cmake_opts', ['-DENABLE_SENSEI=ON'])
        self.__libsim = kwargs.get('libsim', '')
        self.__miniapps = kwargs.get('miniapps', False)
        self.__ospackages = kwargs.get('ospackages', ['ca-certificates', 'git',
                                                      'make'])
        self.prefix = kwargs.get('prefix', '/usr/local/sensei')
        self.__repository = kwargs.get('repository', 'https://gitlab.kitware.com/sensei/sensei.git')
        # Input toolchain, i.e., what to use when building
        self.__toolchain = kwargs.get('toolchain', toolchain())
        self.__vtk = kwargs.get('vtk', '')

        self.__commands = [] # Filled in by __setup()
        self.__wd = '/var/tmp' # working directory

        # Construct the series of steps to execute
        self.__setup()

        # Fill in container instructions
        self.__instructions()

    def __instructions(self):
        """Fill in container instructions"""

        self += comment('SENSEI version {}'.format(self.__branch))
        self += packages(ospackages=self.__ospackages)
        self += shell(commands=self.__commands)

    def __setup(self):
        """Construct the series of shell commands, i.e., fill in
           self.__commands"""

        # Download source
        self.__commands.append(self.clone_step(repository=self.__repository,
                                               branch=self.__branch,
                                               path=self.__wd))

        # Configure
        if self.__catalyst:
            self.cmake_opts.extend(
                ['-DENABLE_CATALYST=ON',
                 '-DParaView_DIR={}'.format(self.__catalyst)])
        if self.__libsim:
            self.cmake_opts.extend(
                ['-DENABLE_LIBSIM=ON',
                 '-DLIBSIM_DIR={}'.format(self.__libsim)])
        if not self.__miniapps:
            self.cmake_opts.extend(
                ['-DENABLE_PARALLEL3D=OFF', '-DENABLE_OSCILLATORS=OFF'])
        else:
            self.cmake_opts.append('-DCMAKE_C_STANDARD=99')
        if self.__vtk:
            self.cmake_opts.append(
                '-DVTK_DIR={}'.format(self.__vtk))
        self.__commands.append(self.configure_step(
            directory=posixpath.join(self.__wd, 'sensei'),
            opts=self.cmake_opts, toolchain=self.__toolchain))

        # Build
        self.__commands.append(self.build_step())

        # Install
        self.__commands.append(self.build_step(target='install'))

        # Cleanup
        self.__commands.append(self.cleanup_step(
            items=[posixpath.join(self.__wd, 'sensei')]))

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples
        ```python
        s = sensei(...)
        Stage0 += s
        Stage1 += s.runtime()
        ```
        """
        instructions = []
        instructions.append(comment('SENSEI'))
        instructions.append(copy(_from=_from, src=self.prefix,
                                 dest=self.prefix))
        return '\n'.join(str(x) for x in instructions)
