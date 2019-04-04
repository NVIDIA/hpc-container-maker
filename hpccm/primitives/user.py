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

"""User primitive"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import

import hpccm.config

from hpccm.common import container_type

class user(object):
    """The `user` primitive sets the user name to use for any subsequent
    steps.

    This primitive is the null operation for Singularity.

    # Parameters

    user: The user name to use.  The default is an empty string.

    # Examples

    ```python
    user(user='ncognito')
    ```
    """

    def __init__(self, **kwargs):
        """Initialize primitive"""

        self.user = kwargs.get('user', '')

    def __str__(self):
        """String representation of the primitive"""
        if self.user:
            if hpccm.config.g_ctype == container_type.DOCKER:
                return 'USER {}'.format(self.user)
            elif hpccm.config.g_ctype == container_type.SINGULARITY:
                return ''
            elif hpccm.config.g_ctype == container_type.BASH:
                return ''
            else:
                raise RuntimeError('Unknown container type')
        else:
            logging.error('No user specified')
            return ''
