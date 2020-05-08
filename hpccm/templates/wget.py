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

"""wget template"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import

import hpccm.base_object

class wget(hpccm.base_object):
    """wget template"""

    def __init__(self, **kwargs):
        """Initialize wget template"""

        super(wget, self).__init__(**kwargs)

        self.wget_opts = kwargs.get('opts', ['-q', '-nc',
                                             '--no-check-certificate'])

    def download_step(self, outfile=None, referer=None, url=None,
                      directory='/tmp'):
        """Generate wget command line string"""

        if not url:
            logging.error('url is not defined')
            return ''

        # Copy so not to modify the member variable
        opts = self.wget_opts

        if outfile:
            opts.append('-O {}'.format(outfile))

        if referer:
            opts.append('--referer {}'.format(referer))

        opt_string = ' '.join(self.wget_opts)

        # Add annotation if the caller inherits from the annotate template
        if callable(getattr(self, 'add_annotation', None)):
            self.add_annotation('url', url)

        # Ensure the directory exists
        return 'mkdir -p {1} && wget {0} -P {1} {2}'.format(opt_string,
                                                            directory, url)
