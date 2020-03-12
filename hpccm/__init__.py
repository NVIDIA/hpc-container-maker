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

from __future__ import absolute_import

from hpccm.version import __version__

from hpccm.base_object import base_object

from hpccm.common import cpu_arch
from hpccm.common import container_type
from hpccm.common import linux_distro

from hpccm.Stage import Stage
from hpccm.recipe import include
from hpccm.recipe import recipe
from hpccm.toolchain import toolchain

import hpccm.building_blocks
import hpccm.templates
import hpccm.primitives

# Templates
# For backwards compatibility with recipes that use "hpccm.git()", etc.
from hpccm.templates.ConfigureMake import ConfigureMake
from hpccm.templates.git import git
from hpccm.templates.rm import rm
from hpccm.templates.sed import sed
from hpccm.templates.tar import tar
from hpccm.templates.wget import wget
