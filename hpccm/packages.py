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
        self.__epel = kwargs.get('epel', False)
        self.__ospackages = kwargs.get('ospackages', [])
        self.__yum = kwargs.get('yum', [])

    def __str__(self):
        """String representation of the building block"""
        if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
            if self.__apt:
                return str(apt_get(ospackages=self.__apt))
            else:
                return str(apt_get(ospackages=self.__ospackages))
        elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
            if self.__yum:
                return str(yum(epel=self.__epel, ospackages=self.__yum))
            else:
                return str(yum(epel=self.__epel, ospackages=self.__ospackages))
        else:
            raise RuntimeError('Unknown Linux distribution')
