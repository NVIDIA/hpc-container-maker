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
from .shell import shell

class workdir(object):
    """Documentation TBD"""

    def __init__(self, **kwargs):
        """Documentation TBD"""

        #super(workdir, self).__init__()

        self.directory = kwargs.get('directory', '')

    def toString(self, ctype):
        """Documentation TBD"""

        if self.directory:
            if ctype == container_type.DOCKER:
                return 'WORKDIR {}'.format(self.directory)
            elif ctype == container_type.SINGULARITY:
                s = shell(commands=['mkdir -p {}'.format(self.directory),
                                    'cd {}'.format(self.directory)])
                return s.toString(ctype)
            else:
                logging.error('Unknown container type')
            return ''
        else:
            logging.error('No directory specified')
            return ''
