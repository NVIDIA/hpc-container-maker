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

"""Documentation TBD"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import

class toolchain(object):
    """Documentation TBD"""

    def __init__(self, **kwargs):
        """Documentation TBD"""

        self.CC = kwargs.get('CC')
        self.CUDA_HOME = kwargs.get('CUDA_HOME')
        self.CXX = kwargs.get('CXX')
        self.F77 = kwargs.get('F77')
        self.F90 = kwargs.get('F90')
        self.FC = kwargs.get('FC')
