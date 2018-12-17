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
