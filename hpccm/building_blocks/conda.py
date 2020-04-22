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

"""conda building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import logging
import posixpath

import hpccm.config
import hpccm.templates.rm
import hpccm.templates.wget

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.packages import packages
from hpccm.common import cpu_arch
from hpccm.primitives.comment import comment
from hpccm.primitives.copy import copy
from hpccm.primitives.shell import shell

class conda(bb_base, hpccm.templates.rm, hpccm.templates.wget):
    """The `conda` building block installs Anaconda.

    You must agree to the [Anaconda End User License Agreement](https://docs.anaconda.com/anaconda/eula/) to use this building block.

    # Parameters

    channels: List of additional Conda channels to enable.  The
    default is an empty list.

    environment: Path to the Conda environment file to clone.  The
    default value is empty.

    eula: By setting this value to `True`, you agree to the [Anaconda End User License Agreement](https://docs.anaconda.com/anaconda/eula/).
    The default value is `False`.

    ospackages: List of OS packages to install prior to installing
    Conda.  The default values are `ca-certificates` and `wget`.

    packages: List of Conda packages to install.  The default is an
    empty list.

    prefix: The top level install location.  The default value is
    `/usr/local/anaconda`.

    python2: Boolean flag to specify that the Python 2 version of
    Anaconda should be installed.  The default is False.

    version: The version of Anaconda to download.  The default value
    is `4.7.12`.

    # Examples

    ```python
    conda(packages=['numpy'])
    ```

    ```python
    conda(channels=['conda-forge', 'nvidia'], prefix='/opt/conda')
    ```

    ```python
    conda(environment='environment.yml')
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(conda, self).__init__(**kwargs)

        self.__arch_pkg = '' # Filled in by __cpu_arch()
        self.__baseurl = kwargs.get('baseurl',
                                    'http://repo.anaconda.com/miniconda')
        self.__channels = kwargs.get('channels', [])
        self.__environment = kwargs.get('environment', None)

        # By setting this value to True, you agree to the
        # corresponding Anaconda End User License Agreement
        # https://docs.anaconda.com/anaconda/eula/
        self.__eula = kwargs.get('eula', False)
        self.__ospackages = kwargs.get('ospackages',
                                       ['ca-certificates', 'wget'])
        self.__packages = kwargs.get('packages', [])
        self.__prefix = kwargs.get('prefix', '/usr/local/anaconda')
        self.__python2 = kwargs.get('python2', False)
        self.__python_version = '2' if self.__python2 else '3'
        self.__version = kwargs.get('version', '4.7.12')

        self.__commands = [] # Filled in by __setup()
        self.__wd = '/var/tmp' # working directory

        if not self.__eula:
            logging.warning('Anaconda EULA was not accepted.  To accept, see the documentation for this building block')

        # Set the CPU architecture specific parameters
        self.__cpu_arch()

        # Construct the series of steps to execute
        self.__setup()

        # Fill in container instructions
        self.__instructions()

    def __instructions(self):
        """Fill in container instructions"""

        self += comment('Anaconda')
        self += packages(ospackages=self.__ospackages)
        if self.__environment:
            self += copy(src=self.__environment, dest=posixpath.join(
                self.__wd, posixpath.basename(self.__environment)))
        self += shell(commands=self.__commands)

    def __cpu_arch(self):
        """Based on the CPU architecture, set values accordingly.  A user
        specified value overrides any defaults."""

        if hpccm.config.g_cpu_arch == cpu_arch.PPC64LE:
            self.__arch_pkg = 'ppc64le'
        elif hpccm.config.g_cpu_arch == cpu_arch.X86_64:
            self.__arch_pkg = 'x86_64'
        else: # pragma: no cover
            raise RuntimeError('Unknown CPU architecture')

    def __setup(self):
        """Construct the series of shell commands, i.e., fill in
           self.__commands"""

        miniconda = 'Miniconda{0}-{1}-Linux-{2}.sh'.format(
            self.__python_version, self.__version, self.__arch_pkg)
        url = '{0}/{1}'.format(self.__baseurl, miniconda)

        # Download source from web
        self.__commands.append(self.download_step(url=url, directory=self.__wd))

        # Install
        install_args = ['-p {}'.format(self.__prefix)]
        if self.__eula:
            install_args.append('-b')
        self.__commands.append('bash {0} {1}'.format(
            posixpath.join(self.__wd, miniconda),
            ' '.join(sorted(install_args))))

        # Initialize conda
        self.__commands.append('{0} init'.format(
            posixpath.join(self.__prefix, 'bin', 'conda')))
        self.__commands.append('ln -s {} /etc/profile.d/conda.sh'.format(
            posixpath.join(self.__prefix, 'etc', 'profile.d', 'conda.sh')))

        # Activate
        if self.__channels or self.__environment or self.__packages:
            self.__commands.append('. {}'.format(
                posixpath.join(self.__prefix, 'etc', 'profile.d', 'conda.sh')))
            self.__commands.append('conda activate base')

        # Enable channels
        if self.__channels:
            self.__commands.append('conda config {}'.format(
                ' '.join(['--add channels {}'.format(x)
                          for x in sorted(self.__channels)])))

        # Install environment
        if self.__environment:
            self.__commands.append('conda env update -f {}'.format(
                posixpath.join(self.__wd,
                               posixpath.basename(self.__environment))))
            self.__commands.append(self.cleanup_step(
                items=[posixpath.join(
                    self.__wd, posixpath.basename(self.__environment))]))

        # Install conda packages
        if self.__packages:
            self.__commands.append('conda install -y {}'.format(
                ' '.join(sorted(self.__packages))))

        # Cleanup conda install
        self.__commands.append('{0} clean -afy'.format(
            posixpath.join(self.__prefix, 'bin', 'conda')))

        # Cleanup miniconda download file
        self.__commands.append(self.cleanup_step(
            items=[posixpath.join(self.__wd, miniconda)]))

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples

        ```python
        c = conda(...)
        Stage0 += c
        Stage1 += c.runtime()
        ```
        """
        instructions = []
        instructions.append(comment('Anaconda'))
        instructions.append(copy(_from=_from, src=self.__prefix,
                                 dest=self.__prefix))
        instructions.append(shell(commands=[
            '{0} init'.format(
                posixpath.join(self.__prefix, 'bin', 'conda')),
            'ln -s {0} /etc/profile.d/conda.sh'.format(
                posixpath.join(self.__prefix, 'etc', 'profile.d',
                               'conda.sh'))]))
        return '\n'.join(str(x) for x in instructions)
