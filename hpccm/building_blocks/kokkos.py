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

"""Kokkos building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import posixpath

import hpccm.templates.CMakeBuild
import hpccm.templates.annotate
import hpccm.templates.downloader
import hpccm.templates.envvars
import hpccm.templates.ldconfig
import hpccm.templates.rm

from hpccm.building_blocks.base import bb_base
from hpccm.primitives.comment import comment
from hpccm.primitives.copy import copy
from hpccm.primitives.environment import environment
from hpccm.primitives.label import label
from hpccm.primitives.shell import shell
from hpccm.toolchain import toolchain

class kokkos(bb_base, hpccm.templates.CMakeBuild,
                    hpccm.templates.annotate, hpccm.templates.downloader,
                    hpccm.templates.envvars, hpccm.templates.ldconfig,
                    hpccm.templates.rm):
    
    """Kokkos building block"""

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(kokkos, self).__init__(**kwargs)

        self.__annotations = kwargs.get('annotations', {})
        self.__build_directory = kwargs.get('build_directory', 'build')
        self.__build_environment = kwargs.get('build_environment', {})
        self.__check = kwargs.get('check', False)
        self.cmake_opts = kwargs.get('cmake_opts', [])
        self.__comment = kwargs.get('comment', True)
        self.__directory = kwargs.get('directory', None)
        self.environment_variables = kwargs.get('devel_environment', {})
        self.__install = kwargs.get('install', True)
        self.__libdir = kwargs.get('libdir', 'lib')
        self.__make = kwargs.get('make', True)
        self.__postinstall = kwargs.get('postinstall', [])
        self.__preconfigure = kwargs.get('preconfigure', [])
        self.__recursive = kwargs.get('recursive', False)
        self.__run_arguments = kwargs.get('_run_arguments', None)
        self.runtime_environment_variables = kwargs.get('runtime_environment', {})
        self.__toolchain = kwargs.get('toolchain', toolchain())

        self.__commands = [] # Filled in by __setup()
        self.__wd = '/var/tmp' # working directory

        # Construct the series of steps to execute
        self.__setup()

         # Setup the environment variables
        self.runtime_environment_variables['PATH'] = '{}/bin:$PATH'.format(
            self.prefix)

        # Fill in container instructions
        self.__instructions()

    def __instructions(self):
        """Fill in container instructions"""

        if self.__comment:
            if self.url:
                self += comment(self.url, reformat=False)
            elif self.repository:
                self += comment(self.repository, reformat=False)

        self += shell(_arguments=self.__run_arguments,
                      commands=self.__commands)
        self += environment(variables=self.environment_step())
        self += label(metadata=self.annotate_step())

    def __setup(self):
        """Construct the series of shell commands, i.e., fill in
           self.__commands"""

        # Get source
        self.__commands.append(self.download_step(recursive=self.__recursive,
                                                  wd=self.__wd))

        # directory containing the unarchived package
        if self.__directory:
            if posixpath.isabs(self.__directory):
                self.src_directory = self.__directory
            else:
                self.src_directory = posixpath.join(self.__wd,
                                                    self.__directory)

        # Preconfigure setup
        if self.__preconfigure:
            # Assume the preconfigure commands should be run from the
            # source directory
            self.__commands.append('cd {}'.format(self.src_directory))
            self.__commands.extend(self.__preconfigure)

        # Configure
        build_environment = []
        if self.__build_environment:
            for key, val in sorted(self.__build_environment.items()):
                build_environment.append('{0}={1}'.format(key, val))
        self.__commands.append(self.configure_step(
            build_directory=self.__build_directory,
            directory=self.src_directory, environment=build_environment,
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

        # Set library path
        if self.ldconfig:
            self.__commands.append(self.ldcache_step(
                directory=posixpath.join(self.prefix, self.__libdir)))

        for key,value in self.__annotations.items():
            self.add_annotation(key, value)

        # Cleanup
        remove = [self.src_directory]
        if self.url:
            remove.append(posixpath.join(self.__wd,
                                         posixpath.basename(self.url)))
        if self.__build_directory:
            if posixpath.isabs(self.__build_directory):
                remove.append(self.__build_directory)
        self.__commands.append(self.cleanup_step(items=remove))

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples

        ```python
        g = kokkos(...)
        Stage0 += g
        Stage1 += g.runtime()
        ```
        """

        if self.prefix:
            instructions = []
            if self.__comment:
                if self.url:
                    instructions.append(comment(self.url, reformat=False))
                elif self.repository:
                    instructions.append(comment(self.repository,
                                                reformat=False))
            instructions.append(copy(_from=_from, src=self.prefix,
                                     dest=self.prefix))
            if self.ldconfig:
                instructions.append(shell(commands=[self.ldcache_step(
                    directory=posixpath.join(self.prefix, self.__libdir))]))
            if self.runtime_environment_variables:
                instructions.append(environment(
                    variables=self.environment_step(runtime=True)))
            if self.annotate:
                instructions.append(label(metadata=self.annotate_step()))
            return '\n'.join(str(x) for x in instructions)
        else: # pragma: no cover
            return
