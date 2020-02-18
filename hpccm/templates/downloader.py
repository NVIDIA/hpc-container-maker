# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
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

"""downloader template"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import posixpath
import re

import hpccm.base_object

class downloader(hpccm.base_object):
    """Template for downloading source code"""

    def __init__(self, **kwargs):
        """Initialize template"""

        self.branch = kwargs.get('branch', None)
        self.commit = kwargs.get('commit', None)
        self.repository = kwargs.get('repository', None)
        self.src_directory = None
        self.url = kwargs.get('url', None)

        super(downloader, self).__init__(**kwargs)

    def download_step(self, recursive=False, unpack=True, wd='/var/tmp'):
        """Get source code"""

        if not self.repository and not self.url:
            raise RuntimeError('must specify a repository or a URL')

        if self.repository and self.url:
            raise RuntimeError('cannot specify both a repository and a URL')

        commands = []

        if self.url:
            # Download tarball
            commands.append(hpccm.templates.wget().download_step(
                url=self.url, directory=wd))

            if unpack:
                # Unpack tarball
                tarball = posixpath.join(wd, posixpath.basename(self.url))
                commands.append(hpccm.templates.tar().untar_step(
                    tarball, directory=wd))

                match = re.search(r'(.*)(?:(?:\.tar)|(?:\.tar\.gz)'
                                  r'|(?:\.tgz)|(?:\.tar\.bz2)|(?:\.tar\.xz))$',
                                  tarball)
                if match:
                    # Set directory where to find source
                    self.src_directory = posixpath.join(wd, match.group(1))
                else:
                    raise RuntimeError('unrecognized package format')


        elif self.repository:
            # Clone git repository
            commands.append(hpccm.templates.git().clone_step(
                branch=self.branch, commit=self.commit, path=wd,
                recursive=recursive, repository=self.repository))

            # Set directory where to find source
            self.src_directory = posixpath.join(wd, posixpath.splitext(
                posixpath.basename(self.repository))[0])

        return ' && \\\n    '.join(commands)
