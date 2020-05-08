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

import hpccm.templates.git

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.generic_cmake import generic_cmake
from hpccm.building_blocks.packages import packages
from hpccm.primitives.comment import comment

class sensei(bb_base, hpccm.templates.git):
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

    annotate: Boolean flag to specify whether to include annotations
    (labels).  The default is False.

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

        self.__branch = kwargs.pop('branch', 'v2.1.1')
        self.__catalyst = kwargs.pop('catalyst', '')
        self.__cmake_opts = kwargs.pop('cmake_opts', ['-DENABLE_SENSEI=ON'])
        self.__libsim = kwargs.pop('libsim', '')
        self.__miniapps = kwargs.pop('miniapps', False)
        self.__ospackages = kwargs.pop('ospackages', ['ca-certificates', 'git',
                                                      'make'])
        self.__prefix = kwargs.pop('prefix', '/usr/local/sensei')
        self.__repository = kwargs.pop('repository', 'https://gitlab.kitware.com/sensei/sensei.git')
        self.__vtk = kwargs.pop('vtk', '')

        # Set the cmake options
        self.__cmake()

        # Setup build configuration
        self.__bb = generic_cmake(
            base_annotation=self.__class__.__name__,
            branch=self.__branch,
            comment=False,
            cmake_opts=self.__cmake_opts,
            prefix=self.__prefix,
            repository=self.__repository,
            **kwargs)

        # Container instructions
        self += comment('SENSEI version {}'.format(self.__branch))
        self += packages(ospackages=self.__ospackages)
        self += self.__bb

    def __cmake(self):
        """Setup cmake options based on users parameters"""

        # Configure
        if self.__catalyst:
            self.__cmake_opts.extend(
                ['-DENABLE_CATALYST=ON',
                 '-DParaView_DIR={}'.format(self.__catalyst)])
        if self.__libsim:
            self.__cmake_opts.extend(
                ['-DENABLE_LIBSIM=ON',
                 '-DLIBSIM_DIR={}'.format(self.__libsim)])
        if not self.__miniapps:
            self.__cmake_opts.extend(
                ['-DENABLE_PARALLEL3D=OFF', '-DENABLE_OSCILLATORS=OFF'])
        else:
            self.__cmake_opts.append('-DCMAKE_C_STANDARD=99')

        if self.__vtk:
            self.__cmake_opts.append(
                '-DVTK_DIR={}'.format(self.__vtk))

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
        instructions.append(self.__bb.runtime(_from=_from))
        return '\n'.join(str(x) for x in instructions)
