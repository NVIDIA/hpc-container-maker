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

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import os
import re
import subprocess

class git(object):
    """Template for working with git repositories"""

    def __init__(self, **kwargs):
        """Initialize template"""

        #super(git, self).__init__()

        self.git_opts = kwargs.get('opts', ['--depth=1'])

    def __verify(self, repository, branch=None, commit=None, fatal=False):
        """Verify that the specific git reference exists in the remote
           repository"""

        if not branch and not commit: # pragma: no cover
            # Should have already been caught before calling this function
            logging.warning('Must specify one of branch or commit, '
                            'skipping verification')
            return

        command = 'git ls-remote {0} | grep {1}'.format(repository, commit)
        ref = commit
        if branch:
            command = 'git ls-remote --exit-code --heads {0} {1}'.format(repository, branch)
            ref = branch

        with open(os.devnull, 'w') as DEVNULL:
            p = subprocess.Popen(command, shell=True, stdout=DEVNULL,
                                 stderr=DEVNULL)
        o = p.communicate()

        if p.returncode != 0:
            if fatal:
                raise RuntimeError('git ref "{}" does not exist'.format(ref))
            else:
                logging.warning('git ref "{}" does not exist'.format(ref))

        return

    def clone_step(self, branch=None, commit=None, directory='', path='/tmp',
                   repository=None, verify=None, lfs=False):
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

        # Verify the commit / branch is valid
        if verify:
            fatal = False
            if verify == 'fatal':
                fatal = True
            self.__verify(repository, branch=branch, commit=commit,
                          fatal=fatal)

        # If lfs=True use `git lfs clone`
        lfs_string = " "
        if lfs:
          lfs_string = " lfs "

        # Ensure the path exists
        # Would prefer to use 'git -C', but the ancient git included
        # with CentOS7 does not support that option.
        clone = ['mkdir -p {0}'.format(path),
                 'cd {0}'.format(path),
                 'git{0}clone {1} {2} {3}'.format(
                     lfs_string, opt_string, repository, directory).strip(),
                 'cd -']

        if commit:
            clone.extend(['cd {0}'.format(os.path.join(path, directory)),
                          'git checkout {0}'.format(commit),
                          'cd -'])

        return ' && '.join(clone)
