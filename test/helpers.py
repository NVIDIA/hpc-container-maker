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

"""Unit testing helpers"""

from __future__ import unicode_literals
from __future__ import print_function

from distutils.version import StrictVersion
import logging # pylint: disable=unused-import

import hpccm.config

from hpccm.common import container_type, cpu_arch, linux_distro

def aarch64(function):
    """Decorator to set the CPU architecture to aarch64"""
    def wrapper(*args, **kwargs):
        hpccm.config.g_cpu_arch = cpu_arch.AARCH64
        return function(*args, **kwargs)

    return wrapper

def bash(function):
    """Decorator to set the global container type to bash"""
    def wrapper(*args, **kwargs):
        hpccm.config.g_ctype = container_type.BASH
        return function(*args, **kwargs)

    return wrapper

def centos(function):
    """Decorator to set the Linux distribution to CentOS 7"""
    def wrapper(*args, **kwargs):
        hpccm.config.g_linux_distro = linux_distro.CENTOS
        hpccm.config.g_linux_version = StrictVersion('7.0')
        return function(*args, **kwargs)

    return wrapper

def centos8(function):
    """Decorator to set the Linux distribution to CentOS 8"""
    def wrapper(*args, **kwargs):
        hpccm.config.g_linux_distro = linux_distro.CENTOS
        hpccm.config.g_linux_version = StrictVersion('8.0')
        return function(*args, **kwargs)

    return wrapper

def docker(function):
    """Decorator to set the global container type to docker"""
    def wrapper(*args, **kwargs):
        hpccm.config.g_ctype = container_type.DOCKER
        return function(*args, **kwargs)

    return wrapper

def invalid_cpu_arch(function):
    """Decorator to set the global CPU architecture to an invalid value"""
    def wrapper(*args, **kwargs):
        hpccm.config.g_cpu_arch = None
        return function(*args, **kwargs)

    return wrapper

def invalid_ctype(function):
    """Decorator to set the global container type to an invalid value"""
    def wrapper(*args, **kwargs):
        hpccm.config.g_ctype = None
        return function(*args, **kwargs)

    return wrapper

def invalid_distro(function):
    """Decorator to set the global Linux distribution to an invalid value"""
    def wrapper(*args, **kwargs):
        hpccm.config.g_linux_distro = None
        return function(*args, **kwargs)

    return wrapper

def ppc64le(function):
    """Decorator to set the CPU architecture to ppc64le"""
    def wrapper(*args, **kwargs):
        hpccm.config.g_cpu_arch = cpu_arch.PPC64LE
        return function(*args, **kwargs)

    return wrapper

def singularity(function):
    """Decorator to set the global container type to singularity"""
    def wrapper(*args, **kwargs):
        hpccm.config.g_ctype = container_type.SINGULARITY
        return function(*args, **kwargs)

    return wrapper

def singularity26(function):
    """Decorator to set the global singularity version"""
    def wrapper(*args, **kwargs):
        hpccm.config.g_ctype = container_type.SINGULARITY
        hpccm.config.g_singularity_version = StrictVersion('2.6')
        return function(*args, **kwargs)

    return wrapper

def singularity32(function):
    """Decorator to set the global singularity version"""
    def wrapper(*args, **kwargs):
        hpccm.config.g_ctype = container_type.SINGULARITY
        hpccm.config.g_singularity_version = StrictVersion('3.2')
        return function(*args, **kwargs)

    return wrapper

def ubuntu(function):
    """Decorator to set the Linux distribution to Ubuntu 16.04"""
    def wrapper(*args, **kwargs):
        hpccm.config.g_linux_distro = linux_distro.UBUNTU
        hpccm.config.g_linux_version = StrictVersion('16.04')
        return function(*args, **kwargs)

    return wrapper

def ubuntu18(function):
    """Decorator to set the Linux distribution to Ubuntu 18.04"""
    def wrapper(*args, **kwargs):
        hpccm.config.g_linux_distro = linux_distro.UBUNTU
        hpccm.config.g_linux_version = StrictVersion('18.04')
        return function(*args, **kwargs)

    return wrapper

def x86_64(function):
    """Decorator to set the CPU architecture to x86_64"""
    def wrapper(*args, **kwargs):
        hpccm.config.g_cpu_arch = cpu_arch.X86_64
        return function(*args, **kwargs)

    return wrapper
