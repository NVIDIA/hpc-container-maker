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

from hpccm.common import container_type, linux_distro
from hpccm.primitives.shell import shell

class baseimage(object):
    """The `baseimage` primitive defines the base image to be used.

    # Parameters

    _as: Name for the build stage (Docker specific).  The default
    value is empty.

    _distro: The underlying Linux distribution of the base image.
    Valid values are `centos`, `redhat`, `rhel`, `ubuntu`, `ubuntu16`,
    and `ubuntu18`.  By default, the primitive attempts to figure out
    the Linux distribution by inspecting the image identifier, and
    falls back to `ubuntu` if unable to determine the Linux
    distribution automatically.

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

        self.__as = kwargs.get('AS', '') # Docker specific
        self.__as = kwargs.get('_as', self.__as) # Docker specific
        self.image = kwargs.get('image', 'nvidia/cuda:9.0-devel-ubuntu16.04')
        self.__distro = kwargs.get('_distro', '')

        # Set the global Linux distribution.  Use the user specified
        # value if available, otherwise try to figure it out based on
        # the image name.
        self.__distro = self.__distro.lower()
        if self.__distro == 'ubuntu':
            hpccm.config.g_linux_distro = linux_distro.UBUNTU
            hpccm.config.g_linux_version = StrictVersion('16.04')
        elif self.__distro == 'ubuntu16':
            hpccm.config.g_linux_distro = linux_distro.UBUNTU
            hpccm.config.g_linux_version = StrictVersion('16.04')
        elif self.__distro == 'ubuntu18':
            hpccm.config.g_linux_distro = linux_distro.UBUNTU
            hpccm.config.g_linux_version = StrictVersion('18.04')
        elif (self.__distro == 'centos' or self.__distro == 'rhel' or
              self.__distro == 'redhat'):
            hpccm.config.g_linux_distro = linux_distro.CENTOS
            hpccm.config.g_linux_version = StrictVersion('7.0')
        elif re.search(r'centos|rhel|redhat', self.image):
            hpccm.config.g_linux_distro = linux_distro.CENTOS
            hpccm.config.g_linux_version = StrictVersion('7.0')
        elif re.search(r'ubuntu:?16', self.image):
            hpccm.config.g_linux_distro = linux_distro.UBUNTU
            hpccm.config.g_linux_version = StrictVersion('16.04')
        elif re.search(r'ubuntu:?18', self.image):
            hpccm.config.g_linux_distro = linux_distro.UBUNTU
            hpccm.config.g_linux_version = StrictVersion('18.04')
        elif re.search(r'ubuntu', self.image):
            hpccm.config.g_linux_distro = linux_distro.UBUNTU
            hpccm.config.g_linux_version = StrictVersion('16.04')
        else:
            logging.warning('Unable to determine the Linux distribution, defaulting to Ubuntu')
            hpccm.config.g_linux_distro = linux_distro.UBUNTU
            hpccm.config.g_linux_version = StrictVersion('16.04')

    def __str__(self):
        """String representation of the primitive"""
        if hpccm.config.g_ctype == container_type.DOCKER:
            image = 'FROM {}'.format(self.image)

            if self.__as:
                image = image + ' AS {}'.format(self.__as)

            return image
        elif hpccm.config.g_ctype == container_type.SINGULARITY:
            # Singularity does not inherit the environment from the
            # Docker base image automatically.  Do it manually.
            docker_env = shell(chdir=False,
                               commands=['. /.singularity.d/env/10-docker.sh'])
            return 'BootStrap: docker\nFrom: {0}\n{1}'.format(self.image,
                                                              str(docker_env))
        else:
            raise RuntimeError('Unknown container type')
