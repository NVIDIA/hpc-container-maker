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

"""PnetCDF building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from distutils.version import LooseVersion
import posixpath

import hpccm.config
import hpccm.templates.envvars
import hpccm.templates.ldconfig

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.generic_autotools import generic_autotools
from hpccm.building_blocks.packages import packages
from hpccm.common import linux_distro
from hpccm.primitives.comment import comment
from hpccm.toolchain import toolchain

class pnetcdf(bb_base, hpccm.templates.envvars, hpccm.templates.ldconfig):
    """The `pnetcdf` building block downloads, configures, builds, and
    installs the
    [PnetCDF](http://cucis.ece.northwestern.edu/projects/PnetCDF/index.html)
    component.

    # Parameters

    annotate: Boolean flag to specify whether to include annotations
    (labels).  The default is False.

    check: Boolean flag to specify whether the `make check` step
    should be performed.  The default is False.

    configure_opts: List of options to pass to `configure`.  The
    default values are `--enable-shared`.

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
    PnetCDF. The default is True.

    ldconfig: Boolean flag to specify whether the PnetCDF library
    directory should be added dynamic linker cache.  If False, then
    `LD_LIBRARY_PATH` is modified to include the PnetCDF library
    directory. The default value is False.

    ospackages: List of OS packages to install prior to configuring
    and building.  The default values are `m4`, `make`, `tar`, and
    `wget`.

    prefix: The top level install location.  The default value is
    `/usr/local/pnetcdf`.

    toolchain: The toolchain object.  A MPI compiler toolchain must be
    used.  The default is to use the standard MPI compiler wrappers,
    e.g., `CC=mpicc`, `CXX=mpicxx`, etc.

    version: The version of PnetCDF source to download.  The default
    value is `1.12.1`.

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
    pnetcdf(prefix='/opt/pnetcdf/1.10.0', version='1.10.0')
    ```

    ```python
    ompi = openmpi(...)
    pnetcdf(toolchain=ompi.toolchain, ...)
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(pnetcdf, self).__init__(**kwargs)

        self.__baseurl = kwargs.get('baseurl', 'https://parallel-netcdf.github.io/Release')
        self.__configure_opts = kwargs.pop('configure_opts',
                                           ['--enable-shared'])
        self.__ospackages = kwargs.pop('ospackages', ['m4', 'make', 'tar',
                                                      'wget'])
        self.__prefix = kwargs.pop('prefix', '/usr/local/pnetcdf')
        self.__runtime_ospackages = [] # Filled in by __distro()
        self.__toolchain = kwargs.pop('toolchain',
                                      toolchain(CC='mpicc', CXX='mpicxx',
                                                F77='mpif77', F90='mpif90',
                                                FC='mpifort'))
        self.__url = None # Filled in by __download()
        self.__version = kwargs.get('version', '1.12.1')

        # Set the Linux distribution specific parameters
        self.__distro()

        # Set the download specific parameters
        self.__download()

        # Set the environment variables
        self.environment_variables['PATH'] = '{}:$PATH'.format(
            posixpath.join(self.__prefix, 'bin'))
        if not self.ldconfig:
            self.environment_variables['LD_LIBRARY_PATH'] = '{}:$LD_LIBRARY_PATH'.format(posixpath.join(self.__prefix, 'lib'))

        # Setup build configuration
        self.__bb = generic_autotools(
            annotations={'version': self.__version},
            base_annotation=self.__class__.__name__,
            comment=False,
            configure_opts=self.__configure_opts,
            devel_environment=self.environment_variables,
            # For some compilers, --enable-shared leads to the following error:
            #   GEN      libpnetcdf.la
            # /usr/bin/ld: .libs/libpnetcdf.lax/libf77.a/strerrnof.o: relocation R_X86_64_32 against `.data' can not be used when making a shared object; recompile with -fPIC
            # .libs/libpnetcdf.lax/libf77.a/strerrnof.o: error adding symbols: Bad value
            # Apply the workaround
            postconfigure=['sed -i -e \'s#pic_flag=""#pic_flag=" -fpic -DPIC"#\' -e \'s#wl=""#wl="-Wl,"#\' libtool'] if '--enable-shared' in self.__configure_opts else None,
            prefix=self.__prefix,
            runtime_environment=self.environment_variables,
            toolchain=self.__toolchain,
            url=self.__url,
            **kwargs)

        # Container instructions
        self += comment('PnetCDF version {}'.format(self.__version))
        self += packages(ospackages=self.__ospackages)
        self += self.__bb

    def __distro(self):
        """Based on the Linux distribution, set values accordingly.  A user
        specified value overrides any defaults."""

        if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
            self.__runtime_ospackages = ['libatomic1']
        elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
            pass
        else: # pragma: no cover
            raise RuntimeError('Unknown Linux distribution')

    def __download(self):
        """Set download source based on user parameters"""

        # Version 1.11.0 changed the package name
        if LooseVersion(self.__version) >= LooseVersion('1.11.0'):
            pkgname = 'pnetcdf'
        else:
            pkgname = 'parallel-netcdf'
        tarball = '{0}-{1}.tar.gz'.format(pkgname, self.__version)
        self.__url = '{0}/{1}'.format(self.__baseurl, tarball)

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples

        ```python
        p = pnetcdf(...)
        Stage0 += p
        Stage1 += p.runtime()
        ```
        """
        instructions = []
        instructions.append(comment('PnetCDF'))
        if self.__runtime_ospackages:
            instructions.append(packages(ospackages=self.__runtime_ospackages))
        instructions.append(self.__bb.runtime(_from=_from))
        return '\n'.join(str(x) for x in instructions)
