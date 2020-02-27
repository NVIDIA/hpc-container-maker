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
import platform
import sys

from hpccm.common import cpu_arch
from hpccm.common import container_type
from hpccm.common import linux_distro

# Global variables
g_cpu_arch = cpu_arch.X86_64         # CPU architecture
if platform.machine() == 'aarch64':
  g_cpu_arch = cpu_arch.AARCH64
elif platform.machine() == 'ppc64le':
  g_cpu_arch = cpu_arch.PPC64LE
g_ctype = container_type.DOCKER      # Container type
g_linux_distro = linux_distro.UBUNTU # Linux distribution
g_linux_version = StrictVersion('16.04') # Linux distribution version
g_singularity_version = StrictVersion('2.6') # Singularity version

def get_cpu_architecture():
  """Return the architecture string for the currently configured CPU
  architecture, e.g., `aarch64`, `ppc64le`, or `x86_64`.

  """

  this = sys.modules[__name__]
  if this.g_cpu_arch == cpu_arch.AARCH64:
    return 'aarch64'
  elif this.g_cpu_arch == cpu_arch.PPC64LE:
    return 'ppc64le'
  elif this.g_cpu_arch == cpu_arch.X86_64:
    return 'x86_64'
  else: # pragma: no cover
    raise RuntimeError('Unrecognized processor architecture')

def get_format():
  """Return the container format string for the currently configured
  format, e.g., `bash`, `docker`, or `singularity`."""

  this = sys.modules[__name__]

  if this.g_ctype == container_type.BASH:
    return 'bash'
  elif this.g_ctype == container_type.DOCKER:
    return 'docker'
  elif this.g_ctype == container_type.SINGULARITY:
    return 'singularity'
  else: # pragma: no cover
    raise RuntimeError('Unrecognized format')

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

def set_cpu_architecture(arch):
  """Set the CPU architecture

  In most cases, the `baseimage` primitive should be relied upon to
  set the CPU architecture.  Only use this function if you really
  know what you are doing.

  # Arguments

  arch (string): Value values are `aarch64`, `ppc64le`, and `x86_64`.
  `arm` and `arm64v8` are aliases for `aarch64`, `power` is an alias
  for `ppc64le`, and `amd64` and `x86` are aliases for `x86_64`.
  """
  this = sys.modules[__name__]
  if arch == 'aarch64' or arch == 'arm' or arch == 'arm64v8':
    this.g_cpu_arch = cpu_arch.AARCH64
  elif arch == 'ppc64le' or arch == 'power':
    this.g_cpu_arch = cpu_arch.PPC64LE
  elif arch == 'x86_64' or arch == 'amd64' or arch == 'x86':
    this.g_cpu_arch = cpu_arch.X86_64
  else:
    logging.warning('Unable to determine the CPU architecture, defaulting to x86_64')
    this.g_cpu_arch = cpu_arch.X86_64

def set_linux_distro(distro):

  """Set the Linux distribution and version

  In most cases, the `baseimage` primitive should be relied upon to
  set the Linux distribution.  Only use this function if you really
  know what you are doing.

  # Arguments

  distro (string): Valid values are `centos7`, `centos8`, `rhel7`,
  `rhel8`, `ubuntu16`, and `ubuntu18`.  `ubuntu` is an alias for
  `ubuntu16`, `centos` is an alias for `centos7`, and `rhel` is an
  alias for `rhel7`.

  """
  this = sys.modules[__name__]
  if distro == 'centos':
    this.g_linux_distro = linux_distro.CENTOS
    this.g_linux_version = StrictVersion('7.0')
  elif distro == 'centos7':
    this.g_linux_distro = linux_distro.CENTOS
    this.g_linux_version = StrictVersion('7.0')
  elif distro == 'centos8':
    this.g_linux_distro = linux_distro.CENTOS
    this.g_linux_version = StrictVersion('8.0')
  elif distro == 'rhel':
    this.g_linux_distro = linux_distro.RHEL
    this.g_linux_version = StrictVersion('7.0')
  elif distro == 'rhel7':
    this.g_linux_distro = linux_distro.RHEL
    this.g_linux_version = StrictVersion('7.0')
  elif distro == 'rhel8':
    this.g_linux_distro = linux_distro.RHEL
    this.g_linux_version = StrictVersion('8.0')
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

def set_singularity_version(ver):
  """Set the Singularity definition file format version

  The Singularity definition file format was extended in version 3.2
  to enable multi-stage builds.  However, these changes are not
  backwards compatible.

  # Arguments

  ver (string): Singularity definition file format version.

  """
  this = sys.modules[__name__]
  this.g_singularity_version = StrictVersion(ver)
