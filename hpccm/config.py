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

# Global configuration
#
# Import this as
# import hpccm.config
#
# And access variables as
# hpccm.config.var

from __future__ import absolute_import

from distutils.version import StrictVersion
import logging
import sys

from hpccm.common import container_type
from hpccm.common import linux_distro

# Global variables
g_ctype = container_type.DOCKER      # Container type
g_linux_distro = linux_distro.UBUNTU # Linux distribution
g_linux_version = StrictVersion('16.04') # Linux distribution version

def set_container_format(ctype):
  """Set the container format

  # Arguments

  ctype (string): 'docker' to specify the Dockerfile format, or
  'singularity' to specify the Singularity definition file format

  # Raises

  RuntimeError: invalid container type argument
  """
  this = sys.modules[__name__]
  if ctype == 'docker':
    this.g_ctype = container_type.DOCKER
  elif ctype == 'singularity':
    this.g_ctype = container_type.SINGULARITY
  else:
    raise RuntimeError('Unrecognized container format: {}'.format(ctype))

def set_linux_distro(distro):
  """Set the Linux distribution and version

  In most cases, the `baseimage` primitive should be relied upon to
  set the Linux distribution.  Only use this function if you really
  know what you are doing.

  # Arguments

  distro (string): Valid values are `centos7`, `ubuntu16`, and
  `ubuntu18`.  `ubuntu` is an alias for `ubuntu16` and `centos` is an
  alias for `centos7`.
  """
  this = sys.modules[__name__]
  if distro == 'centos':
    this.g_linux_distro = linux_distro.CENTOS
    this.g_linux_version = StrictVersion('7.0')
  elif distro == 'centos7':
    this.g_linux_distro = linux_distro.CENTOS
    this.g_linux_version = StrictVersion('7.0')
  elif distro == 'ubuntu':
    this.g_linux_distro = linux_distro.UBUNTU
    this.g_linux_version = StrictVersion('16.04')
  elif distro == 'ubuntu16':
    this.g_linux_distro = linux_distro.UBUNTU
    this.g_linux_version = StrictVersion('16.04')
  elif distro == 'ubuntu18':
    this.g_linux_distro = linux_distro.UBUNTU
    this.g_linux_version = StrictVersion('18.04')
  else:
    logging.warning('Unable to determine the Linux distribution, defaulting to Ubuntu')
    this.g_linux_distro = linux_distro.UBUNTU
    this.g_linux_version = StrictVersion('16.04')
