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

from helpers import docker, invalid_ctype, singularity

import hpccm.config

from hpccm.baseimage import baseimage
from hpccm.common import linux_distro

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
        self.assertEqual(str(b), 'BootStrap: docker\nFrom: foo')

    @docker
    def test_as_deprecated_docker(self):
        """Docker specified image naming"""
        b = baseimage(image='foo', AS='dev')
        self.assertEqual(str(b), 'FROM foo AS dev')

    @singularity
    def test_as_deprecated_singularity(self):
        """Docker specified image naming"""
        b = baseimage(image='foo', AS='dev')
        self.assertEqual(str(b), 'BootStrap: docker\nFrom: foo')

    @docker
    def test_as_docker(self):
        """Docker specified image naming"""
        b = baseimage(image='foo', _as='dev')
        self.assertEqual(str(b), 'FROM foo AS dev')

    @singularity
    def test_as_singularity(self):
        """Docker specified image naming"""
        b = baseimage(image='foo', _as='dev')
        self.assertEqual(str(b), 'BootStrap: docker\nFrom: foo')

    @docker
    def test_detect_ubuntu(self):
        """Base image Linux distribution detection"""
        b = baseimage(image='nvidia/cuda:9.0-devel-ubuntu16.04')
        self.assertEqual(hpccm.config.g_linux_distro, linux_distro.UBUNTU)

    @docker
    def test_detect_centos(self):
        """Base image Linux distribution detection"""
        b = baseimage(image='nvidia/cuda:9.0-devel-centos7')
        self.assertEqual(hpccm.config.g_linux_distro, linux_distro.CENTOS)

    @docker
    def test_detect_nonexistent(self):
        """Base image Linux distribution detection"""
        b = baseimage(image='nonexistent')
        self.assertEqual(hpccm.config.g_linux_distro, linux_distro.UBUNTU)

    @docker
    def test_distro_ubuntu(self):
        """Base image Linux distribution specification"""
        b = baseimage(image='foo', _distro='ubuntu')
        self.assertEqual(hpccm.config.g_linux_distro, linux_distro.UBUNTU)

    @docker
    def test_distro_centos(self):
        """Base image Linux distribution specification"""
        b = baseimage(image='foo', _distro='centos')
        self.assertEqual(hpccm.config.g_linux_distro, linux_distro.CENTOS)

    @docker
    def test_distro_nonexistent(self):
        """Base image Linux distribution specification"""
        b = baseimage(image='foo', _distro='nonexistent')
        self.assertEqual(hpccm.config.g_linux_distro, linux_distro.UBUNTU)
