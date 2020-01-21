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
import logging # pylint: disable=unused-import
import posixpath
from copy import copy as _copy

import hpccm.config
import hpccm.templates.ConfigureMake
import hpccm.templates.envvars
import hpccm.templates.ldconfig
import hpccm.templates.rm
import hpccm.templates.tar
import hpccm.templates.wget

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.packages import packages
from hpccm.common import linux_distro
from hpccm.primitives.comment import comment
from hpccm.primitives.copy import copy
from hpccm.primitives.environment import environment
from hpccm.primitives.shell import shell
from hpccm.toolchain import toolchain

class netcdf(bb_base, hpccm.templates.ConfigureMake, hpccm.templates.envvars,
             hpccm.templates.ldconfig, hpccm.templates.rm, hpccm.templates.tar,
             hpccm.templates.wget):
    """The `netcdf` building block downloads, configures, builds, and
    installs the
    [NetCDF](https://www.unidata.ucar.edu/software/netcdf/) component.

    The [HDF5](#hdf5) building block should be installed prior to this
    building block.

    # Parameters

    check: Boolean flag to specify whether the `make check` step
    should be performed.  The default is False.

    configure_opts: List of options to pass to `configure`.  The
    default value is an empty list.

    cxx: Boolean flag to specify whether the NetCDF C++ library should
    be installed.  The default is True.

    environment: Boolean flag to specify whether the environment
    (`LD_LIBRARY_PATH` and `PATH`) should be modified to include
    NetCDF. The default is True.

    fortran: Boolean flag to specify whether the NetCDF Fortran
    library should be installed.  The default is True.

    hdf5_dir: Path to the location where HDF5 is installed in the
    container image.  The default value is `/usr/local/hdf5`.

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
    `4.7.0`.

    version_cxx: The version of NetCDF C++ to download.  The default
    value is `4.3.0`.

    version_fortran: The version of NetCDF Fortran to download.  The
    default value is `4.4.5`.

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

        self.configure_opts = kwargs.get('configure_opts', [])

        self.__c_baseurl = 'https://github.com/Unidata/netcdf-c/archive'
        self.__cxx_baseurl = 'https://github.com/Unidata/netcdf-cxx4/archive'
        self.__fortran_baseurl = 'https://github.com/Unidata/netcdf-fortran/archive'
        self.__check = kwargs.get('check', False)
        self.__cxx = kwargs.get('cxx', True)
        self.__fortran = kwargs.get('fortran', True)
        self.__hdf5_dir = kwargs.get('hdf5_dir', '/usr/local/hdf5')
        self.__ospackages = kwargs.get('ospackages', [])
        self.prefix = kwargs.get('prefix', '/usr/local/netcdf')
        self.__runtime_ospackages = [] # Filled in by __distro()
        self.__toolchain = kwargs.get('toolchain', toolchain())
        self.__version = kwargs.get('version', '4.7.0')
        self.__version_cxx = kwargs.get('version_cxx', '4.3.0')
        self.__version_fortran = kwargs.get('version_fortran', '4.4.5')
        self.__wd = '/var/tmp'

        self.__commands = [] # Filled in by __setup()

        # Set the Linux distribution specific parameters
        self.__distro()

        # C interface (required)
        self.__setup()

        # C++ interface (optional)
        if self.__cxx:
            self.__setup_optional(pkg='netcdf-cxx4',
                                  version=self.__version_cxx)

        # Fotran interface (optional)
        if self.__fortran:
            self.__setup_optional(pkg='netcdf-fortran',
                                  version=self.__version_fortran)

        # Fill in container instructions
        self.__instructions()

    def __instructions(self):
        """Fill in container instructions"""

        comments = ['NetCDF version {}'.format(self.__version)]
        if self.__cxx:
            comments.append('NetCDF C++ version {}'.format(self.__version_cxx))
        if self.__fortran:
            comments.append('NetCDF Fortran version {}'.format(self.__version_fortran))
        self += comment(', '.join(comments))

        if self.__ospackages:
            self += packages(ospackages=self.__ospackages)

        self += shell(commands=self.__commands)

        self += environment(variables=self.environment_step())

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

    def __setup(self):
        """Construct the series of shell commands, i.e., fill in
           self.__commands"""

        # Create a copy of the toolchain so that it can be modified
        # without impacting the original.
        toolchain = _copy(self.__toolchain)

        # Need to tell it where to find HDF5
        if not toolchain.CPPFLAGS:
            toolchain.CPPFLAGS = '-I{}/include'.format(self.__hdf5_dir)
        if not toolchain.LDFLAGS:
            toolchain.LDFLAGS = '-L{}/lib'.format(self.__hdf5_dir)

        # Version 4.3.1 changed the package name
        if LooseVersion(self.__version) >= LooseVersion('4.3.1'):
            pkgname = 'netcdf-c'
            tarball = 'v{0}.tar.gz'.format(self.__version)
        else:
            pkgname = 'netcdf'
            tarball = '{0}-{1}.tar.gz'.format(pkgname, self.__version)

        url = '{0}/{1}'.format(self.__c_baseurl, tarball)

        # Download source from web
        self.__commands.append(self.download_step(url=url,
                                                  directory=self.__wd))
        self.__commands.append(self.untar_step(
            tarball=posixpath.join(self.__wd, tarball), directory=self.__wd))

        self.__commands.append(self.configure_step(
            directory=posixpath.join(self.__wd,
                                     '{0}-{1}'.format(pkgname, self.__version)),
            toolchain=toolchain))

        self.__commands.append(self.build_step())

        # Check the build
        if self.__check:
            self.__commands.append(self.check_step())

        self.__commands.append(self.install_step())

        # Set library path
        libpath = posixpath.join(self.prefix, 'lib')
        if self.ldconfig:
            self.__commands.append(self.ldcache_step(directory=libpath))
        else:
            self.environment_variables['LD_LIBRARY_PATH'] = '{}:$LD_LIBRARY_PATH'.format(libpath)

        self.__commands.append(self.cleanup_step(
            items=[posixpath.join(self.__wd, tarball),
                   posixpath.join(self.__wd,
                                  '{0}-{1}'.format(pkgname, self.__version))]))

        # Set the environment
        self.environment_variables['PATH'] = '{}:$PATH'.format(
            posixpath.join(self.prefix, 'bin'))

    def __setup_optional(self, pkg='', version=''):
        # Create a copy of the toolchain so that it can be modified
        # without impacting the original.
        toolchain = _copy(self.__toolchain)

        # Need to tell it where to find NetCDF and HDF5
        if not toolchain.CPPFLAGS:
            toolchain.CPPFLAGS = '-I{0}/include -I{1}/include'.format(self.prefix, self.__hdf5_dir)
        if not toolchain.LDFLAGS:
            toolchain.LDFLAGS = '-L{}/lib'.format(self.prefix)
        if not toolchain.LD_LIBRARY_PATH:
            toolchain.LD_LIBRARY_PATH = '{}/lib:$LD_LIBRARY_PATH'.format(self.prefix)

        if pkg == 'netcdf-cxx4':
            baseurl = self.__cxx_baseurl
        elif pkg == 'netcdf-fortran':
            baseurl = self.__fortran_baseurl
        else:
            raise RuntimeError('unrecognized package name: "{}"'.format(pkg))

        tarball = 'v{0}.tar.gz'.format(version)
        url = '{0}/{1}'.format(baseurl, tarball)

        # Download source from web
        self.__commands.append(self.download_step(url=url,
                                                  directory=self.__wd))
        self.__commands.append(self.untar_step(
            tarball=posixpath.join(self.__wd, tarball), directory=self.__wd))

        self.__commands.append(self.configure_step(
            directory=posixpath.join(self.__wd,
                                     '{0}-{1}'.format(pkg, version)),
            toolchain=toolchain))

        self.__commands.append(self.build_step())

        # Check the build
        if self.__check:
            # Checks fail when using parallel make.  Disable it
            # temporarily.
            _parallel = self.parallel
            self.parallel = 1
            self.__commands.append(self.check_step())
            self.parallel = _parallel

        self.__commands.append(self.install_step())

        self.__commands.append(self.cleanup_step(
            items=[posixpath.join(self.__wd, tarball),
                   posixpath.join(self.__wd,
                                  '{0}-{1}'.format(pkg, version))]))

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
        instructions.append(copy(_from=_from, src=self.prefix,
                                 dest=self.prefix))
        if self.ldconfig:
            instructions.append(shell(
                commands=[self.ldcache_step(
                    directory=posixpath.join(self.prefix, 'lib'))]))
        instructions.append(environment(variables=self.environment_step()))
        return '\n'.join(str(x) for x in instructions)
