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

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import re

class tar(object):
    """Documentation TBD"""

    def __init__(self, **kwargs):
        """Documentation TBD"""

        #super(tar, self).__init__()

    def untar_step(self, tarball=None, directory=None):
        """Documentation TBD"""

        if not tarball:
            logging.error('tarball is not defined')
            return ''

        opts = ['-x', '-f {}'.format(tarball)]
        if directory:
            opts.append('-C {}'.format(directory))

        if re.search(r'\.tar\.bz2$', tarball):
            opts.append('-j')
        elif re.search(r'\.tar\.gz$', tarball):
            opts.append('-z')
        elif re.search(r'\.tgz$', tarball):
            opts.append('-z')
        elif re.search(r'\.tar$', tarball):
            pass
        else:
            logging.warning('File type not recognized, trying anyway...')

        return 'tar {}'.format(' '.join(opts))
