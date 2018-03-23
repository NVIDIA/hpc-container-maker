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
import os

from .common import container_type

class copy(object):
    """Documentation TBD"""

    def __init__(self, **kwargs):
        """Documentation TBD"""

        #super(copy, self).__init__()

        self.dest = kwargs.get('dest', '')
        self.src = kwargs.get('src', '')
        self.__from = kwargs.get('_from', '') # Docker specific

    def toString(self, ctype):
        """Documentation TBD"""

        if self.dest and self.src:
            if ctype == container_type.DOCKER:
                # Format:
                # COPY src1 \
                #     src2 \
                #     src3 \
                #     dest/
                # COPY src dest
                copy = ['COPY ']

                if self.__from:
                    copy[0] = copy[0] + '--from={} '.format(self.__from)

                if isinstance(self.src, list):
                    copy[0] = copy[0] + self.src[0]
                    copy.extend(['    {}'.format(x) for x in self.src[1:]])
                    # Docker requires a trailing slash.  Add one if missing.
                    copy.append('    {}'.format(os.path.join(self.dest, '')))
                else:
                    copy[0] = copy[0] + '{0} {1}'.format(self.src, self.dest)

                return ' \\\n'.join(copy)
            if ctype == container_type.SINGULARITY:
                # Format:
                # %files
                #     src1 dest
                #     src2 dest
                #     src3 dest
                if self.__from:
                    logging.warning('The Docker specific "COPY --from" syntax was requested.  Singularity does not have an equivalent, so this is probably not going to do what you want.')

                # Note: if the source is a file and the destination
                # path does not already exist in the container, this
                # will likely error.  Probably need a '%setup' step to
                # first create the directory.
                if isinstance(self.src, list):
                    return '%files\n' + '\n'.join(
                        ['    {0} {1}'.format(x, self.dest) for x in self.src])
                else:
                    return '%files\n    {0} {1}'.format(self.src, self.dest)
            else:
                logging.error('Unknown container type')
                return ''
        else:
            return ''
