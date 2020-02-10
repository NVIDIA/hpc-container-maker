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

"""Raw primitive"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import hpccm.config

from hpccm.common import container_type

class raw(object):
    """The `raw` primitive inserts the specified string, without
    modification, into the corresponding place in the container
    specification file.

    Generally, the string should be functionally equivalent for each
    container format.

    Wherever possible, the raw primitive should be avoided and other,
    more portable, primitives should be used instead.

    # Parameters

    docker: String containing the Dockerfile instruction (Docker
    specific).

    singularity: String containing the Singularity instruction
    (Singularity specific).

    # Examples

    ```python
    raw(docker='COPY --from=0 /usr/local/openmpi /usr/local/openmpi',
        singularity='# no equivalent to --from')
    ```

    """

    def __init__(self, **kwargs):
        """Raw primitive"""

        #super(raw, self).__init__()

        self.__docker = kwargs.get('docker', '') # Docker specific
        self.__singularity = kwargs.get('singularity', '') # Singularity
                                                           # specific

    def __str__(self):
        """String representation of the primitive"""
        if hpccm.config.g_ctype == container_type.DOCKER:
            return str(self.__docker)
        elif hpccm.config.g_ctype == container_type.SINGULARITY:
            return str(self.__singularity)
        elif hpccm.config.g_ctype == container_type.BASH:
            return ''
        else:
            raise RuntimeError('Unknown container type')
