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

"""Blob primitive"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import

import hpccm.config

from hpccm.common import container_type

class blob(object):
    """The `blob` primitive inserts a file, without modification, into the
    corresponding place in the container specification file.  If a
    relative path is specified, the path is relative to current
    directory.

    Generally, the blob should be functionally equivalent for each
    container format.

    Wherever possible, the blob primitive should be avoided and other,
    more portable, operations should be used instead.

    # Parameters

    docker: Path to the file containing the Dockerfile blob (Docker
    specific).

    singularity: Path to the file containing the Singularity blob
    (Singularity specific).

    # Example

    ```python
    blob(docker='path/to/foo.docker', singularity='path/to/foo.singularity')
    ```
    """

    def __init__(self, **kwargs):
        """Initialize primitive"""

        #super(blob, self).__init__()

        self.__docker = kwargs.get('docker', {}) # Docker specific
        self.__singularity = kwargs.get('singularity', {}) # Singularity
                                                           # specific

    def __str__(self):
        """String representation of the primitive"""
        if hpccm.config.g_ctype == container_type.DOCKER:
            return self.__read_blob(self.__docker)
        if hpccm.config.g_ctype == container_type.SINGULARITY:
            return self.__read_blob(self.__singularity)
        elif hpccm.config.g_ctype == container_type.BASH:
            return ''
        else:
            raise RuntimeError('Unknown container type')

    def __read_blob(self, path):
        """Read the blob from a file"""

        b = ''
        try:
            if path:
                with open(path, 'r') as f:
                    b = f.read()
            else:
                logging.warning('Blob file not specified')
        except IOError:
            logging.error('Error opening blob {}'.format(path))

        return b
