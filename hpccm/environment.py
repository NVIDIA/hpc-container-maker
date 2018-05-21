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

class environment(object):
    """Environment primitive"""

    def __init__(self, **kwargs):
        """Initialize primitive"""

        #super(environment, self).__init__()

        # Singularity does not export environment variables into the
        # current build context when using the '%environment' section.
        # The variables are only set when the container is run.  If
        # this variable is True, then also generate a '%post' section
        # to set the variables for the build context.
        self.__export = kwargs.get('_export', True) # Singularity specific
        self.__variables = kwargs.get('variables', {})

    def __str__(self):
        """String representation of the primitive"""
        if self.__variables:
            keyvals = []
            for key, val in sorted(self.__variables.items()):
                keyvals.append('{0}={1}'.format(key, val))

            if hpccm.config.g_ctype == container_type.DOCKER:
                # Format:
                # ENV K1=V1 \
                #     K2=V2 \
                #     K3=V3
                environ = ['ENV {}'.format(keyvals[0])]
                environ.extend(['    {}'.format(x) for x in keyvals[1:]])
                return ' \\\n'.join(environ)
            elif hpccm.config.g_ctype == container_type.SINGULARITY:
                # Format:
                # %environment
                #     export K1=V1
                #     export K2=V2
                #     export K3=V3
                # %post
                #     export K1=V1
                #     export K2=V2
                #     export K3=V3
                environ = ['%environment']
                environ.extend(['    export {}'.format(x) for x in keyvals])

                if self.__export:
                    environ.extend(['%post'])
                    environ.extend(['    export {}'.format(x)
                                    for x in keyvals])
                return '\n'.join(environ)
            else:
                raise RuntimeError('Unknown container type')
        else:
            return ''
