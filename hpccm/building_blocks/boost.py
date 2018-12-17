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

import hpccm.config

from hpccm.building_blocks.packages import packages
from hpccm.common import linux_distro
from hpccm.primitives.comment import comment
from hpccm.primitives.copy import copy
from hpccm.primitives.environment import environment
from hpccm.primitives.shell import shell
from hpccm.templates.rm import rm
from hpccm.templates.tar import tar
from hpccm.templates.wget import wget

class boost(rm, tar, wget):
    """The `boost` building block downloads and installs the
    [Boost](https://www.boost.org) component.

    As a side effect, this building block modifies `LD_LIBRARY_PATH`
    to include the Boost build.

    # Parameters

    bootstrap_opts: List of options to pass to `bootstrap.sh`.  The
    default is an empty list.

    ospackages: List of OS packages to install prior to building.  For
    Ubuntu, the default values are `bzip2`, `libbz2-dev`, `tar`,
    `wget`, and `zlib1g-dev`.  For RHEL-based Linux distributions the
    default values are `bzip2`, `bzip2-devel`, `tar`, `wget`, `which`,
    and `zlib-devel`.

    prefix: The top level installation location.  The default value
    is `/usr/local/boost`.

    python: Boolean flag to specify whether Boost should be built with
    Python support.  If enabled, the Python C headers need to be
    installed (typically this can be done by adding `python-dev` or
    `python-devel` to the list of OS packages).  The default is False.

    sourceforge: Boolean flag to specify whether Boost should be
    downloaded from SourceForge rather than the current Boost
    repository.  For versions of Boost older than 1.63.0, the
    SourceForge repository should be used.  The default is False.

    version: The version of Boost source to download.  The default
    value is `1.68.0`.

    # Examples

    ```python
    boost(prefix='/opt/boost/1.67.0', version='1.67.0')
    ```

    ```python
    boost(sourceforge=True, version='1.57.0')
    ```
    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        # Trouble getting MRO with kwargs working correctly, so just call
        # the parent class constructors manually for now.
        #super(boost, self).__init__(**kwargs)
        rm.__init__(self, **kwargs)
        tar.__init__(self, **kwargs)
        wget.__init__(self, **kwargs)

        self.__baseurl = kwargs.get('baseurl',
                                    'https://dl.bintray.com/boostorg/release/__version__/source')
        self.__bootstrap_opts = kwargs.get('bootstrap_opts', [])
        self.__ospackages = kwargs.get('ospackages', [])
        self.__parallel = kwargs.get('parallel', '$(nproc)')
        self.__prefix = kwargs.get('prefix', '/usr/local/boost')
        self.__python = kwargs.get('python', False)
        self.__sourceforge = kwargs.get('sourceforge', False)
        self.__version = kwargs.get('version', '1.68.0')

        self.__commands = [] # Filled in by __setup()
        self.__environment_variables = {
            'LD_LIBRARY_PATH':
            '{}:$LD_LIBRARY_PATH'.format(os.path.join(self.__prefix, 'lib'))}
        self.__wd = '/var/tmp' # working directory

        if self.__sourceforge:
            self.__baseurl = 'https://sourceforge.net/projects/boost/files/boost/__version__'

        # Set the Linux distribution specific parameters
        self.__distro()

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

    def __distro(self):
        """Based on the Linux distribution, set values accordingly.  A user
        specified value overrides any defaults."""

        if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
            if not self.__ospackages:
                self.__ospackages = ['bzip2', 'libbz2-dev', 'tar', 'wget',
                                     'zlib1g-dev']
        elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
            if not self.__ospackages:
                self.__ospackages = ['bzip2', 'bzip2-devel', 'tar', 'wget',
                                     'which', 'zlib-devel']
        else: # pragma: no cover
            raise RuntimeError('Unknown Linux distribution')

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
        url = '{0}/{1}'.format(self.__baseurl, tarball)
        url = url.replace('__version__', self.__version)

        # Python support requires pyconfig.h which is not part of the
        # standard Python install.  It requires the development
        # package, python-dev or python-devel.  So skip Python unless
        # it's specifically enabled.
        if not self.__python:
            self.__bootstrap_opts.append('--without-libraries=python')

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
        self.__commands.append('./b2 -j{} -q install'.format(self.__parallel))

        # Cleanup tarball and directory
        self.__commands.append(self.cleanup_step(
            items=[os.path.join(self.__wd, tarball),
                   os.path.join(self.__wd,
                                'boost_{}'.format(v_underscore))]))

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples

        ```python
        b = boost(...)
        Stage0 += b
        Stage1 += b.runtime()
        ```
        """
        instructions = []
        instructions.append(comment('Boost'))
        instructions.append(copy(_from=_from, src=self.__prefix,
                                 dest=self.__prefix))
        instructions.append(environment(
            variables=self.__environment_variables))
        return '\n'.join(str(x) for x in instructions)
