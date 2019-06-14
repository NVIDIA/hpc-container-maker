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

"""Copy primitive"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from distutils.version import StrictVersion
import logging  # pylint: disable=unused-import
import posixpath

import hpccm.config

from hpccm.common import container_type


class copy(object):
    """The `copy` primitive copies files from the host to the container
    image.

    # Parameters

    _app: String containing the [SCI-F](https://www.sylabs.io/guides/2.6/user-guide/reproducible_scif_apps.html)
    identifier.  This also causes the Singularity block to named
    `%appfiles` rather than `%files` (Singularity specific).

    _chown: Set the ownership of the file(s) in the container image
    (Docker specific).

    dest: Path in the container image to copy the file(s)

    files: A dictionary of file pairs, source and destination, to copy
    into the container image.  If specified, has precedence over
    `dest` and `src`.

    _from: Set the source location to a previous build stage rather
    than the host filesystem (Docker specific).

    _mkdir: Boolean flag specifying that the destination directory
    should be created in a separate `%setup` step.  This can be used
    to work around the Singularity limitation that the destination
    directory must exist in the container image prior to copying files
    into the image.  The default is False (Singularity specific).

    _post: Boolean flag specifying that file(s) should be first copied
    to `/` and then moved to the final destination by a `%post` step.
    This can be used to work around the Singularity limitation that
    the destination must exist in the container image prior to copying
    files into the image.  The default is False (Singularity
    specific).

    src: A file, or a list of files, to copy

    # Examples

    ```python
    copy(src='component', dest='/opt/component')
    ```

    ```python
    copy(src=['a', 'b', 'c'], dest='/tmp')
    ```

    ```python
    copy(files={'a': '/tmp/a', 'b': '/opt/b'})
    ```

    """

    def __init__(self, **kwargs):
        """Initialize primitive"""

        #super(copy, self).__init__()

        self._app = kwargs.get('_app', '')  # Singularity specific
        self.__chown = kwargs.get('_chown', '')  # Docker specific
        self.__dest = kwargs.get('dest', '')
        self.__files = kwargs.get('files', {})
        self.__from = kwargs.get('_from', '')  # Docker specific
        self._mkdir = kwargs.get('_mkdir', '')  # Singularity specific
        self._post = kwargs.get('_post', '')  # Singularity specific
        self.__src = kwargs.get('src', '')

        if self._mkdir and self._post:
            logging.error('_mkdir and _post are mutually exclusive!')
            self._post = False # prefer _mkdir

        if self._app and (self._mkdir or self._post):
            logging.error('_app cannot be used with _mkdir or _post!')
            self._mkdir = False # prefer _app
            self._post = False

    def __str__(self):
        """String representation of the primitive"""

        # Build a list of files to make the logic a bit simpler below.
        # The items in the files list are dictionaries with keys 'src'
        # and 'dest'.
        files = []
        if self.__files:
            # Sort to make it deterministic
            files.extend([{'dest': dest, 'src': src}
                          for src, dest in sorted(self.__files.items())])
        elif self.__dest and self.__src:
            files.append({'dest': self.__dest, 'src': self.__src})
        else:
            # No files!
            return ''

        if hpccm.config.g_ctype == container_type.DOCKER:
            if self._app:
                logging.warning('The Singularity specific SCI-F syntax '
                                'was requested. Docker does not have an '
                                'equivalent: using regular COPY!')

            # Format:
            # COPY src1 \
            #     src2 \
            #     src3 \
            #     dest/
            # COPY src1 dest1
            # COPY src2 dest2
            # COPY src3 dest3
            base_inst = 'COPY '

            if self.__chown:
                base_inst = base_inst + '--chown={} '.format(self.__chown)

            if self.__from:
                base_inst = base_inst + '--from={} '.format(self.__from)

            # Docker does not have the notion of copying a set of
            # files to different locations inside the container in a
            # single instruction.  So generate multiple COPY
            # instructions in that case.
            instructions = []
            for pair in files:
                dest = pair['dest']
                src = pair['src']
                c = [base_inst]

                if isinstance(src, list):
                    c[0] = c[0] + src[0]
                    c.extend(['    {}'.format(x) for x in src[1:]])
                    # Docker requires a trailing slash.  Add one if missing.
                    c.append('    {}'.format(posixpath.join(dest, '')))
                else:
                    c[0] = c[0] + '{0} {1}'.format(src, dest)

                instructions.append(' \\\n'.join(c))

            return '\n'.join(instructions)

        elif hpccm.config.g_ctype == container_type.SINGULARITY:
            # Format:
            # %files
            #     src1 dest
            #     src2 dest
            #     src3 dest
            # %files
            #     src1 dest1
            #     src2 dest2
            #     src3 dest3
            section = '%files'
            if (self.__from and
                hpccm.config.g_singularity_version >= StrictVersion('3.2')):
                section = section + ' from {}'.format(self.__from)

            if self._app:
                # SCIF appfiles does not support "from"
                section = '%appfiles {0}'.format(self._app)

            # Singularity will error if the destination does not
            # already exist in the container.  The workarounds are to
            # either 1) prior to copying the files, create the
            # destination directories with %setup or 2) copy the files
            # to a path guaranteed to exist, "/", and then move them
            # later with %post.  Option 1 is the "pre" approach,
            # option 2 is the "post" approach.
            flat_files = []
            post = [] # post actions if _post is enabled
            pre = [] # pre actions if _mkdir is enabled
            for pair in files:
                dest = pair['dest']
                src = pair['src']

                if self._post:
                    dest = '/'

                if isinstance(src, list):
                    for s in src:
                        flat_files.append('    {0} {1}'.format(s, dest))

                        if self._post:
                            post.append('    mv /{0} {1}'.format(posixpath.basename(s), posixpath.join(pair['dest'], s)))
                    if (self._mkdir and
                        posixpath.dirname(dest) != '/' and
                        posixpath.basename(dest) != dest):
                        # When multiple files are to be copied to the
                        # same destination, assume the destination is
                        # a directory
                        pre.append('    mkdir -p ${{SINGULARITY_ROOTFS}}{0}'.format(dest))
                else:
                    flat_files.append('    {0} {1}'.format(src, dest))
                    if (self._mkdir and
                        posixpath.dirname(dest) != '/' and
                        posixpath.basename(dest) != dest):
                        # When a single file is to be copied to a
                        # destination, assume the destination is a
                        # file.
                        pre.append('    mkdir -p ${{SINGULARITY_ROOTFS}}{0}'.format(posixpath.dirname(dest)))
                    elif self._post:
                        post.append('    mv /{0} {1}'.format(posixpath.basename(src), pair['dest']))

            s = ''
            if pre:
                s += '%setup\n' + '\n'.join(pre) + '\n'
            s += section + '\n' + '\n'.join(flat_files)
            if post:
                s += '\n%post\n' + '\n'.join(post)

            return s

        elif hpccm.config.g_ctype == container_type.BASH:
            logging.warning('copy primitive does not map into bash')
            return ''
        else:
            raise RuntimeError('Unknown container type')

    def merge(self, lst, _app=None):
        """Merge one or more instances of the primitive into a single
        instance.  Due to conflicts or option differences the merged
        primitive may not be exact merger.

        """

        if not lst: # pragma: nocover
            raise RuntimeError('no items provided to merge')

        files = {}
        for item in lst:
            if not item.__class__.__name__ == 'copy': # pragma: nocover
                logging.warning('item is not the correct type, skipping...')
                continue

            if item._copy__files:
                files.update(item._copy__files)
            elif isinstance(item._copy__src, list):
                # Build a files dictionary from src / dest options.
                # src is a list.
                for s in item._copy__src:
                    files.update({s: item._copy__dest})
            else:
                # Build a files dictionary from src / dest options.
                files.update({item._copy__src: item._copy__dest})

        return copy(files=files, _app=_app)
