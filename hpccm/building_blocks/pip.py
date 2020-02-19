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

"""pip building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from distutils.version import StrictVersion
import posixpath

import hpccm.config
import hpccm.templates.rm

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.packages import packages
from hpccm.common import linux_distro
from hpccm.primitives.comment import comment
from hpccm.primitives.copy import copy
from hpccm.primitives.shell import shell

class pip(bb_base, hpccm.templates.rm):
    """The `pip` building block installs Python packages from PyPi.

    # Parameters

    alternatives: Boolean flag to specify whether to configure alternatives for `python` and `pip`.  RHEL-based 8.x distributions do not setup `python` by [default](https://developers.redhat.com/blog/2019/05/07/what-no-python-in-red-hat-enterprise-linux-8/).  The default is False.

    ospackages: List of OS packages to install prior to installing
    PyPi packages.  For Ubuntu, the default values are `python-pip`,
    `python-setuptools`, and `python-wheel` for Python 2.x and
    `python3-pip`, `python3-setuptools`, and `python3-wheel` for
    Python 3.x.  For RHEL-based distributions, the default
    values are `python2-pip` for Python 2.x and `python3-pip` for
    Python 3.x.

    packages: List of PyPi packages to install.  The default is
    an empty list.

    pip: The name of the `pip` tool to use. The default is `pip`.

    requirements: Path to pip requirements file.  The default is
    empty.

    upgrade: Boolean flag to control whether pip itself should be
    upgraded prior to installing any PyPi packages.  The default is
    False.

    # Examples

    ```python
    pip(packages=['hpccm'])
    ```

    ```python
    pip(packages=['hpccm'], pip='pip3')
    ```

    ```python
    pip(requirements='requirements.txt')
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(pip, self).__init__(**kwargs)

        self.__alternatives = kwargs.get('alternatives', False)
        self.__epel = False
        self.__ospackages = kwargs.get('ospackages', None)
        self.__packages = kwargs.get('packages', [])
        self.__pip = kwargs.get('pip', 'pip')
        self.__requirements = kwargs.get('requirements', None)
        self.__upgrade = kwargs.get('upgrade', False)
        self.__wd = '/var/tmp' # working directory

        self.__debs = [] # Filled in below
        self.__rpms = [] # Filled in below

        if self.__ospackages is None:
            if self.__pip.startswith('pip3'):
                self.__debs.extend(['python3-pip', 'python3-setuptools',
                                    'python3-wheel'])
                self.__rpms.append('python3-pip')
            else:
                self.__debs.extend(['python-pip', 'python-setuptools',
                                    'python-wheel'])
                self.__rpms.append('python2-pip')
                if (hpccm.config.g_linux_distro == linux_distro.CENTOS and
                    hpccm.config.g_linux_version < StrictVersion('8.0')):
                    # python2-pip is an EPEL package in CentOS 7.x
                    self.__epel = True
        elif self.__ospackages:
            self.__debs = self.__ospackages
            self.__rpms = self.__ospackages

        # Fill in container instructions
        self.__instructions()

    def __instructions(self):
        """Fill in container instructions"""

        self += comment('pip')
        if self.__debs or self.__rpms:
            self += packages(apt=self.__debs, epel=self.__epel,
                             yum=self.__rpms)

        if self.__alternatives:
            self += shell(commands=[
                'alternatives --set python /usr/bin/python2',
                'alternatives --install /usr/bin/pip pip /usr/bin/pip2 30'])

        if self.__pip:
            cmds = []

            if self.__upgrade:
                cmds.append('{0} install --upgrade pip'.format(self.__pip))

            if self.__requirements:
                self += copy(src=self.__requirements,
                             dest=posixpath.join(
                                 self.__wd,
                                 posixpath.basename(self.__requirements)))
                cmds.append('{0} install -r {1}'.format(
                    self.__pip,
                    posixpath.join(self.__wd,
                                   posixpath.basename(self.__requirements))))
                cmds.append(self.cleanup_step(items=[
                    posixpath.join(self.__wd,
                                   posixpath.basename(self.__requirements))]))

            if self.__packages:
                cmds.append('{0} install {1}'.format(self.__pip,
                                                     ' '.join(self.__packages)))
            self += shell(commands=cmds)
