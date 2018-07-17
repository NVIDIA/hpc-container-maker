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

"""Copy primitive"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import os

import hpccm.config

from hpccm.common import container_type

class copy(object):
    """Copy primitive"""

    def __init__(self, **kwargs):
        """Initialize primitive"""

        #super(copy, self).__init__()

        self.__dest = kwargs.get('dest', '')
        self.__from = kwargs.get('_from', '') # Docker specific
        self.__src = kwargs.get('src', '')

    def __str__(self):
        """String representation of the primitive"""
        if self.__dest and self.__src:
            if hpccm.config.g_ctype == container_type.DOCKER:
                # Format:
                # COPY src1 \
                #     src2 \
                #     src3 \
                #     dest/
                # COPY src dest
                c = ['COPY ']

                if self.__from:
                    c[0] = c[0] + '--from={} '.format(self.__from)

                if isinstance(self.__src, list):
                    c[0] = c[0] + self.__src[0]
                    c.extend(['    {}'.format(x) for x in self.__src[1:]])
                    # Docker requires a trailing slash.  Add one if missing.
                    c.append('    {}'.format(os.path.join(self.__dest, '')))
                else:
                    c[0] = c[0] + '{0} {1}'.format(self.__src, self.__dest)

                return ' \\\n'.join(c)
            if hpccm.config.g_ctype == container_type.SINGULARITY:
                # Format:
                # %files
                #     src1 dest
                #     src2 dest
                #     src3 dest
                if self.__from:
                    logging.warning('The Docker specific "COPY --from" '
                                    'syntax was requested.  Singularity does '
                                    'not have an equivalent, so this is '
                                    'probably not going to do what you want.')

                # Note: if the source is a file and the destination
                # path does not already exist in the container, this
                # will likely error.  Probably need a '%setup' step to
                # first create the directory.
                if isinstance(self.__src, list):
                    return '%files\n' + '\n'.join(
                        ['    {0} {1}'.format(x, self.__dest)
                         for x in self.__src])
                else:
                    return '%files\n    {0} {1}'.format(self.__src,
                                                        self.__dest)
            else:
                raise RuntimeError('Unknown container type')
        else:
            return ''
