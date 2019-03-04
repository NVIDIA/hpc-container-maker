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

"""packages building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import

import hpccm.config

from hpccm.building_blocks.apt_get import apt_get
from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.yum import yum
from hpccm.common import linux_distro

class packages(bb_base):
    """The `packages` building block specifies the set of operating system
    packages to install.  Based on the Linux distribution, the
    building block invokes either `apt-get` (Ubuntu) or `yum`
    (RHEL-based).

    This building block is preferred over directly using the
    [`apt_get`](#apt_get) or [`yum`](#yum) building blocks.

    # Parameters

    apt: A list of Debian packages to install.  The default is an
    empty list.

    apt_keys: A list of GPG keys to add.  The default is an empty
    list.

    apt_ppas: A list of personal package archives to add.  The default
    is an empty list.

    apt_repositories: A list of apt repositories to add.  The default
    is an empty list.

    epel: Boolean flag to specify whether to enable the Extra Packages
    for Enterprise Linux (EPEL) repository.  The default is False.
    This parameter is ignored if the Linux distribution is not
    RHEL-based.

    ospackages: A list of packages to install.  The list is used for
    both Ubuntu and RHEL-based Linux distributions, therefore only
    packages with the consistent names across Linux distributions
    should be specified.  This parameter is ignored if `apt` or `yum`
    is specified.  The default value is an empty list.

    scl: Boolean flag to specify whether to enable the Software
    Collections (SCL) repository.  The default is False.  This
    parameter is ignored if the Linux distribution is not RHEL-based.

    yum: A list of RPM packages to install.  The default value is an
    empty list.

    yum_keys: A list of GPG keys to import.  The default is an empty
    list.

    yum_repositories: A list of yum repositories to add.  The default
    is an empty list.

    # Examples

    ```python
    packages(ospackages=['make', 'wget'])
    ```

    ```python
    packages(apt=['zlib1g-dev'], yum=['zlib-devel'])
    ```

    ```python
    packages(apt=['python3'], yum=['python34'], epel=True)
    ```
    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(packages, self).__init__()

        self.__apt = kwargs.get('apt', [])
        self.__apt_keys = kwargs.get('apt_keys', [])
        self.__apt_ppas = kwargs.get('apt_ppas', [])
        self.__apt_repositories = kwargs.get('apt_repositories', [])
        self.__epel = kwargs.get('epel', False)
        self.__ospackages = kwargs.get('ospackages', [])
        self.__scl = kwargs.get('scl', False)
        self.__yum = kwargs.get('yum', [])
        self.__yum_keys = kwargs.get('yum_keys', [])
        self.__yum_repositories = kwargs.get('yum_repositories', [])

        # Fill in container instructions
        self.__instructions()

    def __instructions(self):
        """String representation of the building block"""
        if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
            if self.__apt:
                self += apt_get(keys=self.__apt_keys, ospackages=self.__apt,
                                ppas=self.__apt_ppas,
                                repositories=self.__apt_repositories)
            else:
                self += apt_get(keys=self.__apt_keys,
                                ospackages=self.__ospackages,
                                ppas=self.__apt_ppas,
                                repositories=self.__apt_repositories)
        elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
            if self.__yum:
                self += yum(epel=self.__epel, keys=self.__yum_keys,
                            ospackages=self.__yum, scl=self.__scl,
                            repositories=self.__yum_repositories)
            else:
                self += yum(epel=self.__epel, keys=self.__yum_keys,
                            ospackages=self.__ospackages, scl=self.__scl,
                            repositories=self.__yum_repositories)
        else:
            raise RuntimeError('Unknown Linux distribution')
