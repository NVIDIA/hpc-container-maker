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

"""Base image primitive"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from distutils.version import StrictVersion
import logging # pylint: disable=unused-import
import re

import hpccm.config

from hpccm.common import container_type
from hpccm.primitives.comment import comment
from hpccm.primitives.shell import shell

class baseimage(object):
    """The `baseimage` primitive defines the base image to be used.

    # Parameters

    _arch: The underlying CPU architecture of the base image.  Valid
    values are `aarch64`, `ppc64le`, and `x86_64`.  By default, the
    primitive attemps to figure out the CPU architecture by inspecting
    the image identifier, and falls back to `x86_64` if unable to
    determine the CPU architecture automatically.

    _as: Name for the stage.  When using Singularity multi-stage
    recipes, this value must be specified.  The default value is
    empty.

    _bootstrap: The Singularity bootstrap agent.  This default value
    is `docker` (Singularity specific).

    _distro: The underlying Linux distribution of the base image.
    Valid values are `centos`, `centos7`, `centos8`, `redhat`, `rhel`,
    `rhel7`, `rhel8, `ubuntu`, `ubuntu16`, and `ubuntu18`.  By
    default, the primitive attempts to figure out the Linux
    distribution by inspecting the image identifier, and falls back to
    `ubuntu` if unable to determine the Linux distribution
    automatically.

    _docker_env: Boolean specifying whether to load the Docker base
     image environment, i.e., source
     `/.singularity.d/env/10-docker*.sh` (Singularity specific).  The
     default value is True.

    image: The image identifier to use as the base image.  The default value is `nvidia/cuda:9.0-devel-ubuntu16.04`.

    AS: Name for the build stage (Docker specific).  The default value
    is empty.  This parameter is deprecated; use `_as` instead.

    # Examples

    ```python
    baseimage(image='nvidia/cuda:9.1-devel')
    ```

    """

    def __init__(self, **kwargs):
        """Initialize the primitive"""

        #super(baseimage, self).__init__()

        self.__arch = kwargs.get('_arch', '')
        self.__as = kwargs.get('AS', '') # Deprecated
        self.__as = kwargs.get('_as', self.__as)
        self.__bootstrap = kwargs.get('_bootstrap', 'docker')
        self.image = kwargs.get('image', 'nvidia/cuda:9.0-devel-ubuntu16.04')
        self.__distro = kwargs.get('_distro', '')
        self.__docker_env = kwargs.get('_docker_env', True) # Singularity specific

        # Set the global CPU architecture.  User the user specified
        # value if available, otherwise try to figure it out based on
        # the image name.
        self.__arch = self.__arch.lower()
        if self.__arch == 'aarch64':
            hpccm.config.set_cpu_architecture('aarch64')
        elif self.__arch == 'ppc64le':
            hpccm.config.set_cpu_architecture('ppc64le')
        elif self.__arch == 'x86_64':
            hpccm.config.set_cpu_architecture('x86_64')
        elif re.search(r'aarch64|arm64v8', self.image):
            hpccm.config.set_cpu_architecture('aarch64')
        elif re.search(r'ppc64le', self.image):
            hpccm.config.set_cpu_architecture('ppc64le')
        else:
            hpccm.config.set_cpu_architecture('x86_64')

        # Set the global Linux distribution.  Use the user specified
        # value if available, otherwise try to figure it out based on
        # the image name.
        self.__distro = self.__distro.lower()
        if self.__distro == 'ubuntu':
            hpccm.config.set_linux_distro('ubuntu')
        elif self.__distro == 'ubuntu16':
            hpccm.config.set_linux_distro('ubuntu16')
        elif self.__distro == 'ubuntu18':
            hpccm.config.set_linux_distro('ubuntu18')
        elif self.__distro == 'centos':
            hpccm.config.set_linux_distro('centos')
        elif self.__distro == 'centos7':
            hpccm.config.set_linux_distro('centos7')
        elif self.__distro == 'centos8':
            hpccm.config.set_linux_distro('centos8')
        elif (self.__distro == 'rhel' or self.__distro == 'redhat'):
            hpccm.config.set_linux_distro('rhel')
        elif self.__distro == 'rhel7':
            hpccm.config.set_linux_distro('rhel7')
        elif self.__distro == 'rhel8':
            hpccm.config.set_linux_distro('rhel8')
        elif re.search(r'centos:?7', self.image):
            hpccm.config.set_linux_distro('centos7')
        elif re.search(r'centos:?8', self.image):
            hpccm.config.set_linux_distro('centos8')
        elif re.search(r'centos|rhel|redhat', self.image):
            hpccm.config.set_linux_distro('centos')
        elif re.search(r'ubi:?7', self.image):
            hpccm.config.set_linux_distro('rhel7')
        elif re.search(r'ubi:?8', self.image):
            hpccm.config.set_linux_distro('rhel8')
        elif re.search(r'ubuntu:?16', self.image):
            hpccm.config.set_linux_distro('ubuntu16')
        elif re.search(r'ubuntu:?18', self.image):
            hpccm.config.set_linux_distro('ubuntu18')
        elif re.search(r'ubuntu', self.image):
            hpccm.config.set_linux_distro('ubuntu')
        else:
            logging.warning('Unable to determine the Linux distribution, defaulting to Ubuntu')
            hpccm.config.set_linux_distro('ubuntu')

    def __str__(self):
        """String representation of the primitive"""
        if hpccm.config.g_ctype == container_type.DOCKER:
            image = 'FROM {}'.format(self.image)

            if self.__as:
                image = image + ' AS {}'.format(self.__as)

            return image
        elif hpccm.config.g_ctype == container_type.SINGULARITY:
            image = 'BootStrap: {0}\nFrom: {1}'.format(self.__bootstrap,
                                                       self.image)

            if (self.__as and
                hpccm.config.g_singularity_version >= StrictVersion('3.2')):
                image = image + '\nStage: {}'.format(self.__as)

                image = str(comment('NOTE: this definition file depends on features only available in Singularity 3.2 and later.')) + '\n' + image

            # Singularity does not inherit the environment from the
            # Docker base image automatically.  Do it manually.
            if self.__docker_env:
                docker_env = shell(
                    chdir=False,
                    commands=['. /.singularity.d/env/10-docker*.sh'])
                image = image + '\n' + str(docker_env)

            return image
        elif hpccm.config.g_ctype == container_type.BASH:
            return '#!/bin/bash -ex'
        else:
            raise RuntimeError('Unknown container type')
