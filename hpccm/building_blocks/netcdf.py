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

"""NetCDF building block"""

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

class netcdf(bb_base, hpccm.templates.envvars, hpccm.templates.ldconfig):
    """The `netcdf` building block downloads, configures, builds, and
    installs the
    [NetCDF](https://www.unidata.ucar.edu/software/netcdf/) component.

    The [HDF5](#hdf5) building block should be installed prior to this
    building block.

    # Parameters

    annotate: Boolean flag to specify whether to include annotations
    (labels).  The default is False.

    check: Boolean flag to specify whether the `make check` step
    should be performed.  The default is False.

    configure_opts: List of options to pass to `configure`.  The
    default value is an empty list.

    cxx: Boolean flag to specify whether the NetCDF C++ library should
    be installed.  The default is True.

    disable_FEATURE: Flags to control disabling features when
    configuring.  For instance, `disable_foo=True` maps to
    `--disable-foo`.  Underscores in the parameter name are converted
    to dashes.

    enable_FEATURE[=ARG]: Flags to control enabling features when
    configuring.  For instance, `enable_foo=True` maps to
    `--enable-foo` and `enable_foo='yes'` maps to `--enable-foo=yes`.
    Underscores in the parameter name are converted to dashes.

    environment: Boolean flag to specify whether the environment
    (`CPATH`, `LD_LIBRARY_PATH`, `LIBRARY_PATH` and `PATH`) should be
    modified to include NetCDF. The default is True.

    fortran: Boolean flag to specify whether the NetCDF Fortran
    library should be installed.  The default is True.

    ldconfig: Boolean flag to specify whether the NetCDF library
    directory should be added dynamic linker cache.  If False, then
    `LD_LIBRARY_PATH` is modified to include the NetCDF library
    directory. The default value is False.

    ospackages: List of OS packages to install prior to configuring
    and building.  For Ubuntu, the default values are
    `ca-certificates`, `file`, `libcurl4-openssl-dev`, `m4`, `make`,
    `wget`, and `zlib1g-dev`.  For RHEL-based Linux distributions the
    default values are `ca-certificates`, `file`, `libcurl-devel`
    `m4`, `make`, `wget`, and `zlib-devel`.

    prefix: The top level install location.  The default location is
    `/usr/local/netcdf`.

    toolchain: The toolchain object.  This should be used if
    non-default compilers or other toolchain options are needed.  The
    default is empty.

    version: The version of NetCDF to download.  The default value is
    `4.7.3`.

    version_cxx: The version of NetCDF C++ to download.  The default
    value is `4.3.1`.

    version_fortran: The version of NetCDF Fortran to download.  The
    default value is `4.5.2`.

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
    netcdf(prefix='/opt/netcdf/4.6.1', version='4.6.1')
    ```

    ```python
    p = pgi(eula=True)
    netcdf(toolchain=p.toolchain)
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(netcdf, self).__init__(**kwargs)

        self.__baseurl_c = 'https://github.com/Unidata/netcdf-c/archive'
        self.__baseurl_cxx = 'https://github.com/Unidata/netcdf-cxx4/archive'
        self.__baseurl_fortran = 'https://github.com/Unidata/netcdf-fortran/archive'
        self.__check = kwargs.pop('check', False)
        self.__cxx = kwargs.pop('cxx', True)
        self.__fortran = kwargs.pop('fortran', True)
        self.__ospackages = kwargs.pop('ospackages', [])
        self.__prefix = kwargs.pop('prefix', '/usr/local/netcdf')
        self.__runtime_ospackages = [] # Filled in by __distro()
        self.__version = kwargs.pop('version', '4.7.3')
        self.__version_cxx = kwargs.pop('version_cxx', '4.3.1')
        self.__version_fortran = kwargs.pop('version_fortran', '4.5.2')

        # Set the Linux distribution specific parameters
        self.__distro()

        # Set the download specific parameters
        self.__download()

        # Setup the environment variables
        self.environment_variables['CPATH'] = '{}:$CPATH'.format(
            posixpath.join(self.__prefix, 'include'))
        self.environment_variables['LIBRARY_PATH'] = '{}:$LIBRARY_PATH'.format(
            posixpath.join(self.__prefix, 'lib'))
        self.environment_variables['PATH'] = '{}:$PATH'.format(
            posixpath.join(self.__prefix, 'bin'))
        if not self.ldconfig:
            self.environment_variables['LD_LIBRARY_PATH'] = '{}:$LD_LIBRARY_PATH'.format(posixpath.join(self.__prefix, 'lib'))

        # Setup build configuration
        comments = ['NetCDF version {}'.format(self.__version)]
        self.__bb = [generic_autotools(
            annotations={'version': self.__version},
            base_annotation=self.__class__.__name__,
            check=self.__check,
            comment=False,
            devel_environment=self.environment_variables,
            directory=self.__directory_c,
            prefix=self.__prefix,
            runtime_environment=self.environment_variables,
            url=self.__url_c,
            **kwargs)]

        # Setup optional CXX build configuration
        if self.__cxx:
            comments.append('NetCDF C++ version {}'.format(self.__version_cxx))
            self.__bb.append(generic_autotools(
                annotations={'version': self.__version_cxx},
                base_annotation='{}-cxx4'.format(self.__class__.__name__),
                check=self.__check,
                comment=False,
                directory='netcdf-cxx4-{}'.format(self.__version_cxx),
                # Checks fail when using parallel make.  Disable it.
                parallel=1 if self.__check else '$(nproc)',
                prefix=self.__prefix,
                url='{0}/v{1}.tar.gz'.format(self.__baseurl_cxx,
                                             self.__version_cxx),
                **kwargs))

        # Setup optional Fortran build configuration
        if self.__fortran:
            comments.append('NetCDF Fortran version {}'.format(self.__version_fortran))
            self.__bb.append(generic_autotools(
                annotations={'version': self.__version_fortran},
                base_annotation='{}-fortran'.format(self.__class__.__name__),
                check=self.__check,
                comment=False,
                directory='netcdf-fortran-{}'.format(self.__version_fortran),
                # Checks fail when using parallel make.  Disable it.
                parallel=1 if self.__check else '$(nproc)',
                prefix=self.__prefix,
                url='{0}/v{1}.tar.gz'.format(self.__baseurl_fortran,
                                             self.__version_fortran),
                **kwargs))

        # Container instructions
        self += comment(', '.join(comments))
        self += packages(ospackages=self.__ospackages)
        self += [bb for bb in self.__bb]

    def __distro(self):
        """Based on the Linux distribution, set values accordingly.  A user
        specified value overrides any defaults."""

        if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
            if not self.__ospackages:
                self.__ospackages = ['ca-certificates', 'file',
                                     'libcurl4-openssl-dev', 'm4', 'make',
                                     'wget', 'zlib1g-dev']
            self.__runtime_ospackages = ['zlib1g']
        elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
            if not self.__ospackages:
                self.__ospackages = ['ca-certificates', 'file',
                                     'libcurl-devel', 'm4', 'make',
                                     'wget', 'zlib-devel']
                if self.__check:
                    self.__ospackages.append('diffutils')
            self.__runtime_ospackages = ['zlib']
        else: # pragma: no cover
            raise RuntimeError('Unknown Linux distribution')

    def __download(self):
        """Set download source based on user parameters"""

        # Version 4.3.1 changed the package name
        if LooseVersion(self.__version) >= LooseVersion('4.3.1'):
            pkgname = 'netcdf-c'
            tarball = 'v{0}.tar.gz'.format(self.__version)
        else:
            pkgname = 'netcdf'
            tarball = '{0}-{1}.tar.gz'.format(pkgname, self.__version)

        self.__directory_c = '{0}-{1}'.format(pkgname, self.__version)
        self.__url_c = '{0}/{1}'.format(self.__baseurl_c, tarball)

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples

        ```python
        n = netcdf(...)
        Stage0 += n
        Stage1 += n.runtime()
        ```
        """
        instructions = []
        instructions.append(comment('NetCDF'))
        instructions.append(packages(ospackages=self.__runtime_ospackages))
        instructions.append(self.__bb[0].runtime(_from=_from))
        return '\n'.join(str(x) for x in instructions)
