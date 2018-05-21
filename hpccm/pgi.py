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

"""PGI building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import re
import os

import hpccm.config

from hpccm.comment import comment
from hpccm.common import linux_distro
from hpccm.copy import copy
from hpccm.environment import environment
from hpccm.packages import packages
from hpccm.shell import shell
from hpccm.tar import tar
from hpccm.toolchain import toolchain
from hpccm.wget import wget

class pgi(tar, wget):
    """PGI building block"""

    def __init__(self, **kwargs):
        """Initialize building block"""

        # Trouble getting MRO with kwargs working correctly, so just call
        # the parent class constructors manually for now.
        #super(pgi, self).__init__(**kwargs)
        tar.__init__(self, **kwargs)
        wget.__init__(self, **kwargs)

        self.__basepath = '/opt/pgi/linux86-64/'
        self.__commands = [] # Filled in by __setup()

        # By setting this value to True, you agree to the PGI End-User
        # License Agreement (https://www.pgroup.com/doc/LICENSE.txt)
        self.__eula = kwargs.get('eula', False)

        self.__ospackages = kwargs.get('ospackages', [])
        self.__referer = r'https://www.pgroup.com/products/community.htm?utm_source=hpccm\&utm_medium=wgt\&utm_campaign=CE\&nvid=nv-int-14-39155'
        self.__system_cuda = kwargs.get('system_cuda', False)
        self.__tarball = kwargs.get('tarball', '')
        self.__url = 'https://www.pgroup.com/support/downloader.php?file=pgi-community-linux-x64'

        # The version is fragile since the latest version is
        # automatically downloaded, which may not match this default.
        self.__version = kwargs.get('version', '18.4')
        self.__wd = '/tmp/pgi' # working directory

        self.toolchain = toolchain(CC='pgcc', CXX='pgc++', F77='pgfortran',
                                   F90='pgfortran', FC='pgfortran')

        # Set the Linux distribution specific parameters
        self.__distro()

        # Construct the series of steps to execute
        self.__setup()

    def __str__(self):
        """String representation of the building block"""

        ospackages = list(self.__ospackages)
        # Installer needs perl
        ospackages.append('perl')

        instructions = []
        instructions.append(comment(
            'PGI compiler version {}'.format(self.__version)))
        if self.__tarball:
            # Use tarball from local build context
            instructions.append(
                copy(src=self.__tarball,
                     dest=os.path.join(self.__wd, self.__tarball)))
        else:
            # Downloading, so need wget
            ospackages.append('wget')

        if ospackages:
            instructions.append(packages(ospackages=ospackages))

        instructions.append(shell(commands=self.__commands))
        instructions.append(environment(
            variables={'PATH': '{}:$PATH'.format(os.path.join(self.__basepath,
                                                              self.__version,
                                                              'bin')),
                       'LD_LIBRARY_PATH': '{}:$LD_LIBRARY_PATH'.format(
                           os.path.join(self.__basepath, self.__version,
                                        'lib'))}))

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
                self.__ospackages = ['libnuma1']
        elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
            if not self.__ospackages:
                self.__ospackages = ['numactl-libs']
        else:
            raise RuntimeError('Unknown Linux disribution')

    def __setup(self):
        """Construct the series of shell commands, i.e., fill in
           self.__commands"""

        if self.__tarball:
            # Use tarball from local build context
            tarball = self.__tarball

            # Figure out the version from the tarball name
            match = re.match(r'pgilinux-\d+-(?P<year>\d\d)(?P<month>\d\d)',
                             tarball)
            if match.groupdict()['year'] and match.groupdict()['month']:
                self.__version = '{0}.{1}'.format(match.groupdict()['year'],
                                                  match.groupdict()['month'])
        else:
            # The URL would normally result in a downloaded file with
            # the name 'downloader.php?file=pgi-community-linux-x64'.
            # Also, the version downloaded cannot be controlled, it
            # will always be the 'latest'.  Use a synthetic tarball
            # filename.
            tarball = 'pgi-community-linux-x64-latest.tar.gz'

            self.__commands.append(self.download_step(
                url=self.__url, outfile=os.path.join(self.__wd, tarball),
                referer=self.__referer, directory=self.__wd))

        self.__commands.append(self.untar_step(
            tarball=os.path.join(self.__wd, tarball), directory=self.__wd))

        flags = {'PGI_ACCEPT_EULA': 'accept',
                 'PGI_INSTALL_NVIDIA': 'true',
                 'PGI_SILENT': 'true'}
        if not self.__eula:
            # This will fail when building the container
            logging.warning('PGI EULA was not accepted')
            flags['PGI_ACCEPT_EULA'] = 'decline'
            flags['PGI_SILENT'] = 'false'
        if self.__system_cuda:
            flags['PGI_INSTALL_NVIDIA'] = 'false'
        flag_string = ' '.join('{0}={1}'.format(key, val)
                               for key, val in sorted(flags.items()))

        self.__commands.append('cd {0} && {1} ./install'.format(self.__wd,
                                                                flag_string))

        # Create siterc to specify use of the system CUDA
        if self.__system_cuda:
            self.__commands.append('echo "set CUDAROOT=/usr/local/cuda;" >> {}'.format(os.path.join(self.__basepath, self.__version, 'bin', 'siterc')))

        self.__commands.append(self.cleanup_step(
            items=[os.path.join(self.__wd, tarball), self.__wd]))

    def runtime(self, _from='0'):
        """Install the runtime from a full build in a previous stage"""
        instructions = []
        instructions.append(comment('PGI compiler'))
        if self.__ospackages:
            instructions.append(packages(ospackages=self.__ospackages))
        instructions.append(copy(_from=_from,
                                 src=os.path.join(self.__basepath,
                                                  self.__version, 'REDIST',
                                                  '*.so'),
                                 dest=os.path.join(self.__basepath,
                                                   self.__version, 'lib', '')))
        instructions.append(shell(
            commands=['ln -s {0} {1}'.format(os.path.join(self.__basepath,
                                                          self.__version,
                                                          'lib',
                                                          'libpgnuma.so'),
                                             os.path.join(self.__basepath,
                                                          self.__version,
                                                          'lib',
                                                          'libnuma.so'))]))
        instructions.append(environment(
            variables={'LD_LIBRARY_PATH': '{}:$LD_LIBRARY_PATH'.format(
                os.path.join(self.__basepath, self.__version, 'lib'))}))
        return instructions
