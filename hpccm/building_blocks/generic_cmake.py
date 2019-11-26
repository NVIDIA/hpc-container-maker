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

"""Generic cmake building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import posixpath
import re

import hpccm.templates.CMakeBuild
import hpccm.templates.git
import hpccm.templates.rm
import hpccm.templates.tar
import hpccm.templates.wget

from hpccm.building_blocks.base import bb_base
from hpccm.primitives.comment import comment
from hpccm.primitives.copy import copy
from hpccm.primitives.shell import shell
from hpccm.toolchain import toolchain

class generic_cmake(bb_base, hpccm.templates.CMakeBuild, hpccm.templates.git,
                    hpccm.templates.rm, hpccm.templates.tar,
                    hpccm.templates.wget):
    """The `generic_cmake` building block downloads, configures,
    builds, and installs a specified CMake enabled package.

    # Parameters

    branch: The git branch to clone.  Only recognized if the
    `repository` parameter is specified.  The default is empty, i.e.,
    use the default branch for the repository.

    build_directory: The location to build the package.  The default
    value is a `build` subdirectory in the source code location.

    check: Boolean flag to specify whether the `make check` step
    should be performed.  The default is False.

    cmake_opts: List of options to pass to `cmake`.  The default value
    is an empty list.

    directory: The source code location.  The default value is the
    basename of the downloaded package.  If the value is not an
    absolute path, then the temporary working directory is prepended.

    install: Boolean flag to specify whether the `make install` step
    should be performed.  The default is True.

    make: Boolean flag to specify whether the `make` step should be
    performed.  The default is True.

    postinstall: List of shell commands to run after running 'make
    install'.  The working directory is the install prefix.  The
    default is an empty list.

    preconfigure: List of shell commands to run prior to running
    `cmake`.  The working directory is the source code location.  The
    default is an empty list.

    prefix: The top level install location.  The default value is
    `/usr/local`. It is highly recommended not to use this default and
    instead set the prefix to a package specific directory.

    repository: The git repository of the package to build.  One of
    this paramter or the `url` parameter must be specified.

    toolchain: The toolchain object.  This should be used if
    non-default compilers or other toolchain options are needed.  The
    default is empty.

    url: The URL of the tarball package to build.  One of this
    parameter or the `repository` parameter must be specified.

    # Examples

    ```python
    generic_cmake(cmake_opts=['-D CMAKE_BUILD_TYPE=Release',
                              '-D CUDA_TOOLKIT_ROOT_DIR=/usr/local/cuda',
                              '-D GMX_BUILD_OWN_FFTW=ON',
                              '-D GMX_GPU=ON',
                              '-D GMX_MPI=OFF',
                              '-D GMX_OPENMP=ON',
                              '-D GMX_PREFER_STATIC_LIBS=ON',
                              '-D MPIEXEC_PREFLAGS=--allow-run-as-root'],
                  directory='gromacs-2018.2',
                  prefix='/usr/local/gromacs',
                  url='https://github.com/gromacs/gromacs/archive/v2018.2.tar.gz')
    ```

    ```python
    generic_cmake(branch='v0.8.0',
                  cmake_opts=['-D CMAKE_BUILD_TYPE=RELEASE',
                              '-D QUDA_DIRAC_CLOVER=ON',
                              '-D QUDA_DIRAC_DOMAIN_WALL=ON',
                              '-D QUDA_DIRAC_STAGGERED=ON',
                              '-D QUDA_DIRAC_TWISTED_CLOVER=ON',
                              '-D QUDA_DIRAC_TWISTED_MASS=ON',
                              '-D QUDA_DIRAC_WILSON=ON',
                              '-D QUDA_FORCE_GAUGE=ON',
                              '-D QUDA_FORCE_HISQ=ON',
                              '-D QUDA_GPU_ARCH=sm_70',
                              '-D QUDA_INTERFACE_MILC=ON',
                              '-D QUDA_INTERFACE_QDP=ON',
                              '-D QUDA_LINK_HISQ=ON',
                              '-D QUDA_MPI=ON'],
                  prefix='/usr/local/quda',
                  repository='https://github.com/lattice/quda.git')
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(generic_cmake, self).__init__(**kwargs)

        self.__branch = kwargs.get('branch', None)
        self.__build_directory = kwargs.get('build_directory', 'build')
        self.__check = kwargs.get('check', False)
        self.cmake_opts = kwargs.get('cmake_opts', [])
        self.__directory = kwargs.get('directory', None)
        self.__environment = kwargs.get('environment', {})
        self.__install = kwargs.get('install', True)
        self.__make = kwargs.get('make', True)
        self.__postinstall = kwargs.get('postinstall', [])
        self.__preconfigure = kwargs.get('preconfigure', [])
        self.__repository = kwargs.get('repository', None)
        self.__toolchain = kwargs.get('toolchain', toolchain())
        self.__url = kwargs.get('url', None)

        self.__commands = [] # Filled in by __setup()
        self.__wd = '/var/tmp' # working directory

        if not self.__repository and not self.__url:
            raise RuntimeError('must specify a repository or a URL')

        if self.__repository and self.__url:
            raise RuntimeError('cannot specify both a repository and a URL')

        # Construct the series of steps to execute
        self.__setup()

        # Fill in container instructions
        self.__instructions()

    def __instructions(self):
        """Fill in container instructions"""

        if self.__url:
            self += comment(self.__url, reformat=False)
        elif self.__repository:
            self += comment(self.__repository, reformat=False)
        self += shell(commands=self.__commands)

    def __setup(self):
        """Construct the series of shell commands, i.e., fill in
           self.__commands"""

        if self.__url:
            # Set the name of the tarball, untarred package directory, and
            # source directory inside the extracted directory
            tarball = posixpath.basename(self.__url)
            match = re.search(r'(.*)(?:(?:\.tar)|(?:\.tar\.gz)|(?:\.tgz)|(?:\.tar\.bz2)|(?:\.tar\.xz))$',
                              tarball)
            if match:
                pkgdir = match.group(1)
            else:
                raise RuntimeError('unrecognized package format')

            # directory containing the unarchived package
            if self.__directory:
                if posixpath.isabs(self.__directory):
                    directory = self.__directory
                else:
                    directory = posixpath.join(self.__wd, self.__directory)
            else:
                directory = posixpath.join(self.__wd, pkgdir)

            # Download source from web
            self.__commands.append(self.download_step(url=self.__url,
                                                      directory=self.__wd))

            # Untar source package
            self.__commands.append(self.untar_step(
                tarball=posixpath.join(self.__wd, tarball),
                directory=self.__wd))

        if self.__repository:
            # Clone git repository
            self.__commands.append(self.clone_step(
                branch=self.__branch, path=self.__wd,
                repository=self.__repository))

            directory = posixpath.join(self.__wd, posixpath.splitext(
                posixpath.basename(self.__repository))[0])

        # Preconfigure setup
        if self.__preconfigure:
            # Assume the preconfigure commands should be run from the
            # source directory
            self.__commands.append('cd {}'.format(directory))
            self.__commands.extend(self.__preconfigure)

        # Configure
        environment = []
        if self.__environment:
            for key, val in sorted(self.__environment.items()):
                environment.append('{0}={1}'.format(key, val))
        self.__commands.append(self.configure_step(
            build_directory=self.__build_directory,
            directory=directory, environment=environment,
            toolchain=self.__toolchain))

        # Build
        if self.__make:
            self.__commands.append(self.build_step())

        # Check the build
        if self.__check:
            self.__commands.append(self.build_step(target='check'))

        # Install
        if self.__install:
            self.__commands.append(self.build_step(target='install'))

        if self.__postinstall:
            # Assume the postinstall commands should be run from the
            # install directory
            self.__commands.append('cd {}'.format(self.prefix))
            self.__commands.extend(self.__postinstall)

        # Cleanup
        remove = [directory]
        if self.__url:
            remove.append(posixpath.join(self.__wd, tarball))
        if self.__build_directory:
            if posixpath.isabs(self.__build_directory):
                remove.append(self.__build_directory)
        self.__commands.append(self.cleanup_step(items=remove))


    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples

        ```python
        g = generic_cmake(...)
        Stage0 += g
        Stage1 += g.runtime()
        ```
        """
        if self.prefix:
            instructions = []
            if self.__url:
                instructions.append(comment(self.__url, reformat=False))
            elif self.__repository:
                instructions.append(comment(self.__repository, reformat=False))
            instructions.append(copy(_from=_from, src=self.prefix,
                                     dest=self.prefix))
            return '\n'.join(str(x) for x in instructions)
