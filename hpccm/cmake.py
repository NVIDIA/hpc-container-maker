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

"""CMake building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import os
import re

from hpccm.comment import comment
from hpccm.packages import packages
from hpccm.shell import shell
from hpccm.wget import wget

class cmake(wget):
    """CMake building block"""

    def __init__(self, **kwargs):
        """Initialize building block"""

        # Trouble getting MRO with kwargs working correctly, so just call
        # the parent class constructors manually for now.
        #super(cmake, self).__init__(**kwargs)
        wget.__init__(self, **kwargs)

        self.__baseurl = kwargs.get('baseurl', 'https://cmake.org/files')

        # By setting this value to True, you agree to the CMake
        # End-User License Agreement
        # (https://gitlab.kitware.com/cmake/cmake/raw/master/Copyright.txt)
        self.__eula = kwargs.get('eula', False)

        self.__ospackages = kwargs.get('ospackages', ['wget'])
        self.__prefix = kwargs.get('prefix', '/usr/local')
        self.__version = kwargs.get('version', '3.11.1')

        self.__commands = [] # Filled in by __setup()
        self.__wd = '/tmp' # working directory

        # Construct the series of steps to execute
        self.__setup()

    def __str__(self):
        """String representation of the building block"""
        instructions = []
        instructions.append(comment(
            'CMake version {}'.format(self.__version)))
        instructions.append(packages(ospackages=self.__ospackages))
        instructions.append(shell(commands=self.__commands))

        return '\n'.join(str(x) for x in instructions)

    def cleanup_step(self, items=None):
        """Cleanup temporary files"""

        if not items: # pragma: no cover
            logging.warning('items are not defined')
            return ''

        return 'rm -rf {}'.format(' '.join(items))

    def __setup(self):
        """Construct the series of shell commands, i.e., fill in
           self.__commands"""

        # The download URL has the format contains vMAJOR.MINOR in the
        # path and the runfile contains MAJOR.MINOR.REVISION, so pull
        # apart the full version to get the MAJOR and MINOR
        # components.
        match = re.match(r'(?P<major>\d+)\.(?P<minor>\d+)', self.__version)
        major_minor = '{0}.{1}'.format(match.groupdict()['major'],
                                       match.groupdict()['minor'])
        runfile = 'cmake-{}-Linux-x86_64.sh'.format(self.__version)
        url = '{0}/v{1}/{2}'.format(self.__baseurl, major_minor, runfile)

        # Download source from web
        self.__commands.append(self.download_step(url=url,
                                                  directory=self.__wd))

        # Run the runfile
        if self.__eula:
            self.__commands.append(
                '/bin/sh {0} --prefix={1} --skip-license'.format(
                    os.path.join(self.__wd, runfile), self.__prefix))
        else:
            # This will fail when building the container
            logging.warning('CMake EULA was not accepted')
            self.__commands.append(
                '/bin/sh {0} --prefix={1}'.format(
                    os.path.join(self.__wd, runfile), self.__prefix))

        # Cleanup runfile
        self.__commands.append(self.cleanup_step(
            items=[os.path.join(self.__wd, runfile)]))

    def runtime(self, _from='0'):
        """Install the runtime from a full build in a previous stage.  In this
           case there is no difference between the runtime and the
           full build."""
        return self
