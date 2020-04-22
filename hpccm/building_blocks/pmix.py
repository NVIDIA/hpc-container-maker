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

"""PMIX building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import posixpath

import hpccm.config
import hpccm.templates.envvars
import hpccm.templates.ldconfig

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.generic_autotools import generic_autotools
from hpccm.building_blocks.packages import packages
from hpccm.common import linux_distro
from hpccm.primitives.comment import comment

class pmix(bb_base,hpccm.templates.envvars, hpccm.templates.ldconfig):
    """The `pmix` building block configures, builds, and installs the
    [PMIX](https://github.com/openpmix/openpmix) component.

    # Parameters

    annotate: Boolean flag to specify whether to include annotations
    (labels).  The default is False.

    check: Boolean flag to specify whether the `make check` step
    should be performed.  The default is False.

    configure_opts: List of options to pass to `configure`.  The
    default is an empty list.

    disable_FEATURE: Flags to control disabling features when
    configuring.  For instance, `disable_foo=True` maps to
    `--disable-foo`.  Underscores in the parameter name are converted
    to dashes.

    enable_FEATURE[=ARG]: Flags to control enabling features when
    configuring.  For instance, `enable_foo=True` maps to
    `--enable-foo` and `enable_foo='yes'` maps to `--enable-foo=yes`.
    Underscores in the parameter name are converted to dashes.

    environment: Boolean flag to specify whether the environment
    (`CPATH`, `LD_LIBRARY_PATH`, and `PATH`) should be modified to
    include PMIX. The default is True.

    ldconfig: Boolean flag to specify whether the PMIX library
    directory should be added dynamic linker cache.  If False, then
    `LD_LIBRARY_PATH` is modified to include the PMIX library
    directory. The default value is False.

    ospackages: List of OS packages to install prior to configuring
    and building.  For Ubuntu, the default values are `file`, `hwloc`,
    `libevent-dev`, `make`, `tar`, and `wget`. For RHEL-based Linux
    distributions, the default values are `file`, `hwloc`,
    `libevent-devel`, `make`, `tar`, and `wget`.

    prefix: The top level install location.  The default value is
    `/usr/local/pmix`.

    toolchain: The toolchain object.  This should be used if
    non-default compilers or other toolchain options are needed.  The
    default value is empty.

    version: The version of PMIX source to download.  The default value
    is `3.1.4`.

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
    pmix(prefix='/opt/pmix/3.1.4', version='3.1.4')
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(pmix, self).__init__(**kwargs)

        self.__baseurl = kwargs.pop('baseurl', 'https://github.com/openpmix/openpmix/releases/download')
        self.__check = kwargs.pop('check', False)
        self.__ospackages = kwargs.pop('ospackages', [])
        self.__prefix = kwargs.pop('prefix', '/usr/local/pmix')
        self.__runtime_ospackages = [] # Filled in by __distro()
        self.__version = kwargs.pop('version', '3.1.4')

        # Set the Linux distribution specific parameters
        self.__distro()

        # Set the environment variables
        self.environment_variables['CPATH'] = '{}:$CPATH'.format(
            posixpath.join(self.__prefix, 'include'))
        self.environment_variables['PATH'] = '{}:$PATH'.format(
            posixpath.join(self.__prefix, 'bin'))
        if not self.ldconfig:
            self.environment_variables['LD_LIBRARY_PATH'] = '{}:$LD_LIBRARY_PATH'.format(posixpath.join(self.__prefix, 'lib'))

        # Setup build configuration
        self.__bb = generic_autotools(
            annotations={'version': self.__version},
            base_annotation=self.__class__.__name__,
            check=self.__check,
            comment=False,
            devel_environment=self.environment_variables,
            prefix=self.__prefix,
            runtime_environment=self.environment_variables,
            url='{0}/v{1}/pmix-{1}.tar.gz'.format(self.__baseurl,
                                                  self.__version),
            **kwargs)

        # Container instructions
        self += comment('PMIX version {}'.format(self.__version))
        self += packages(ospackages=self.__ospackages)
        self += self.__bb

    def __distro(self):
        """Based on the Linux distribution, set values accordingly.  A user
        specified value overrides any defaults."""

        if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
            if not self.__ospackages:
                self.__ospackages = ['file', 'hwloc', 'libevent-dev', 'make',
                                     'tar', 'wget']
                if self.__check:
                    self.__ospackages.append('perl')
            self.__runtime_ospackages = ['libevent-2.*',
                                         'libevent-pthreads-2.*']
        elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
            if not self.__ospackages:
                self.__ospackages = ['file', 'hwloc', 'libevent-devel', 'make',
                                     'tar', 'wget']
                if self.__check:
                    self.__ospackages.append('perl')
            self.__runtime_ospackages = ['libevent']
        else: # pragma: no cover
            raise RuntimeError('Unknown Linux distribution')

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples

        ```python
        p = pmix(...)
        Stage0 += p
        Stage1 += p.runtime()
        ```
        """
        instructions = []
        instructions.append(comment('PMIX'))
        instructions.append(packages(ospackages=self.__runtime_ospackages))
        instructions.append(self.__bb.runtime(_from=_from))
        return '\n'.join(str(x) for x in instructions)
