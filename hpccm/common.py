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

"""Common stuff used by multiple parts of HPC Container Maker"""

from enum import Enum

class container_type(Enum):
    """Supported container types"""
    DOCKER = 1
    SINGULARITY = 2

class package_type(Enum):
    """Supported package manager types"""
    DEB = 1
    RPM = 2
