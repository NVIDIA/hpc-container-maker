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

import logging # pylint: disable=unused-import

import hpccm.config

from hpccm.common import container_type, package_type

def deb(function):
    """Decorator to set the global package type to deb"""
    def wrapper(*args, **kwargs):
        hpccm.config.g_pkgtype = package_type.DEB
        return function(*args, **kwargs)

    return wrapper

def docker(function):
    """Decorator to set the global container type to docker"""
    def wrapper(*args, **kwargs):
        hpccm.config.g_ctype = container_type.DOCKER
        return function(*args, **kwargs)

    return wrapper

def invalid_ctype(function):
    """Decorator to set the global container type to an invalid value"""
    def wrapper(*args, **kwargs):
        hpccm.config.g_ctype = None
        return function(*args, **kwargs)

    return wrapper

def invalid_pkgtype(function):
    """Decorator to set the global package type to an invalid value"""
    def wrapper(*args, **kwargs):
        hpccm.config.g_pkgtype = None
        return function(*args, **kwargs)

    return wrapper

def rpm(function):
    """Decorator to set the global package type to rpm"""
    def wrapper(*args, **kwargs):
        hpccm.config.g_pkgtype = package_type.RPM
        return function(*args, **kwargs)

    return wrapper

def singularity(function):
    """Decorator to set the global container type to singularity"""
    def wrapper(*args, **kwargs):
        hpccm.config.g_ctype = container_type.SINGULARITY
        return function(*args, **kwargs)

    return wrapper
