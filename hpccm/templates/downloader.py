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
import hpccm.config

from hpccm.common import container_type

class downloader(hpccm.base_object):
    """Template for downloading source code"""

    def __init__(self, **kwargs):
        """Initialize template"""

        self.branch = kwargs.get('branch', None)
        self.commit = kwargs.get('commit', None)
        self.package = kwargs.get('package', None)
        self.repository = kwargs.get('repository', None)
        self.src_directory = None
        self.url = kwargs.get('url', None)

        super(downloader, self).__init__(**kwargs)

    def download_step(self, recursive=False, unpack=True, wd='/var/tmp'):
        """Get source code"""

        if not self.repository and not self.package and not self.url:
            raise RuntimeError('must specify a package, repository, or a URL')

        if sum([bool(self.package), bool(self.repository),
                bool(self.url)]) > 1:
            raise RuntimeError('must specify exactly one of a package, repository, or a URL')

        # Check if the caller inherits from the annotate template
        annotate = getattr(self, 'add_annotation', None)

        commands = []

        if self.url:
            # Download package
            commands.append(hpccm.templates.wget().download_step(
                url=self.url, directory=wd))

            if unpack:
                commands.append(self.__unpack(self.url, wd))

            if callable(annotate):
                self.add_annotation('url', self.url)

        elif self.package:
            # Use an already available package
            if unpack:
                commands.append(self.__unpack(self.package, wd))

            if callable(annotate):
                self.add_annotation('package', self.package)

        elif self.repository:
            # Clone git repository
            commands.append(hpccm.templates.git().clone_step(
                branch=self.branch, commit=self.commit, path=wd,
                recursive=recursive, repository=self.repository))

            # Set directory where to find source
            self.src_directory = posixpath.join(wd, posixpath.splitext(
                posixpath.basename(self.repository))[0])

            # Add annotations
            if callable(annotate):
                self.add_annotation('repository', self.repository)
                if self.branch:
                    self.add_annotation('branch', self.branch)
                if self.commit:
                    self.add_annotation('commit', self.commit)

        if hpccm.config.g_ctype == container_type.DOCKER:
            return ' && \\\n    '.join(commands)
        elif hpccm.config.g_ctype == container_type.SINGULARITY:
            return '\n    '.join(commands)
        elif hpccm.config.g_ctype == container_type.BASH:
            return '\n'.join(commands)
        else:
            raise RuntimeError('Unknown container type')

    def __unpack(self, package, wd):
        """Unpack package and set source directory"""

        match_tar = re.search(r'(.*)(?:(?:\.tar)|(?:\.tar\.gz)|(?:\.txz)'
                              r'|(?:\.tgz)|(?:\.tar\.bz2)|(?:\.tar\.xz))$',
                              posixpath.basename(package))

        match_zip = re.search(r'(.*)(?:(?:\.zip))$',
                              posixpath.basename(package))

        if match_tar:
            # Set directory where to find source
            self.src_directory = posixpath.join(wd, match_tar.group(1))
            return hpccm.templates.tar().untar_step(
                posixpath.join(wd, posixpath.basename(package)), directory=wd)
        elif match_zip:
            self.src_directory = posixpath.join(wd, match_zip.group(1))
            return hpccm.templates.zipfile().unzip_step(
                posixpath.join(wd, posixpath.basename(package)), directory=wd)
        else:
            raise RuntimeError('unrecognized package format')

