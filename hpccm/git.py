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

class git(object):
    """Documentation TBD"""

    def __init__(self, **kwargs):
        """Documentation TBD"""

        #super(git, self).__init__()

        self.git_opts = kwargs.get('opts', ['--depth=1'])

    def clone_step(self, branch=None, directory='', path='/tmp',
                   repository=None):
        """Documentation TBD"""

        if not repository:
            logging.warning('No git repository specified')
            return ''

        # Copy so not to modify the member variable
        opts = list(self.git_opts)

        if branch:
            opts.append('--branch {}'.format(branch))

        opt_string = ' '.join(opts)

        # Ensure the path exists
        return 'mkdir -p {0} && git -C {0} clone {1} {2} {3}'.format(
            path, opt_string, repository, directory)
