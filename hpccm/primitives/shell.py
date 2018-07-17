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

"""Shell primitive"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import

import hpccm.config

from hpccm.common import container_type

class shell(object):
    """Shell primitive"""

    def __init__(self, **kwargs):
        """Initialize primitive"""

        #super(wget, self).__init__()

        self.commands = kwargs.get('commands', [])

    def __str__(self):
        """String representation of the primitive"""
        if self.commands:
            if hpccm.config.g_ctype == container_type.DOCKER:
                # Format:
                # RUN cmd1 && \
                #     cmd2 && \
                #     cmd3
                s = ['RUN {}'.format(self.commands[0])]
                s.extend(['    {}'.format(x) for x in self.commands[1:]])
                return ' && \\\n'.join(s)
            elif hpccm.config.g_ctype == container_type.SINGULARITY:
                # Format:
                # %post
                #     cmd1
                #     cmd2
                #     cmd3
                s = ['%post']
                s.extend(['    {}'.format(x) for x in self.commands])
                return '\n'.join(s)
            else:
                raise RuntimeError('Unknown container type')
        else:
            return ''
