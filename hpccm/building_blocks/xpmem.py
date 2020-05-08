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

"""XPMEM building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import posixpath

import hpccm.templates.envvars
import hpccm.templates.ldconfig

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.generic_autotools import generic_autotools
from hpccm.building_blocks.packages import packages
from hpccm.primitives.comment import comment

class xpmem(bb_base, hpccm.templates.envvars, hpccm.templates.ldconfig):
    """The `xpmem` building block builds and installs the user space
    library from the [XPMEM](https://gitlab.com/hjelmn/xpmem)
    component.

    # Parameters

    annotate: Boolean flag to specify whether to include annotations
    (labels).  The default is False.

    branch: The branch of XPMEM to use.  The default value is
    `master`.

    configure_opts: List of options to pass to `configure`.  The
    default values are `--disable-kernel-module`.

    disable_FEATURE: Flags to control disabling features when
    configuring.  For instance, `disable_foo=True` maps to
    `--disable-foo`.  Underscores in the parameter name are converted
    to dashes.

    enable_FEATURE[=ARG]: Flags to control enabling features when
    configuring.  For instance, `enable_foo=True` maps to
    `--enable-foo` and `enable_foo='yes'` maps to `--enable-foo=yes`.
    Underscores in the parameter name are converted to dashes.

    environment: Boolean flag to specify whether the environment
    (`CPATH`, `LD_LIBRARY_PATH` and `LIBRARY_PATH`) should be modified
    to include XPMEM. The default is True.

    ldconfig: Boolean flag to specify whether the XPMEM library
    directory should be added dynamic linker cache.  If False, then
    `LD_LIBRARY_PATH` is modified to include the XPMEM library
    directory. The default value is False.

    ospackages: List of OS packages to install prior to configuring
    and building.  The default value are `autoconf`, `automake`,
    `ca-certificates`, `file, `git`, `libtool`, and `make`.

    prefix: The top level install location.  The default value is
    `/usr/local/xpmem`.

    toolchain: The toolchain object.  This should be used if
    non-default compilers or other toolchain options are needed.  The
    default is empty.

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
    xpmem(prefix='/opt/xpmem', branch='master')
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(xpmem, self).__init__(**kwargs)

        # Parameters
        self.__branch = kwargs.pop('branch', 'master')
        self.__configure_opts = kwargs.pop('configure_opts',
                                           ['--disable-kernel-module'])
        self.__ospackages = kwargs.pop('ospackages', ['autoconf', 'automake',
                                                      'ca-certificates',
                                                      'file', 'git',
                                                      'libtool', 'make'])
        self.__prefix = kwargs.pop('prefix', '/usr/local/xpmem')
        self.__repository = kwargs.pop('repository',
                                       'https://gitlab.com/hjelmn/xpmem.git')

        # Setup the environment variables
        self.environment_variables['CPATH'] = '{}:$CPATH'.format(
            posixpath.join(self.__prefix, 'include'))
        self.environment_variables['LIBRARY_PATH'] = '{}:$LIBRARY_PATH'.format(
            posixpath.join(self.__prefix, 'lib'))
        if not self.ldconfig:
            self.environment_variables['LD_LIBRARY_PATH'] = '{}:$LD_LIBRARY_PATH'.format(posixpath.join(self.__prefix, 'lib'))

        # Setup build configuration
        self.__bb = generic_autotools(
            base_annotation=self.__class__.__name__,
            branch=self.__branch,
            comment=False,
            configure_opts=self.__configure_opts,
            devel_environment=self.environment_variables,
            preconfigure=['autoreconf --install'],
            prefix=self.__prefix,
            repository=self.__repository,
            runtime_environment=self.environment_variables,
            **kwargs)

        # Container instructions
        self += comment('XPMEM branch {}'.format(self.__branch))
        self += packages(ospackages=self.__ospackages)
        self += self.__bb

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples

        ```python
        x = xpmem(...)
        Stage0 += x
        Stage1 += x.runtime()
        ```
        """
        instructions = []
        instructions.append(comment('XPMEM'))
        instructions.append(self.__bb.runtime(_from=_from))
        return '\n'.join(str(x) for x in instructions)
