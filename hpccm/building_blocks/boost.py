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

"""Boost building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import re
import os

from hpccm.building_blocks.packages import packages
from hpccm.primitives.comment import comment
from hpccm.primitives.copy import copy
from hpccm.primitives.environment import environment
from hpccm.primitives.shell import shell
from hpccm.templates.rm import rm
from hpccm.templates.tar import tar
from hpccm.templates.wget import wget

class boost(rm, tar, wget):
    """Boost building block"""

    def __init__(self, **kwargs):
        """Initialize building block"""

        # Trouble getting MRO with kwargs working correctly, so just call
        # the parent class constructors manually for now.
        #super(boost, self).__init__(**kwargs)
        rm.__init__(self, **kwargs)
        tar.__init__(self, **kwargs)
        wget.__init__(self, **kwargs)

        self.__baseurl = kwargs.get('baseurl',
                                    'https://dl.bintray.com/boostorg/release')
        self.__bootstrap_opts = kwargs.get('bootstrap_opts', [])
        self.__ospackages = kwargs.get('ospackages', ['bzip2', 'tar', 'wget'])
        self.__parallel = kwargs.get('parallel', 4)
        self.__prefix = kwargs.get('prefix', '/usr/local/boost')
        self.__version = kwargs.get('version', '1.67.0')

        self.__commands = [] # Filled in by __setup()
        self.__environment_variables = {
            'LD_LIBRARY_PATH':
            '{}:$LD_LIBRARY_PATH'.format(os.path.join(self.__prefix, 'lib'))}
        self.__wd = '/var/tmp' # working directory

        # Construct the series of steps to execute
        self.__setup()

    def __str__(self):
        """String representation of the building block"""

        instructions = []
        instructions.append(comment(
            'Boost version {}'.format(self.__version)))
        instructions.append(packages(ospackages=self.__ospackages))
        instructions.append(shell(commands=self.__commands))
        instructions.append(environment(
            variables=self.__environment_variables))
        return '\n'.join(str(x) for x in instructions)

    def __setup(self):
        """Construct the series of shell commands, i.e., fill in
           self.__commands"""

        # The download URL has the version format with underscores so
        # pull apart the full version to get the individual
        # components.
        match = re.match(r'(?P<major>\d+)\.(?P<minor>\d+)\.(?P<revision>\d+)',
                         self.__version)
        v_underscore = '{0}_{1}_{2}'.format(match.groupdict()['major'],
                                            match.groupdict()['minor'],
                                            match.groupdict()['revision'])

        tarball = 'boost_{}.tar.bz2'.format(v_underscore)
        url = '{0}/{1}/source/{2}'.format(self.__baseurl, self.__version,
                                          tarball)

        # Download source from web
        self.__commands.append(self.download_step(url=url,
                                                  directory=self.__wd))
        self.__commands.append(self.untar_step(
            tarball=os.path.join(self.__wd, tarball), directory=self.__wd))

        # Configure
        self.__commands.append(
            'cd {} && ./bootstrap.sh --prefix={} {}'.format(
                os.path.join(self.__wd, 'boost_{}'.format(v_underscore)),
                self.__prefix,
                ' '.join(self.__bootstrap_opts)))

        # Build and install
        self.__commands.append('./b2 -j{} install'.format(self.__parallel))

        # Cleanup tarball and directory
        self.__commands.append(self.cleanup_step(
            items=[os.path.join(self.__wd, tarball),
                   os.path.join(self.__wd,
                                'boost_{}'.format(v_underscore))]))

    def runtime(self, _from='0'):
        """Install the runtime from a full build in a previous stage"""
        instructions = []
        instructions.append(comment('Boost'))
        instructions.append(copy(_from=_from, src=self.__prefix,
                                 dest=self.__prefix))
        instructions.append(environment(
            variables=self.__environment_variables))
        return '\n'.join(str(x) for x in instructions)
