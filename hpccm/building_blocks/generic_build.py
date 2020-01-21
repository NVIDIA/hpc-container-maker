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

"""Generic build building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import posixpath
import re

import hpccm.templates.git
import hpccm.templates.rm
import hpccm.templates.tar
import hpccm.templates.wget

from hpccm.building_blocks.base import bb_base
from hpccm.primitives.comment import comment
from hpccm.primitives.copy import copy
from hpccm.primitives.shell import shell

class generic_build(bb_base, hpccm.templates.git, hpccm.templates.rm,
                    hpccm.templates.tar, hpccm.templates.wget):
    """The `generic_build` building block downloads and builds
    a specified package.

    # Parameters

    build: List of shell commands to run in order to build the
    package.  The working directory is the source directory.  The
    default is an empty list.

    branch: The git branch to clone.  Only recognized if the
    `repository` parameter is specified.  The default is empty, i.e.,
    use the default branch for the repository.

    commit: The git commit to clone.  Only recognized if the
    `repository` parameter is specified.  The default is empty, i.e.,
    use the latest commit on the default branch for the repository.

    directory: The source code location.  The default value is the
    basename of the downloaded package.  If the value is not an
    absolute path, then the temporary working directory is prepended.

    install: List of shell commands to run in order to install the
    package.  The working directory is the source directory.  If
    `prefix` is defined, it will be automatically created if the list
    is non-empty.  The default is an empty list.

    prefix: The top level install location.  The default value is
    empty. If defined then the location is copied as part of the
    runtime method.

    recursive: Initialize and checkout git submodules. `repository` parameter
    must be specified. The default is False.

    repository: The git repository of the package to build.  One of
    this paramter or the `url` parameter must be specified.

    url: The URL of the tarball package to build.  One of this
    parameter or the `repository` parameter must be specified.

    # Examples

    ```python
    generic_build(build=['make ARCH=sm_70'],
                  install=['cp stream /usr/local/bin/cuda-stream'],
                  repository='https://github.com/bcumming/cuda-stream')
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(generic_build, self).__init__(**kwargs)

        self.__build = kwargs.get('build', [])
        self.__branch = kwargs.get('branch', None)
        self.__commit = kwargs.get('commit', None)
        self.__directory = kwargs.get('directory', None)
        self.__install = kwargs.get('install', [])
        self.__prefix = kwargs.get('prefix', None)
        self.__recursive = kwargs.get('recursive', False)
        self.__repository = kwargs.get('repository', None)
        self.__url = kwargs.get('url', None)

        self.__commands = [] # Filled in by __setup()
        self.__wd = '/var/tmp' # working directory

        if not self.__repository and not self.__url:
            raise RuntimeError('must specify a repository or a URL')

        if self.__repository and self.__url:
            raise RuntimeError('cannot specify both a repository and a URL')

        if self.__branch and self.__commit:
            raise RuntimeError('cannot specify both a branch and a commit')

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
                branch=self.__branch, commit=self.__commit, path=self.__wd,
                recursive=self.__recursive, repository=self.__repository))

            directory = posixpath.join(self.__wd, posixpath.splitext(
                posixpath.basename(self.__repository))[0])

        # Build
        if self.__build:
            self.__commands.append('cd {}'.format(directory))
            self.__commands.extend(self.__build)

        # Install
        if self.__install:
            if self.__prefix:
                self.__commands.append('mkdir -p {}'.format(self.__prefix))
            self.__commands.append('cd {}'.format(directory))
            self.__commands.extend(self.__install)

        # Cleanup
        remove = [directory]
        if self.__url:
            remove.append(posixpath.join(self.__wd, tarball))
        self.__commands.append(self.cleanup_step(items=remove))

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples

        ```python
        g = generic_build(...)
        Stage0 += g
        Stage1 += g.runtime()
        ```
        """
        if self.__prefix:
            instructions = []
            if self.__url:
                instructions.append(comment(self.__url, reformat=False))
            elif self.__repository:
                instructions.append(comment(self.__repository, reformat=False))
            instructions.append(copy(_from=_from, src=self.__prefix,
                                     dest=self.__prefix))
            return '\n'.join(str(x) for x in instructions)
        else:
            return
