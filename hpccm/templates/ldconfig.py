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

"""ldconfig template"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import posixpath

import hpccm.base_object

class ldconfig(hpccm.base_object):
    """Template for manipulating the dynamic linker"""

    def __init__(self, **kwargs):
        """Initialize template"""

        super(ldconfig, self).__init__(**kwargs)

        self.ldconfig = kwargs.get('ldconfig', False)

    def ldcache_step(self, conf='hpccm.conf', directory=None):
        """Add a directory to the dynamic linker cache"""

        if not directory:
            logging.error('directory is not defined')
            return ''

        return 'echo "{0}" >> {1} && ldconfig'.format(
            directory, posixpath.join('/etc/ld.so.conf.d', conf))
