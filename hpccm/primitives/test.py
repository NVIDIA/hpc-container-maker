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

"""apptest primitive"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import logging  # pylint: disable=unused-import

import hpccm.config

from hpccm.common import container_type


class test(hpccm.primitives.shell):
    """apptest primitive"""

    def __init__(self, **kwargs):
        """Initialize primitive"""

        super(test, self).__init__(**kwargs)

        self._app = kwargs.get('_app', '')  # Singularity specific

    def __str__(self):
        if self._app == '':
            logging.error('The test building block has to be used with the '
                          '_app-argument!')
        if hpccm.config.g_ctype == container_type.DOCKER:
            logging.error('This building block can be used on Singularity or '
                          'as a scif()-layer only!')
        """String representation of the primitive"""
        if self.commands:
            # prepend last command with exec
            self.commands[-1] = 'exec {0}'.format(self.commands[-1])
            # Format:
            # %apptest appname
            #     cmd1
            #     cmd2
            #     exec cmd3
            s = ['%apptest {0}'.format(self._app)]
            s.extend(['    {}'.format(x) for x in self.commands])
            return '\n'.join(s)
        else:
            return ''
