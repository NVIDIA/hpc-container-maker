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
import shlex

class sed(object):
    """Documentation TBD"""

    def __init__(self, **kwargs):
        """Documentation TBD"""

        #super(sed, self).__init__()

        self.sed_opts = kwargs.get('opts', [])

    def sed_step(self, file=None, in_place=True, patterns=[]):
        """Documentation TBD"""

        if not file:
            logging.error('file is not defined')
            return ''

        if not patterns:
            logging.error('patterns is not defined')
            return ''

        # Copy so not to modify the member variable
        opts = list(self.sed_opts)

        if in_place:
            opts.append('-i')

        opt_string = ' '.join(opts)

        quoted_patterns = ['-e {}'.format(shlex.quote(patterns[0]))]
        quoted_patterns.extend('        -e {}'.format(shlex.quote(x)) for x in patterns[1:])
        quoted_pattern_string = ' \\\n'.join(quoted_patterns)

        return 'sed {0} {1} {2}'.format(opt_string, quoted_pattern_string, file) 
