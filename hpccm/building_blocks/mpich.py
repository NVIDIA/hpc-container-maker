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

"""MPICH building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import posixpath
import re
from copy import copy as _copy

import hpccm.config
import hpccm.templates.envvars
import hpccm.templates.ldconfig

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.generic_autotools import generic_autotools
from hpccm.building_blocks.packages import packages
from hpccm.common import linux_distro
from hpccm.primitives.comment import comment
from hpccm.toolchain import toolchain

class mpich(bb_base, hpccm.templates.envvars, hpccm.templates.ldconfig):
    """The `mpich` building block configures, builds, and installs the
    [MPICH](https://www.mpich.org) component.

    As a side effect, a toolchain is created containing the MPI
    compiler wrappers.  The tool can be passed to other operations
    that want to build using the MPI compiler wrappers.

    # Parameters

    annotate: Boolean flag to specify whether to include annotations
    (labels).  The default is False.

    check: Boolean flag to specify whether the `make check` and `make
    testing` steps should be performed.  The default is False.

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
    (`LD_LIBRARY_PATH` and `PATH`) should be modified to include
    MPICH. The default is True.

    ldconfig: Boolean flag to specify whether the MPICH library
    directory should be added dynamic linker cache.  If False, then
    `LD_LIBRARY_PATH` is modified to include the MPICH library
    directory. The default value is False.

    ospackages: List of OS packages to install prior to configuring
    and building.  For Ubuntu, the default values are `file`, `gzip`,
    `make`, `openssh-client`, `perl`, `tar`, and `wget`.  For
    RHEL-based Linux distributions, the default values are `file`,
    `gzip`, `make`, `openssh-clients`, `perl`, `tar`, and `wget`.

    prefix: The top level install location.  The default value is
    `/usr/local/mpich`.

    toolchain: The toolchain object.  This should be used if
    non-default compilers or other toolchain options are needed.  The
    default is empty.

    version: The version of MPICH source to download.  The default
    value is `3.3.2`.

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
    mpich(prefix='/opt/mpich/3.3', version='3.3')
    ```

    ```python
    p = pgi(eula=True)
    mpich(toolchain=p.toolchain)
    ```
    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(mpich, self).__init__(**kwargs)

        self.__baseurl = kwargs.pop('baseurl',
                                    'https://www.mpich.org/static/downloads')
        self.__check = kwargs.pop('check', False)
        self.__configure_opts = kwargs.pop('configure_opts', [])
        self.__ospackages = kwargs.pop('ospackages', [])
        self.__prefix = kwargs.pop('prefix', '/usr/local/mpich')
        self.__runtime_ospackages = [] # Filled in by __distro()
        # Input toolchain, i.e., what to use when building
        self.__toolchain = kwargs.pop('toolchain', toolchain())
        self.__version = kwargs.pop('version', '3.3.2')

        # Output toolchain
        self.toolchain = toolchain(CC='mpicc', CXX='mpicxx', F77='mpif77',
                                   F90='mpif90', FC='mpifort')

        # Set the configuration options
        self.__configure()

        # Set the Linux distribution specific parameters
        self.__distro()

        # Set the environment variables
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
            configure_opts=self.__configure_opts,
            devel_environment=self.environment_variables,
            # Run test suite (must be after install)
            postinstall=['cd /var/tmp/mpich-{}'.format(self.__version),
                         'RUNTESTS_SHOWPROGRESS=1 make testing'] if self.__check else None,
            prefix=self.__prefix,
            runtime_environment=self.environment_variables,
            toolchain=self.__toolchain,
            url='{0}/{1}/mpich-{1}.tar.gz'.format(self.__baseurl,
                                                  self.__version),
            **kwargs)

        # Container instructions
        self += comment('MPICH version {}'.format(self.__version))
        self += packages(ospackages=self.__ospackages)
        self += self.__bb

    def __configure(self):
        """Setup configure options based on user parameters"""

        # Create a copy of hte toolchain so that it can be modified
        # without impacting the original
        self.__toolchain = _copy(self.__toolchain)

        # MPICH does not accept F90
        self.__toolchain.F90 = ''

        # Workaround issue with the PGI compiler
        # https://lists.mpich.org/pipermail/discuss/2017-July/005235.html
        if self.__toolchain.CC and re.match('.*pgcc', self.__toolchain.CC):
            self.__configure_opts.append('--disable-fast')

    def __distro(self):
        """Based on the Linux distribution, set values accordingly.  A user
        specified value overrides any defaults."""

        if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
            if not self.__ospackages:
                self.__ospackages = ['file', 'gzip', 'make', 'openssh-client',
                                     'perl', 'tar', 'wget']
            self.__runtime_ospackages = ['openssh-client']
        elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
            if not self.__ospackages:
                self.__ospackages = ['file', 'gzip', 'make',
                                     'openssh-clients', 'perl', 'tar', 'wget']
            self.__runtime_ospackages = ['openssh-clients']
        else: # pragma: no cover
            raise RuntimeError('Unknown Linux distribution')

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples
        ```python
        m = mpich(...)
        Stage0 += m
        Stage1 += m.runtime()
        ```
        """
        instructions = []
        instructions.append(comment('MPICH'))
        instructions.append(packages(ospackages=self.__runtime_ospackages))
        instructions.append(self.__bb.runtime(_from=_from))
        return '\n'.join(str(x) for x in instructions)
