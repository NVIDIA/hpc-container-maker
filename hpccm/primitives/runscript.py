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

"""Runscript primitive"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import

import hpccm.config

from hpccm.common import container_type

class runscript(object):
    """Runscript primitive"""

    def __init__(self, **kwargs):
        """Initialize primitive"""

        #super(wget, self).__init__()

        self.commands = kwargs.get('commands', [])

    def __str__(self):
        """String representation of the primitive"""
        if self.commands:
            if hpccm.config.g_ctype == container_type.DOCKER:
                if self._app:
                    logging.warning('The Singularity specific %app.. syntax was'
                                    'requested. Docker does not have an '
                                    'equivalent: ignoring statement!')
                    return ''
                if len(self.commands) > 1:
                    logging.warning('Multiple commands given to runscript.'
                                    'Docker ENTRYPOINT supports just one cmd:'
                                    'ignoring remaining commands!')
                # Format:
                # ENTRYPOINT ["cmd1", "arg1", "arg2", ...]
                s = []
                s.extend('"{}"'.format(x) for x in self.commands[0].split(" "))
                return 'ENTRYPOINT [' + ', '.join(s) + ']'

            elif hpccm.config.g_ctype == container_type.SINGULARITY:
                # prepend last command with exec
                last_cmd_index = len(self.commands) - 1
                self.commands[last_cmd_index] = 'exec {0}'.format(self.commands[last_cmd_index])
                # Format:
                # %runscript
                #     cmd1
                #     cmd2
                #     exec cmd3
                s = ['%runscript']
                s.extend(['    {}'.format(x) for x in self.commands])
                return '\n'.join(s)
            else:
                raise RuntimeError('Unknown container type')
        else:
            return ''
