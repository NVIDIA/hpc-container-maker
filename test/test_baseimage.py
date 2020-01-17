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

"""Test cases for the baseimage module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import bash, docker, invalid_ctype, singularity, singularity26, singularity32

from distutils.version import StrictVersion
import hpccm.config

from hpccm.primitives.baseimage import baseimage
from hpccm.common import cpu_arch, linux_distro

class Test_baseimage(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @docker
    def test_empty_docker(self):
        """Default base image"""
        b = baseimage()
        self.assertNotEqual(str(b), '')

    @singularity
    def test_empty_singularity(self):
        """Default base image"""
        b = baseimage()
        self.assertNotEqual(str(b), '')

    @invalid_ctype
    def test_invalid_ctype(self):
        """Invalid container type specified"""
        b = baseimage()
        with self.assertRaises(RuntimeError):
            str(b)

    @docker
    def test_value_docker(self):
        """Image name is specified"""
        b = baseimage(image='foo')
        self.assertEqual(str(b), 'FROM foo')

    @singularity
    def test_value_singularity(self):
        """Image name is specified"""
        b = baseimage(image='foo')
        self.assertEqual(str(b),
r'''BootStrap: docker
From: foo
%post
    . /.singularity.d/env/10-docker*.sh''')

    @bash
    def test_value_bash(self):
        """Image name is specified"""
        b = baseimage(image='foo')
        self.assertEqual(str(b), '#!/bin/bash -ex')

    @singularity
    def test_false_docker_env_singularity(self):
        """Docker env is False"""
        b = baseimage(image='foo', _docker_env=False)
        self.assertEqual(str(b),
r'''BootStrap: docker
From: foo''')

    @docker
    def test_as_deprecated_docker(self):
        """Docker specified image naming"""
        b = baseimage(image='foo', AS='dev')
        self.assertEqual(str(b), 'FROM foo AS dev')

    @singularity26
    def test_as_deprecated_singularity(self):
        """Docker specified image naming"""
        b = baseimage(image='foo', AS='dev')
        self.assertEqual(str(b),
r'''BootStrap: docker
From: foo
%post
    . /.singularity.d/env/10-docker*.sh''')

    @docker
    def test_as_docker(self):
        """Docker specified image naming"""
        b = baseimage(image='foo', _as='dev')
        self.assertEqual(str(b), 'FROM foo AS dev')

    @singularity26
    def test_as_singularity26(self):
        """Docker specified image naming"""
        b = baseimage(image='foo', _as='dev')
        self.assertEqual(str(b),
r'''BootStrap: docker
From: foo
%post
    . /.singularity.d/env/10-docker*.sh''')

    @singularity32
    def test_as_singularity32(self):
        """Docker specified image naming"""
        b = baseimage(image='foo', _as='dev')
        self.assertEqual(str(b),
r'''# NOTE: this definition file depends on features only available in
# Singularity 3.2 and later.
BootStrap: docker
From: foo
Stage: dev
%post
    . /.singularity.d/env/10-docker*.sh''')

    @singularity
    def test_bootstrap(self):
      """Singularity bootstrap option"""
      b = baseimage(image='foo.sif', _bootstrap='localimage')
      self.assertEqual(str(b),
r'''BootStrap: localimage
From: foo.sif
%post
    . /.singularity.d/env/10-docker*.sh''')

    @docker
    def test_detect_ubuntu(self):
        """Base image Linux distribution detection"""
        b = baseimage(image='ubuntu:sixteen')
        self.assertEqual(hpccm.config.g_linux_distro, linux_distro.UBUNTU)
        self.assertEqual(hpccm.config.g_linux_version, StrictVersion('16.04'))

    @docker
    def test_detect_ubuntu16(self):
        """Base image Linux distribution detection"""
        b = baseimage(image='nvidia/cuda:9.0-devel-ubuntu16.04')
        self.assertEqual(hpccm.config.g_linux_distro, linux_distro.UBUNTU)
        self.assertEqual(hpccm.config.g_linux_version, StrictVersion('16.04'))

    @docker
    def test_detect_ubuntu18(self):
        """Base image Linux distribution detection"""
        b = baseimage(image='nvidia/cuda:9.2-devel-ubuntu18.04')
        self.assertEqual(hpccm.config.g_linux_distro, linux_distro.UBUNTU)
        self.assertEqual(hpccm.config.g_linux_version, StrictVersion('18.04'))

    @docker
    def test_detect_ubuntu_16(self):
        """Base image Linux distribution detection"""
        b = baseimage(image='ubuntu:16.04')
        self.assertEqual(hpccm.config.g_linux_distro, linux_distro.UBUNTU)
        self.assertEqual(hpccm.config.g_linux_version, StrictVersion('16.04'))

    @docker
    def test_detect_ubuntu_18(self):
        """Base image Linux distribution detection"""
        b = baseimage(image='ubuntu:18.04')
        self.assertEqual(hpccm.config.g_linux_distro, linux_distro.UBUNTU)
        self.assertEqual(hpccm.config.g_linux_version, StrictVersion('18.04'))

    @docker
    def test_detect_centos(self):
        """Base image Linux distribution detection"""
        b = baseimage(image='nvidia/cuda:9.0-devel-centos7')
        self.assertEqual(hpccm.config.g_linux_distro, linux_distro.CENTOS)
        self.assertEqual(hpccm.config.g_linux_version, StrictVersion('7.0'))

    @docker
    def test_detect_centos_7(self):
        """Base image Linux distribution detection"""
        b = baseimage(image='centos:7')
        self.assertEqual(hpccm.config.g_linux_distro, linux_distro.CENTOS)
        self.assertEqual(hpccm.config.g_linux_version, StrictVersion('7.0'))

    @docker
    def test_detect_centos_8(self):
        """Base image Linux distribution detection"""
        b = baseimage(image='centos:8')
        self.assertEqual(hpccm.config.g_linux_distro, linux_distro.CENTOS)
        self.assertEqual(hpccm.config.g_linux_version, StrictVersion('8.0'))

    @docker
    def test_detect_ubi7(self):
        """Base image Linux distribution detection"""
        b = baseimage(image='nvidia/cuda:10.1-devel-ubi7')
        self.assertEqual(hpccm.config.g_linux_distro, linux_distro.RHEL)
        self.assertEqual(hpccm.config.g_linux_version, StrictVersion('7.0'))

    @docker
    def test_detect_ubi8(self):
        """Base image Linux distribution detection"""
        b = baseimage(image='nvidia/cuda:10.1-devel-ubi8')
        self.assertEqual(hpccm.config.g_linux_distro, linux_distro.RHEL)
        self.assertEqual(hpccm.config.g_linux_version, StrictVersion('8.0'))

    @docker
    def test_detect_nonexistent(self):
        """Base image Linux distribution detection"""
        b = baseimage(image='nonexistent')
        self.assertEqual(hpccm.config.g_linux_distro, linux_distro.UBUNTU)
        self.assertEqual(hpccm.config.g_linux_version, StrictVersion('16.04'))

    @docker
    def test_distro_ubuntu(self):
        """Base image Linux distribution specification"""
        b = baseimage(image='foo', _distro='ubuntu')
        self.assertEqual(hpccm.config.g_linux_distro, linux_distro.UBUNTU)
        self.assertEqual(hpccm.config.g_linux_version, StrictVersion('16.04'))

    @docker
    def test_distro_ubuntu16(self):
        """Base image Linux distribution specification"""
        b = baseimage(image='foo', _distro='ubuntu16')
        self.assertEqual(hpccm.config.g_linux_distro, linux_distro.UBUNTU)
        self.assertEqual(hpccm.config.g_linux_version, StrictVersion('16.04'))

    @docker
    def test_distro_ubuntu18(self):
        """Base image Linux distribution specification"""
        b = baseimage(image='foo', _distro='ubuntu18')
        self.assertEqual(hpccm.config.g_linux_distro, linux_distro.UBUNTU)
        self.assertEqual(hpccm.config.g_linux_version, StrictVersion('18.04'))

    @docker
    def test_distro_centos(self):
        """Base image Linux distribution specification"""
        b = baseimage(image='foo', _distro='centos')
        self.assertEqual(hpccm.config.g_linux_distro, linux_distro.CENTOS)
        self.assertEqual(hpccm.config.g_linux_version, StrictVersion('7.0'))

    @docker
    def test_distro_centos7(self):
        """Base image Linux distribution specification"""
        b = baseimage(image='foo', _distro='centos7')
        self.assertEqual(hpccm.config.g_linux_distro, linux_distro.CENTOS)
        self.assertEqual(hpccm.config.g_linux_version, StrictVersion('7.0'))

    @docker
    def test_distro_centos8(self):
        """Base image Linux distribution specification"""
        b = baseimage(image='foo', _distro='centos8')
        self.assertEqual(hpccm.config.g_linux_distro, linux_distro.CENTOS)
        self.assertEqual(hpccm.config.g_linux_version, StrictVersion('8.0'))

    @docker
    def test_distro_nonexistent(self):
        """Base image Linux distribution specification"""
        b = baseimage(image='foo', _distro='nonexistent')
        self.assertEqual(hpccm.config.g_linux_distro, linux_distro.UBUNTU)
        self.assertEqual(hpccm.config.g_linux_version, StrictVersion('16.04'))

    @docker
    def test_detect_aarch64(self):
        """Base image CPU architecture detection"""
        b = baseimage(image='arm64v8/centos:7')
        self.assertEqual(hpccm.config.g_cpu_arch, cpu_arch.AARCH64)

    @docker
    def test_detect_ppc64le(self):
        """Base image CPU architecture detection"""
        b = baseimage(image='ppc64le/centos:7')
        self.assertEqual(hpccm.config.g_cpu_arch, cpu_arch.PPC64LE)

    @docker
    def test_detect_nonexistent(self):
        """Base image CPU architecture detection"""
        b = baseimage(image='foo')
        self.assertEqual(hpccm.config.g_cpu_arch, cpu_arch.X86_64)

    @docker
    def test_arch_aarch64(self):
        """Base image CPU architecture specification"""
        b = baseimage(image='foo', _arch='aarch64')
        self.assertEqual(hpccm.config.g_cpu_arch, cpu_arch.AARCH64)

    @docker
    def test_arch_ppc64le(self):
        """Base image CPU architecture specification"""
        b = baseimage(image='foo', _arch='ppc64le')
        self.assertEqual(hpccm.config.g_cpu_arch, cpu_arch.PPC64LE)

    @docker
    def test_arch_x86_64(self):
        """Base image CPU architecture specification"""
        b = baseimage(image='foo', _arch='x86_64')
        self.assertEqual(hpccm.config.g_cpu_arch, cpu_arch.X86_64)

    @docker
    def test_arch_nonexistent(self):
        """Base image CPU architecture specification"""
        b = baseimage(image='foo', _arch='nonexistent')
        self.assertEqual(hpccm.config.g_cpu_arch, cpu_arch.X86_64)
