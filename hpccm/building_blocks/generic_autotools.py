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

"""Generic autotools building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import posixpath
import re

import hpccm.templates.ConfigureMake
import hpccm.templates.downloader
import hpccm.templates.rm

from hpccm.building_blocks.base import bb_base
from hpccm.primitives.comment import comment
from hpccm.primitives.copy import copy
from hpccm.primitives.shell import shell
from hpccm.toolchain import toolchain

class generic_autotools(bb_base, hpccm.templates.ConfigureMake,
                        hpccm.templates.downloader, hpccm.templates.rm):
    """The `generic_autotools` building block downloads, configures,
    builds, and installs a specified GNU Autotools enabled package.

    # Parameters

    branch: The git branch to clone.  Only recognized if the
    `repository` parameter is specified.  The default is empty, i.e.,
    use the default branch for the repository.

    build_directory: The location to build the package.  The default
    value is the source code location.

    check: Boolean flag to specify whether the `make check` step
    should be performed.  The default is False.

    commit: The git commit to clone.  Only recognized if the
    `repository` parameter is specified.  The default is empty, i.e.,
    use the latest commit on the default branch for the repository.

    configure_opts: List of options to pass to `configure`.  The
    default value is an empty list.

    directory: The source code location.  The default value is the
    basename of the downloaded package.  If the value is not an
    absolute path, then the temporary working directory is prepended.

    disable_FEATURE: Flags to control disabling features when
    configuring.  For instance, `disable_foo=True` maps to
    `--disable-foo`.  Underscores in the parameter name are converted
    to dashes.

    enable_FEATURE[=ARG]: Flags to control enabling features when
    configuring.  For instance, `enable_foo=True` maps to
    `--enable-foo` and `enable_foo='yes'` maps to `--enable-foo=yes`.
    Underscores in the parameter name are converted to dashes.

    install: Boolean flag to specify whether the `make install` step
    should be performed.  The default is True.

    make: Boolean flag to specify whether the `make` step should be
    performed.  The default is True.

    postinstall: List of shell commands to run after running 'make
    install'.  The working directory is the install prefix.  The
    default is an empty list.

    preconfigure: List of shell commands to run prior to running
    `configure`.  The working directory is the source code location.
    The default is an empty list.

    prefix: The top level install location.  The default value is
    `/usr/local`. It is highly recommended not use use this default
    and instead set the prefix to a package specific directory.

    recursive: Initialize and checkout git submodules. `repository` parameter
    must be specified. The default is False.

    repository: The git repository of the package to build.  One of
    this paramter or the `url` parameter must be specified.

    toolchain: The toolchain object.  This should be used if
    non-default compilers or other toolchain options are needed.  The
    default is empty.

    url: The URL of the tarball package to build.  One of this
    parameter or the `repository` parameter must be specified.

    with_PACKAGE[=ARG]: Flags to control optional packages when
    configuring.  For instance, `with_foo=True` maps to `--with-foo`
    and `with_foo='/usr/local/foo'` maps to
    `--with-foo=/usr/local/foo`.  Underscores in the parameter name
    are converted to dashes.

    without_PACKAGE: Flags to control optional packages when
    configuring.  For instance `without_foo=True` maps to
    `--without-foo`.  Underscores in the parameter name are converted
    to dashes.

    # Examples

    ```python
    generic_autotools(directory='tcl8.6.9/unix',
                      prefix='/usr/local/tcl',
                      url='https://prdownloads.sourceforge.net/tcl/tcl8.6.9-src.tar.gz')
    ```

    ```python
    generic_autotools(preconfigure=['./autogen.sh'],
                      prefix='/usr/local/zeromq',
                      repository='https://github.com/zeromq/libzmq.git')
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(generic_autotools, self).__init__(**kwargs)

        self.__build_directory = kwargs.get('build_directory', None)
        self.__check = kwargs.get('check', False)
        self.configure_opts = kwargs.get('configure_opts', [])
        self.__directory = kwargs.get('directory', None)
        self.__environment = kwargs.get('environment', {})
        self.__install = kwargs.get('install', True)
        self.__make = kwargs.get('make', True)
        self.__postinstall = kwargs.get('postinstall', [])
        self.__preconfigure = kwargs.get('preconfigure', [])
        self.__recursive = kwargs.get('recursive', False)
        self.__toolchain = kwargs.get('toolchain', toolchain())

        self.__commands = [] # Filled in by __setup()
        self.__wd = '/var/tmp' # working directory

        # Construct the series of steps to execute
        self.__setup()

        # Fill in container instructions
        self.__instructions()

    def __instructions(self):
        """Fill in container instructions"""

        if self.url:
            self += comment(self.url, reformat=False)
        elif self.repository:
            self += comment(self.repository, reformat=False)
        self += shell(commands=self.__commands)

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
        environment = []
        if self.__environment:
            for key, val in sorted(self.__environment.items()):
                environment.append('{0}={1}'.format(key, val))
        self.__commands.append(self.configure_step(
            build_directory=self.__build_directory,
            directory=self.src_directory, environment=environment,
            toolchain=self.__toolchain))

        # Build
        if self.__make:
            self.__commands.append(self.build_step())

        # Check the build
        if self.__check:
            self.__commands.append(self.check_step())

        # Install
        if self.__install:
            self.__commands.append(self.install_step())

        if self.__postinstall:
            # Assume the postinstall commands should be run from the
            # install directory
            self.__commands.append('cd {}'.format(self.prefix))
            self.__commands.extend(self.__postinstall)

        # Cleanup
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
        g = generic_autotools(...)
        Stage0 += g
        Stage1 += g.runtime()
        ```
        """
        if self.prefix:
            instructions = []
            if self.url:
                instructions.append(comment(self.url, reformat=False))
            elif self.repository:
                instructions.append(comment(self.repository, reformat=False))
            instructions.append(copy(_from=_from, src=self.prefix,
                                     dest=self.prefix))
            return '\n'.join(str(x) for x in instructions)
        else:
            return
