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

"""OFED building block"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import

from .apt_get import apt_get
from .comment import comment

class ofed(object):
    """OFED building block"""

    def __init__(self, **kwargs):
        """Initialize building block"""

        # Trouble getting MRO with kwargs working correctly, so just call
        # the parent class constructors manually for now.
        #super(ofed, self).__init__(**kwargs)

        self.__ospackages = kwargs.get('ospackages',
                                       ['dapl2-utils', 'ibutils',
                                        'ibverbs-utils', 'infiniband-diags',
                                        'libdapl-dev', 'libibcm-dev',
                                        'libibmad5', 'libibmad-dev',
                                        'libibverbs1', 'libibverbs-dev',
                                        'libmlx4-1', 'libmlx4-dev',
                                        'libmlx5-1', 'libmlx5-dev',
                                        'librdmacm1', 'librdmacm-dev',
                                        'opensm', 'rdmacm-utils'])

    def runtime(self, _from='0'):
        """Install the runtime from a full build in a previous stage"""
        return self

    def toString(self, ctype):
        """Building block container specification"""

        instructions = []
        instructions.append(comment('OFED').toString(ctype))
        instructions.append(apt_get(
            ospackages=self.__ospackages).toString(ctype))

        return '\n'.join(instructions)
