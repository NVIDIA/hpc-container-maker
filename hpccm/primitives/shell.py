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

"""Shell primitive"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import

import hpccm.config

from hpccm.common import container_type

class shell(object):
    """The `shell` primitive specifies a series of shell commands to
    execute.

    # Parameters

    _app: String containing the [SCI-F](https://www.sylabs.io/guides/2.6/user-guide/reproducible_scif_apps.html)
    identifier.  This also causes the Singularity block to named
    `%appinstall` rather than `%post` (Singularity specific).

    _appenv: Boolean flag to specify whether the general container
    environment should be also be loaded when executing a SCI-F
    `%appinstall` block.  The default is False.

    _arguments: Specify additional [Dockerfile RUN arguments](https://github.com/moby/buildkit/blob/master/frontend/dockerfile/docs/experimental.md) (Docker specific).

    chdir: Boolean flag to specify whether to change the working
    directory to `/` before executing any commands.  Docker
    automatically resets the working directory for each `RUN`
    instruction.  Setting this option to True makes Singularity behave
    the same.  This option is ignored for Docker.  The default is
    True.

    commands: A list of commands to execute.  The default is an empty
    list.

    _test: Boolean flag to specify whether to use `%test` instead of
    `%post` and `%apptest` instead of `%appinstall` as the Singularity
    section headings (Singularity specific).

    # Examples

    ```python
    shell(commands=['cd /path/to/src', './configure', 'make install'])
    ```

    ```python
    # Cache Go packages
    shell(_arguments=['--mount=type=cache,target=/root/.cache/go-build']
          commands=['cd /path/to/go-src', 'go build'])
    ```

    """

    def __init__(self, **kwargs):
        """Initialize primitive"""

        #super(wget, self).__init__()

        self._app = kwargs.get('_app', '') # Singularity specific
        self._appenv = kwargs.get('_appenv', False) # Singularity specific
        self._arguments = kwargs.get('_arguments', '') # Docker specific
        self.chdir = kwargs.get('chdir', True)
        self.commands = kwargs.get('commands', [])
        self._test = kwargs.get('_test', False) # Singularity specific

    def __str__(self):
        """String representation of the primitive"""
        if self.commands:
            # Remove empty items from the list of commands
            self.commands = [x for x in self.commands if x]

            if hpccm.config.g_ctype == container_type.DOCKER:
                if self._app:
                    logging.warning('The Singularity specific %app.. syntax '
                                    'was requested. Docker does not have an '
                                    'equivalent: using regular RUN!')

                if self._appenv:
                    logging.warning('The Singularity specific _appenv argument '
                                    'was given: ignoring argument!')
                # Format:
                # RUN cmd1 && \
                #     cmd2 && \
                #     cmd3
                s = ['RUN ']
                if self._arguments:
                    s[0] += self._arguments + ' '
                s[0] += self.commands[0]
                s.extend(['    {}'.format(x) for x in self.commands[1:]])
                return ' && \\\n'.join(s)
            elif hpccm.config.g_ctype == container_type.SINGULARITY:
                if self._arguments:
                    logging.warning('The Docker specific _arguments was given: '
                                    'ignoring statement!')
                # Format:
                # %post [OR %appinstall app_name]
                #     cmd1
                #     cmd2
                #     cmd3
                if self._app:
                    s = ['%appinstall {0}'.format(self._app)]
                    if self._test:
                        s = ['%apptest {0}'.format(self._app)]
                    # Do not `cd /` here: Singularity %appinstall is already
                    # run in its own working directory at /scif/apps/[appname].

                    # %appinstall commands do not run in regular Singularity
                    # environment. If _appenv=True load environment.
                    if self._appenv:
                        s.append('    for f in /.singularity.d/env/*; do . $f; '
                                 'done')
                else:
                    if self._appenv:
                        logging.warning('The _appenv argument has to be used '
                                        'together with the _app argument: '
                                        'ignoring argument!')
                    s = ['%post']
                    if self._test:
                        s = ['%test']
                    # For consistency with Docker. Docker resets the
                    # working directory to '/' at the beginning of each
                    # 'RUN' instruction.
                    if self.chdir:
                        s.append('    cd /')

                s.extend(['    {}'.format(x) for x in self.commands])
                return '\n'.join(s)
            elif hpccm.config.g_ctype == container_type.BASH:
                s = []
                if self.chdir:
                    s.insert(0, 'cd /')
                s.extend(self.commands)
                return '\n'.join(s)
            else:
                raise RuntimeError('Unknown container type')
        else:
            return ''

    def merge(self, lst, _app=None, _appenv=False, _test=False):
        """Merge one or more instances of the primitive into a single
        instance.  Due to conflicts or option differences the merged
        primitive may not be exact merger.

        """

        if not lst: # pragma: nocover
            raise RuntimeError('no items provided to merge')

        cmds = []
        for item in lst:
            if not item.__class__.__name__ == 'shell': # pragma: nocover
                logging.warning('item is not the correct type, skipping...')
                continue

            cmds.extend(item.commands)

        return shell(commands=cmds, _app=_app, _appenv=_appenv, _test=_test)
