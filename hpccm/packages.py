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

from hpccm.apt_get import apt_get
from hpccm.common import linux_distro
from hpccm.yum import yum

class packages(object):
    """packages building block"""

    def __init__(self, **kwargs):
        """Initialize building block"""

        #super(packages, self).__init__()

        self.__apt = kwargs.get('apt', [])
        self.__apt_keys = kwargs.get('apt_keys', [])
        self.__apt_repositories = kwargs.get('apt_repositories', [])
        self.__epel = kwargs.get('epel', False)
        self.__ospackages = kwargs.get('ospackages', [])
        self.__yum = kwargs.get('yum', [])
        self.__yum_keys = kwargs.get('yum_keys', [])
        self.__yum_repositories = kwargs.get('yum_repositories', [])

    def __str__(self):
        """String representation of the building block"""
        if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
            if self.__apt:
                return str(apt_get(keys=self.__apt_keys, ospackages=self.__apt,
                                   repositories=self.__apt_repositories))
            else:
                return str(apt_get(keys=self.__apt_keys,
                                   ospackages=self.__ospackages,
                                   repositories=self.__apt_repositories))
        elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
            if self.__yum:
                return str(yum(epel=self.__epel, keys=self.__yum_keys,
                               ospackages=self.__yum,
                               repositories=self.__yum_repositories))
            else:
                return str(yum(epel=self.__epel, keys=self.__yum_keys,
                               ospackages=self.__ospackages,
                               repositories=self.__yum_repositories))
        else:
            raise RuntimeError('Unknown Linux distribution')
