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

"""Test cases for the config module"""

from __future__ import unicode_literals
from __future__ import print_function

from distutils.version import StrictVersion
import logging # pylint: disable=unused-import
import unittest

from helpers import docker, singularity

import hpccm.config

class Test_config(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @singularity
    def test_set_container_format_docker(self):
        """Set container format to Docker"""
        hpccm.config.set_container_format('docker')
        self.assertEqual(hpccm.config.g_ctype, hpccm.container_type.DOCKER)

    @docker
    def test_set_container_format_singularity(self):
        """Set container format to Singularity"""
        hpccm.config.set_container_format('singularity')
        self.assertEqual(hpccm.config.g_ctype, hpccm.container_type.SINGULARITY)

    @docker
    def test_set_container_format_invalid(self):
        """Set container format to invalid value"""
        with self.assertRaises(RuntimeError):
            hpccm.config.set_container_format('invalid')

    @docker
    def test_set_linux_distro_ubuntu(self):
        """Set Linux distribution to Ubuntu"""
        hpccm.config.set_linux_distro('ubuntu')
        self.assertEqual(hpccm.config.g_linux_distro,
                         hpccm.linux_distro.UBUNTU)
        self.assertEqual(hpccm.config.g_linux_version, StrictVersion('16.04'))

        hpccm.config.set_linux_distro('ubuntu16')
        self.assertEqual(hpccm.config.g_linux_distro,
                         hpccm.linux_distro.UBUNTU)
        self.assertEqual(hpccm.config.g_linux_version, StrictVersion('16.04'))

        hpccm.config.set_linux_distro('ubuntu18')
        self.assertEqual(hpccm.config.g_linux_distro,
                         hpccm.linux_distro.UBUNTU)
        self.assertEqual(hpccm.config.g_linux_version, StrictVersion('18.04'))

    @docker
    def test_set_linux_distro_centos(self):
        """Set Linux distribution to CentOS"""
        hpccm.config.set_linux_distro('centos')
        self.assertEqual(hpccm.config.g_linux_distro,
                         hpccm.linux_distro.CENTOS)
        self.assertEqual(hpccm.config.g_linux_version, StrictVersion('7.0'))

        hpccm.config.set_linux_distro('centos7')
        self.assertEqual(hpccm.config.g_linux_distro,
                         hpccm.linux_distro.CENTOS)
        self.assertEqual(hpccm.config.g_linux_version, StrictVersion('7.0'))

    @docker
    def test_set_linux_distro_invalid(self):
        """Set Linux distribution to an invalid value"""
        hpccm.config.set_linux_distro('invalid')
        self.assertEqual(hpccm.config.g_linux_distro,
                         hpccm.linux_distro.UBUNTU)
        self.assertEqual(hpccm.config.g_linux_version, StrictVersion('16.04'))
