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

import logging  # pylint: disable=unused-import
import os

import hpccm.config

from hpccm.common import container_type


class copy(object):
    """The `copy` primitive copies files from the host to the container
    image.

    # Parameters

    _app: String containing the [SCI-F](https://www.sylabs.io/guides/2.6/user-guide/reproducible_scif_apps.html)
    identifier.  This also causes the Singularity block to named
    `%appfiles` rather than `%files` (Singularity specific).

    dest: Path in the container image to copy the file(s)

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

    """

    def __init__(self, **kwargs):
        """Initialize primitive"""

        #super(copy, self).__init__()

        self._app = kwargs.get('_app', '')  # Singularity specific
        self.__dest = kwargs.get('dest', '')
        self.__from = kwargs.get('_from', '')  # Docker specific
        self._mkdir = kwargs.get('_mkdir', '')  # Singularity specific
        self._post = kwargs.get('_post', '')  # Singularity specific
        self.__src = kwargs.get('src', '')

    def __str__(self):
        """String representation of the primitive"""
        if self.__dest and self.__src:
            if hpccm.config.g_ctype == container_type.DOCKER:
                if self._app:
                    logging.warning('The Singularity specific %app.. syntax '
                                    'was requested. Docker does not have an '
                                    'equivalent: using regular COPY!')

                # Format:
                # COPY src1 \
                #     src2 \
                #     src3 \
                #     dest/
                # COPY src dest
                c = ['COPY ']

                if self.__from:
                    c[0] = c[0] + '--from={} '.format(self.__from)

                if isinstance(self.__src, list):
                    c[0] = c[0] + self.__src[0]
                    c.extend(['    {}'.format(x) for x in self.__src[1:]])
                    # Docker requires a trailing slash.  Add one if missing.
                    c.append('    {}'.format(os.path.join(self.__dest, '')))
                else:
                    c[0] = c[0] + '{0} {1}'.format(self.__src, self.__dest)

                return ' \\\n'.join(c)
            if hpccm.config.g_ctype == container_type.SINGULARITY:
                # Format:
                # %files
                #     src1 dest
                #     src2 dest
                #     src3 dest
                if self.__from:
                    logging.warning('The Docker specific "COPY --from" '
                                    'syntax was requested.  Singularity does '
                                    'not have an equivalent, so this is '
                                    'probably not going to do what you want.')

                if self._mkdir and self._post:
                    logging.error('_mkdir and _post are mutually exclusive!')

                if self._app and (self._mkdir or self._post):
                    logging.error('_app cannot be used with _mkdir or _post!')

                if self._post and isinstance(self.__src, list):
                    logging.error('_post cannot be used with multiple files!')

                # Note: if the source is a file and the destination
                # path does not already exist in the container, this
                # will likely error.  Probably need a '%setup' step to
                # first create the directory.
                files_directive = '%files'
                if self._app:
                    files_directive = '%appfiles {0}'.format(self._app)
                if isinstance(self.__src, list):
                    multiple_files_str = '{0}\n'.format(files_directive) + '\n'.join(
                        ['    {0} {1}'.format(x, self.__dest)
                         for x in self.__src])
                    if self._mkdir:
                        return '%setup\n    mkdir -p ${{SINGULARITY_ROOTFS}}{0}\n{1}'.format(
                            self.__dest, multiple_files_str)
                    return multiple_files_str
                else:
                    single_file_str = '{0}\n    {1} {2}'.format(files_directive,
                                                                self.__src,
                                                                self.__dest)
                    if self._post:
                        basename = os.path.basename(self.__src)
                        return '%files\n    {0} /\n%post\n    mv /{1} {2}'.format(
                            self.__src,
                            basename,
                            self.__dest)
                    elif self._mkdir:
                        dirname = os.path.dirname(self.__dest)
                        return '%setup\n    mkdir -p ${{SINGULARITY_ROOTFS}}{0}\n{1}'.format(
                            dirname, single_file_str)
                    else:
                        return single_file_str
            else:
                raise RuntimeError('Unknown container type')
        else:
            return ''
