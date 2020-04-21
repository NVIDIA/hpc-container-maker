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

"""CGNS building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import posixpath
import re
from copy import copy as _copy

import hpccm.config

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.generic_autotools import generic_autotools
from hpccm.building_blocks.packages import packages
from hpccm.common import linux_distro
from hpccm.primitives.comment import comment
from hpccm.toolchain import toolchain

class cgns(bb_base):
    """The `cgns` building block downloads and installs the
    [CGNS](https://cgns.github.io/index.html) component.

    The [HDF5](#hdf5) building block should be installed prior to this
    building block.

    # Parameters

    annotate: Boolean flag to specify whether to include annotations
    (labels).  The default is False.

    check: Boolean flag to specify whether the test cases should be
    run.  The default is False.

    configure_opts: List of options to pass to `configure`.  The
    default value is `--with-hdf5=/usr/local/hdf5` and `--with-zlib`.

    disable_FEATURE: Flags to control disabling features when
    configuring.  For instance, `disable_foo=True` maps to
    `--disable-foo`.  Underscores in the parameter name are converted
    to dashes.

    enable_FEATURE[=ARG]: Flags to control enabling features when
    configuring.  For instance, `enable_foo=True` maps to
    `--enable-foo` and `enable_foo='yes'` maps to `--enable-foo=yes`.
    Underscores in the parameter name are converted to dashes.

    prefix: The top level install location.  The default value is
    `/usr/local/cgns`.

    ospackages: List of OS packages to install prior to configuring
    and building.  For Ubuntu, the default values are `file`, `make`,
    `wget`, and `zlib1g-dev`.  For RHEL-based Linux distributions the
    default values are `bzip2`, `file`, `make`, `wget` and
    `zlib-devel`.

    toolchain: The toolchain object.  This should be used if
    non-default compilers or other toolchain options are needed.  The
    default is empty.

    version: The version of CGNS source to download.  The default
    value is `3.4.0`.

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
    cgns(prefix='/opt/cgns/3.3.1', version='3.3.1')
    ```
    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(cgns, self).__init__(**kwargs)

        self.__baseurl = kwargs.pop('baseurl', 'https://github.com/CGNS/CGNS/archive')
        self.__check = kwargs.pop('check', False)
        self.__configure_opts = kwargs.pop('configure_opts',
                                           ['--with-hdf5=/usr/local/hdf5',
                                            '--with-zlib'])
        self.__ospackages = kwargs.pop('ospackages', [])
        self.__prefix = kwargs.pop('prefix', '/usr/local/cgns')
        self.__toolchain = kwargs.pop('toolchain', toolchain())
        self.__version = kwargs.pop('version', '3.4.0')

        # Set the configuration options
        self.__configure()

        # Set the Linux distribution specific parameters
        self.__distro()

        # Setup build configuration
        self.__bb = generic_autotools(
            annotations={'version': self.__version},
            base_annotation=self.__class__.__name__,
            check=self.__check,
            comment=False,
            configure_opts=self.__configure_opts,
            directory=posixpath.join('CGNS-{}'.format(self.__version), 'src'),
            prefix=self.__prefix,
            toolchain=self.__toolchain,
            url='{0}/v{1}.tar.gz'.format(self.__baseurl, self.__version),
            **kwargs)

        # Container instructions
        self += comment('CGNS version {}'.format(self.__version))
        self += packages(ospackages=self.__ospackages)
        self += self.__bb

    def __configure(self):
        """Setup configure options based on user parameters"""

        # Create a copy of the toolchain so that it can be modified
        # without impacting the original.
        self.__toolchain = _copy(self.__toolchain)

        # See https://cgns.github.io/download.html, Known Bugs
        if not self.__toolchain.LIBS:
            self.__toolchain.LIBS = '-Wl,--no-as-needed -ldl'
        if not self.__toolchain.FLIBS:
            self.__toolchain.FLIBS = '-Wl,--no-as-needed -ldl'
        # See https://cgnsorg.atlassian.net/browse/CGNS-40
        if (not self.__toolchain.FFLAGS and self.__toolchain.FC and
            re.match('.*pgf.*', self.__toolchain.FC)):
            self.__toolchain.FFLAGS = '-Mx,125,0x200'

    def __distro(self):
        """Based on the Linux distribution, set values accordingly.  A user
        specified value overrides any defaults."""

        if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
            if not self.__ospackages:
                self.__ospackages = ['file', 'make', 'wget', 'zlib1g-dev']
            self.__runtime_ospackages = ['zlib1g']
        elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
            if not self.__ospackages:
                self.__ospackages = ['bzip2', 'file', 'make', 'wget',
                                     'zlib-devel']
                if self.__check:
                    self.__ospackages.append('diffutils')
            self.__runtime_ospackages = ['zlib']
        else: # pragma: no cover
            raise RuntimeError('Unknown Linux distribution')

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Example

        ```python
        c = cgns(...)
        Stage0 += c
        Stage1 += c.runtime()
        ```
        """
        instructions = []
        instructions.append(comment('CGNS'))
        instructions.append(packages(ospackages=self.__runtime_ospackages))
        instructions.append(self.__bb.runtime(_from=_from))
        return '\n'.join(str(x) for x in instructions)
