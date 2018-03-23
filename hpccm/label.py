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

class label(object):
    """Documentation TBD"""

    def __init__(self, **kwargs):
        """Documentation TBD"""

        #super(label, self).__init__()

        self.metadata = kwargs.get('metadata', {})

    def toString(self, ctype):
        """Documentation TBD"""

        if self.metadata:
            if ctype == container_type.DOCKER:
                # Format:
                # LABEL K1=V1 \
                #     K2=V2 \
                #     K3=V3
                keyvals = []
                for key, val in sorted(self.metadata.items()):
                    keyvals.append('{0}={1}'.format(key, val))

                label = ['LABEL {}'.format(keyvals[0])]
                label.extend(['    {}'.format(x) for x in keyvals[1:]])
                return ' \\\n'.join(label)
            elif ctype == container_type.SINGULARITY:
                # Format:
                # %labels
                #     K1 V1
                #     K2 V2
                #     K3 V3
                keyvals = []
                for key, val in sorted(self.metadata.items()):
                    keyvals.append('{0} {1}'.format(key, val))

                label = ['%labels']
                label.extend(['    {}'.format(x) for x in keyvals])
                return '\n'.join(label)
            else:
                logging.error('Unknown container type')
                return ''
        else:
            return ''
