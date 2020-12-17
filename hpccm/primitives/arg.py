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

"""Environment primitive"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import

import hpccm.config

from hpccm.common import container_type

class arg(object):
    """The `arg` primitive sets the corresponding environment
    variables during the build time of a docker container. 
    This primitive is docker specific and is ignored for singularity

    # Parameters

    variables: A dictionary of key / value pairs.  The default is an
    empty dictionary.

    # Examples

    ```python
    arg(variables={'HTTP_PROXY': 'proxy.example.com', 'NO_PROXY':'example.com'})
    ```
    """

    def __init__(self, **kwargs):
        """Initialize primitive"""
        self.__variables = kwargs.get('variables', {})

    def __str__(self):
        """String representation of the primitive"""
        if self.__variables:

            if hpccm.config.g_ctype == container_type.SINGULARITY or \
               hpccm.config.g_ctype == container_type.BASH:
                return ""
            elif hpccm.config.g_ctype == container_type.DOCKER:
                string = ""
                num_vars = len(self.__variables)
                for count, (key, val) in enumerate(sorted(self.__variables.items())):
                    eol = "" if count == num_vars - 1 else "\n"
                    if val == "":
                        string += 'ARG {0}'.format(key) + eol
                    else:
                        string += 'ARG {0}={1}'.format(key, val) + eol
                return string
            else:
                raise RuntimeError('Unknown container type')
        else:
            return ''
