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

"""git template"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import os
import re

class git(object):
    """Template for working with git repositories"""

    def __init__(self, **kwargs):
        """Initialize template"""

        #super(git, self).__init__()

        self.git_opts = kwargs.get('opts', ['--depth=1'])

    def clone_step(self, branch=None, commit=None, directory='', path='/tmp',
                   repository=None):
        """Clone a git repository"""

        if not repository:
            logging.warning('No git repository specified')
            return ''

        if branch and commit: # pragma: no cover
            logging.warning('Both branch and commit specified, ' +
                            'ignoring branch and using commit...')

        if not directory:
            # Use the final entry in the repository as the directory,
            # stripping off any '.git'.  This is the default git
            # behavior, but the directory may be explicitly needed
            # below.
            directory = os.path.splitext(os.path.basename(repository))[0]

        # Copy so not to modify the member variable
        opts = list(self.git_opts)

        # Commit has precedence over branch
        if branch and not commit:
            opts.append('--branch {}'.format(branch))

        opt_string = ' '.join(opts)

        if commit:
            # Likely need the full repository history, so remove
            # '--depth' if present
            opt_string = re.sub(r'--depth=\d+\s*', '', opt_string).strip()

        # Ensure the path exists
        clone = ['mkdir -p {0}'.format(path),
                 'git -C {0} clone {1} {2} {3}'.format(
                     path, opt_string, repository, directory).strip()]

        if commit:
            clone.append('git -C {0} checkout {1}'.format(
                os.path.join(path, directory), commit))

        return ' && '.join(clone)
