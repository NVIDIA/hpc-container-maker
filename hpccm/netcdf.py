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

import logging # pylint: disable=unused-import
import os
from copy import copy as _copy

import hpccm.config

from hpccm.ConfigureMake import ConfigureMake
from hpccm.comment import comment
from hpccm.common import linux_distro
from hpccm.copy import copy
from hpccm.environment import environment
from hpccm.packages import packages
from hpccm.shell import shell
from hpccm.tar import tar
from hpccm.toolchain import toolchain
from hpccm.wget import wget

class netcdf(ConfigureMake, tar, wget):
    """NetCDF building block"""

    def __init__(self, **kwargs):
        """Initialize building block"""

        # Trouble getting MRO with kwargs working correctly, so just call
        # the parent class constructors manually for now.
        #super(netcdf, self).__init__(**kwargs)
        ConfigureMake.__init__(self, **kwargs)
        tar.__init__(self, **kwargs)
        wget.__init__(self, **kwargs)

        self.configure_opts = kwargs.get('configure_opts', [])

        self.__baseurl = 'https://www.unidata.ucar.edu/downloads/netcdf/ftp'
        self.__check = kwargs.get('check', False)
        self.__cxx = kwargs.get('cxx', True)
        self.__fortran = kwargs.get('fortran', True)
        self.__hdf5_dir = kwargs.get('hdf5_dir', '/usr/local/hdf5')
        self.__ospackages = kwargs.get('ospackages', [])
        self.prefix = kwargs.get('prefix', '/usr/local/netcdf')
        self.__runtime_ospackages = [] # Filled in by __distro()
        self.__toolchain = kwargs.get('toolchain', toolchain())
        self.__version = kwargs.get('version', '4.6.1')
        self.__version_cxx = kwargs.get('version_cxx', '4.3.0')
        self.__version_fortran = kwargs.get('version_fortran', '4.4.4')
        self.__wd = '/var/tmp'

        self.__commands = [] # Filled in by __setup()
        self.__environment_variables = {
            'PATH': '{}:$PATH'.format(os.path.join(self.prefix, 'bin')),
            'LD_LIBRARY_PATH':
            '{}:$LD_LIBRARY_PATH'.format(os.path.join(self.prefix, 'lib'))}

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

    def __str__(self):
        """String representation of the building block"""

        instructions = []

        comments = ['NetCDF version {}'.format(self.__version)]
        if self.__cxx:
            comments.append('NetCDF C++ version {}'.format(self.__version_cxx))
        if self.__fortran:
            comments.append('NetCDF Fortran version {}'.format(self.__version_fortran))
        instructions.append(comment(', '.join(comments)))

        if self.__ospackages:
            instructions.append(packages(ospackages=self.__ospackages))

        instructions.append(shell(commands=self.__commands))

        instructions.append(environment(
            variables=self.__environment_variables))

        return '\n'.join(str(x) for x in instructions)

    def cleanup_step(self, items=None):
        """Cleanup temporary files"""

        if not items: # pragma: no cover
            logging.warning('items are not defined')
            return ''

        return 'rm -rf {}'.format(' '.join(items))

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

        tarball = 'netcdf-{}.tar.gz'.format(self.__version)
        url = '{0}/{1}'.format(self.__baseurl, tarball)

        # Download source from web
        self.__commands.append(self.download_step(url=url,
                                                  directory=self.__wd))
        self.__commands.append(self.untar_step(
            tarball=os.path.join(self.__wd, tarball), directory=self.__wd))

        self.__commands.append(self.configure_step(
            directory=os.path.join(self.__wd,
                                   'netcdf-{}'.format(self.__version)),
            toolchain=toolchain))

        self.__commands.append(self.build_step())

        # Check the build
        if self.__check:
            self.__commands.append(self.check_step())

        self.__commands.append(self.install_step())

        self.__commands.append(self.cleanup_step(
            items=[os.path.join(self.__wd, tarball),
                   os.path.join(self.__wd,
                                'netcdf-{}'.format(self.__version))]))

    def __setup_optional(self, pkg='', version=''):
        # Create a copy of the toolchain so that it can be modified
        # without impacting the original.
        toolchain = _copy(self.__toolchain)

        # Need to tell it where to find NetCDF
        if not toolchain.CPPFLAGS:
            toolchain.CPPFLAGS = '-I{}/include'.format(self.prefix)
        if not toolchain.LDFLAGS:
            toolchain.LDFLAGS = '-L{}/lib'.format(self.prefix)
        if not toolchain.LD_LIBRARY_PATH:
            toolchain.LD_LIBRARY_PATH = '{}/lib:$LD_LIBRARY_PATH'.format(self.prefix)

        tarball = '{0}-{1}.tar.gz'.format(pkg, version)
        url = '{0}/{1}'.format(self.__baseurl, tarball)

        # Download source from web
        self.__commands.append(self.download_step(url=url,
                                                  directory=self.__wd))
        self.__commands.append(self.untar_step(
            tarball=os.path.join(self.__wd, tarball), directory=self.__wd))

        self.__commands.append(self.configure_step(
            directory=os.path.join(self.__wd,
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
            items=[os.path.join(self.__wd, tarball),
                   os.path.join(self.__wd,
                                '{0}-{1}'.format(pkg, version))]))

    def runtime(self, _from='0'):
        """Install the runtime from a full build in a previous stage"""
        instructions = []
        instructions.append(comment('NetCDF'))
        instructions.append(packages(ospackages=self.__runtime_ospackages))
        instructions.append(copy(_from=_from, src=self.prefix,
                                 dest=self.prefix))
        instructions.append(environment(
            variables=self.__environment_variables))
        return instructions
