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

import os
import sys

sys.path.append(os.path.dirname(__file__))

from .common import container_type, package_type

from .ConfigureMake import ConfigureMake
from .Stage import Stage
from .apt_get import apt_get
from .baseimage import baseimage
from .blob import blob
from .cmake import cmake
from .comment import comment
from .copy import copy
from .environment import environment
from .fftw import fftw
from .git import git
from .gnu import gnu
from .hdf5 import hdf5
from .label import label
from .mlnx_ofed import mlnx_ofed
from .mvapich2 import mvapich2
from .mvapich2_gdr import mvapich2_gdr
from .ofed import ofed
from .openmpi import openmpi
from .packages import packages
from .pgi import pgi
from .python import python
from .raw import raw
from .recipe import recipe
from .sed import sed
from .shell import shell
from .tar import tar
from .toolchain import toolchain
from .wget import wget
from .workdir import workdir
from .yum import yum
