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

import os
import posixpath

import hpccm.templates.ConfigureMake
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

class generic_autotools(bb_base, hpccm.templates.ConfigureMake,
                        hpccm.templates.annotate, hpccm.templates.downloader,
                        hpccm.templates.envvars, hpccm.templates.ldconfig,
                        hpccm.templates.rm):
    """The `generic_autotools` building block downloads, configures,
    builds, and installs a specified GNU Autotools enabled package.

    # Parameters

    annotate: Boolean flag to specify whether to include annotations
    (labels).  The default is False.

    annotations: Dictionary of additional annotations to include.  The
    default is an empty dictionary.

    branch: The git branch to clone.  Only recognized if the
    `repository` parameter is specified.  The default is empty, i.e.,
    use the default branch for the repository.

    build_directory: The location to build the package.  The default
    value is the source code location.

    build_environment: Dictionary of environment variables and values
    to set when building the package.  The default is an empty
    dictionary.

    check: Boolean flag to specify whether the `make check` step
    should be performed.  The default is False.

    commit: The git commit to clone.  Only recognized if the
    `repository` parameter is specified.  The default is empty, i.e.,
    use the latest commit on the default branch for the repository.

    configure_opts: List of options to pass to `configure`.  The
    default value is an empty list.

    devel_environment: Dictionary of environment variables and values,
    e.g., `LD_LIBRARY_PATH` and `PATH`, to set in the development
    stage after the package is built and installed.  The default is an
    empty dictionary.

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

    environment: Boolean flag to specify whether the environment
    should be modified (see `devel_environment` and
    `runtime_environment`).  The default is True.

    install: Boolean flag to specify whether the `make install` step
    should be performed.  The default is True.

    ldconfig: Boolean flag to specify whether the library directory
    should be added dynamic linker cache.  The default value is False.

    libdir: The path relative to the install prefix to use when
    configuring the dynamic linker cache.  The default value is `lib`.

    make: Boolean flag to specify whether the `make` step should be
    performed.  The default is True.

    package: Path to the local source package relative to the local
    build context.  One of this parameter or the `repository` or `url`
    parameters must be specified.

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
    this parameter or the `package` or `url` parameters must be
    specified.

    _run_arguments: Specify additional [Dockerfile RUN arguments](https://github.com/moby/buildkit/blob/master/frontend/dockerfile/docs/experimental.md) (Docker specific).

    runtime_environment: Dictionary of environment variables and
    values, e.g., `LD_LIBRARY_PATH` and `PATH`, to set in the runtime
    stage.  The default is an empty dictionary.

    toolchain: The toolchain object.  This should be used if
    non-default compilers or other toolchain options are needed.  The
    default is empty.

    url: The URL of the package to build.  One of this
    parameter or the `package` or `repository` parameters must be
    specified.

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

        self.__annotations = kwargs.get('annotations', {})
        self.__build_directory = kwargs.get('build_directory', None)
        self.__build_environment = kwargs.get('build_environment', {})
        self.__check = kwargs.get('check', False)
        self.__comment = kwargs.get('comment', True)
        self.configure_opts = kwargs.get('configure_opts', [])
        self.__directory = kwargs.get('directory', None)
        self.environment_variables = kwargs.get('devel_environment', {})
        self.__install = kwargs.get('install', True)
        self.__libdir = kwargs.get('libdir', 'lib')
        self.__make = kwargs.get('make', True)
        self.__postconfigure = kwargs.get('postconfigure', [])
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

        # Fill in container instructions
        self.__instructions()

    def __instructions(self):
        """Fill in container instructions"""

        if self.__comment:
            if self.url:
                self += comment(self.url, reformat=False)
            elif self.repository:
                self += comment(self.repository, reformat=False)
            elif self.package:
                self += comment(self.package, reformat=False)
        if self.package:
            self += copy(src=self.package,
                         dest=posixpath.join(self.__wd,
                                             os.path.basename(self.package)))
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

        # Post configure setup
        if self.__postconfigure:
            # Assume the postconfigure commands should be run from the
            # source directory
            self.__commands.append('cd {}'.format(self.src_directory))
            self.__commands.extend(self.__postconfigure)

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

        # Set library path
        if self.ldconfig:
            self.__commands.append(self.ldcache_step(
                directory=posixpath.join(self.prefix, self.__libdir)))

        # Add annotations
        for key,value in self.__annotations.items():
            self.add_annotation(key, value)

        # Cleanup
        remove = [self.src_directory]
        if self.url:
            remove.append(posixpath.join(self.__wd,
                                         posixpath.basename(self.url)))
        elif self.package:
            remove.append(posixpath.join(self.__wd,
                                         posixpath.basename(self.package)))
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
