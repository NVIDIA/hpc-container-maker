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

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import

from .common import container_type

class environment(object):
    """Documentation TBD"""

    def __init__(self, **kwargs):
        """Documentation TBD"""

        #super(environment, self).__init__()

        # Singularity does not export environment variables into the
        # current build context when using the '%environment' section.
        # The variables are only set when the container is run.  If
        # this variable is True, then also generate a '%post' section
        # to set the variables for the build context.
        self.__export = kwargs.get('_export', True) # Singularity specific
        self.variables = kwargs.get('variables', {})

    def toString(self, ctype):
        """Documentation TBD"""

        if self.variables:
            keyvals = []
            for key, val in sorted(self.variables.items()):
                keyvals.append('{0}={1}'.format(key, val))

            if ctype == container_type.DOCKER:
                # Format:
                # ENV K1=V1 \
                #     K2=V2 \
                #     K3=V3
                environ = ['ENV {}'.format(keyvals[0])]
                environ.extend(['    {}'.format(x) for x in keyvals[1:]])
                return ' \\\n'.join(environ)
            elif ctype == container_type.SINGULARITY:
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
                    environ.extend(['    export {}'.format(x) for x in keyvals])
                return '\n'.join(environ)
            else:
                logging.error('Unknown container type')
                return ''
        else:
            return ''
