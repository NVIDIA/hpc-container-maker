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

from helpers import bash, docker, singularity

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

        hpccm.config.set_linux_distro('centos8')
        self.assertEqual(hpccm.config.g_linux_distro,
                         hpccm.linux_distro.CENTOS)
        self.assertEqual(hpccm.config.g_linux_version, StrictVersion('8.0'))

    @docker
    def test_set_linux_distro_rhel(self):
        """Set Linux distribution to RHEL"""
        hpccm.config.set_linux_distro('rhel')
        self.assertEqual(hpccm.config.g_linux_distro,
                         hpccm.linux_distro.RHEL)
        self.assertEqual(hpccm.config.g_linux_version, StrictVersion('7.0'))

        hpccm.config.set_linux_distro('rhel7')
        self.assertEqual(hpccm.config.g_linux_distro,
                         hpccm.linux_distro.RHEL)
        self.assertEqual(hpccm.config.g_linux_version, StrictVersion('7.0'))

        hpccm.config.set_linux_distro('rhel8')
        self.assertEqual(hpccm.config.g_linux_distro,
                         hpccm.linux_distro.RHEL)
        self.assertEqual(hpccm.config.g_linux_version, StrictVersion('8.0'))

    @docker
    def test_set_linux_distro_invalid(self):
        """Set Linux distribution to an invalid value"""
        hpccm.config.set_linux_distro('invalid')
        self.assertEqual(hpccm.config.g_linux_distro,
                         hpccm.linux_distro.UBUNTU)
        self.assertEqual(hpccm.config.g_linux_version, StrictVersion('16.04'))

    @singularity
    def test_set_singularity_version(self):
        """Set Singularity version"""
        hpccm.config.set_singularity_version('10.0')
        self.assertEqual(hpccm.config.g_singularity_version,
                         StrictVersion('10.0'))

    @docker
    def test_set_cpu_architecture_aarch64(self):
        """Set CPU architecture to ARM"""
        hpccm.config.set_cpu_architecture('aarch64')
        self.assertEqual(hpccm.config.g_cpu_arch, hpccm.cpu_arch.AARCH64)
        self.assertEqual(hpccm.config.get_cpu_architecture(), 'aarch64')

    @docker
    def test_set_cpu_architecture_arm(self):
        """Set CPU architecture to ARM"""
        hpccm.config.set_cpu_architecture('arm')
        self.assertEqual(hpccm.config.g_cpu_arch, hpccm.cpu_arch.AARCH64)

    @docker
    def test_set_cpu_architecture_arm64v8(self):
        """Set CPU architecture to ARM"""
        hpccm.config.set_cpu_architecture('arm64v8')
        self.assertEqual(hpccm.config.g_cpu_arch, hpccm.cpu_arch.AARCH64)

    @docker
    def test_set_cpu_architecture_ppc64le(self):
        """Set CPU architecture to POWER"""
        hpccm.config.set_cpu_architecture('ppc64le')
        self.assertEqual(hpccm.config.g_cpu_arch, hpccm.cpu_arch.PPC64LE)
        self.assertEqual(hpccm.config.get_cpu_architecture(), 'ppc64le')

    @docker
    def test_set_cpu_architecture_power(self):
        """Set CPU architecture to POWER"""
        hpccm.config.set_cpu_architecture('power')
        self.assertEqual(hpccm.config.g_cpu_arch, hpccm.cpu_arch.PPC64LE)

    @docker
    def test_set_cpu_architecture_x86_64(self):
        """Set CPU architecture to x86_64"""
        hpccm.config.set_cpu_architecture('x86_64')
        self.assertEqual(hpccm.config.g_cpu_arch, hpccm.cpu_arch.X86_64)
        self.assertEqual(hpccm.config.get_cpu_architecture(), 'x86_64')

    @docker
    def test_set_cpu_architecture_amd64(self):
        """Set CPU architecture to x86_64"""
        hpccm.config.set_cpu_architecture('amd64')
        self.assertEqual(hpccm.config.g_cpu_arch, hpccm.cpu_arch.X86_64)

    @docker
    def test_set_cpu_architecture_x86(self):
        """Set CPU architecture to x86_64"""
        hpccm.config.set_cpu_architecture('x86')
        self.assertEqual(hpccm.config.g_cpu_arch, hpccm.cpu_arch.X86_64)

    @docker
    def test_set_cpu_architecture_invalid(self):
        """Set CPU architecture to invalid value"""
        hpccm.config.set_cpu_architecture('invalid')
        self.assertEqual(hpccm.config.g_cpu_arch, hpccm.cpu_arch.X86_64)

    @bash
    def test_get_format_bash(self):
        """Get container format"""
        self.assertEqual(hpccm.config.get_format(), 'bash')

    @docker
    def test_get_format_docker(self):
        """Get container format"""
        self.assertEqual(hpccm.config.get_format(), 'docker')

    @singularity
    def test_get_format_singularity(self):
        """Get container format"""
        self.assertEqual(hpccm.config.get_format(), 'singularity')
