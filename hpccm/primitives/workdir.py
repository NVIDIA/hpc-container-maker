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

"""Working directory primitive"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import

import hpccm.config

from hpccm.common import container_type
from hpccm.primitives.shell import shell

class workdir(object):
    """The `workdir` primitive sets the working directory for any
    subsequent operations.  As a side effect, if the directory does
    not exist, it is created.

    # Parameters

    directory: The directory path.

    # Examples

    ```python
    workdir(directory='/path/to/directory')
    ```
    """

    def __init__(self, **kwargs):
        """Initialize primitive"""

        #super(workdir, self).__init__()

        self.directory = kwargs.get('directory', '')

    def __str__(self):
        """String representation of the primitive"""
        if self.directory:
            if hpccm.config.g_ctype == container_type.DOCKER:
                return 'WORKDIR {}'.format(self.directory)
            elif hpccm.config.g_ctype == container_type.SINGULARITY:
                s = shell(commands=['mkdir -p {}'.format(self.directory),
                                    'cd {}'.format(self.directory)])
                return str(s)
            elif hpccm.config.g_ctype == container_type.BASH:
                logging.warning('workdir primitive does not map into bash')
                return ''
            else:
                raise RuntimeError('Unknown container type')
        else:
            logging.error('No directory specified')
            return ''
