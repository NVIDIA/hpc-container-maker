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

"""tar template"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import re

import hpccm.base_object

class tar(hpccm.base_object):
    """tar template"""

    def __init__(self, **kwargs):
        """Initialize tar template"""

        super(tar, self).__init__(**kwargs)

    def untar_step(self, tarball=None, directory=None, args=None):
        """Generate untar command line string"""

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
        elif re.search(r'\.tar\.xz$', tarball):
            opts.append('-J')
        elif re.search(r'\.txz$', tarball):
            opts.append('-J')
        elif re.search(r'\.tbz$', tarball):
            opts.append('-j')
        elif re.search(r'\.tar$', tarball):
            pass
        else:
            logging.warning('File type not recognized, trying anyway...')

        if args:
            opts.extend(args)

        if directory:
            return 'mkdir -p {0} && tar {1}'.format(directory, ' '.join(opts))
        else:
            return 'tar {}'.format(' '.join(opts))
