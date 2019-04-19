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

"""Runscript primitive"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function
import shlex
from six.moves import shlex_quote

import logging # pylint: disable=unused-import

import hpccm.config

from hpccm.common import container_type

class runscript(object):
    """The `runscript` primitive specifies the commands to be invoked
    when the container starts.

    # Parameters

    _args: Boolean flag to specify whether `"$@"` should be appended
    to the command.  If more than one command is specified, nothing is
    appended regardless of the value of this flag.  The default is
    True (Singularity specific).

    _app: String containing the [SCI-F](https://www.sylabs.io/guides/2.6/user-guide/reproducible_scif_apps.html)
    identifier.  This also causes the Singularity block to named `%apprun`
    rather than `%runscript` (Singularity specific).

    commands: A list of commands to execute.  The default is an empty
    list.

    _exec: Boolean flag to specify whether `exec` should be inserted
    to preface the final command.  The default is True (Singularity
    specific).

    # Examples

    ```python
    runscript(commands=['cd /workdir', 'source env.sh'])
    ```

    ```python
    runscript(commands=['/usr/local/bin/entrypoint.sh'])
    ```

    """

    def __init__(self, **kwargs):
        """Initialize primitive"""

        #super(wget, self).__init__()

        self._args = kwargs.get('_args', True) # Singularity specific
        self._app = kwargs.get('_app', '') # Singularity specific
        self._exec = kwargs.get('_exec', True) # Singularity specific
        self.commands = kwargs.get('commands', [])

    def __str__(self):
        """String representation of the primitive"""
        if self.commands:
            if hpccm.config.g_ctype == container_type.DOCKER:
                if self._app:
                    logging.warning('The Singularity specific %app.. syntax was '
                                    'requested. Docker does not have an '
                                    'equivalent: using regular ENTRYPOINT!')

                if len(self.commands) > 1:
                    logging.warning('Multiple commands given to runscript. '
                                    'Docker ENTRYPOINT supports just one cmd: '
                                    'ignoring remaining commands!')
                # Format:
                # ENTRYPOINT ["cmd1", "arg1", "arg2", ...]
                s = []
                s.extend('"{}"'.format(shlex_quote(x))
                    for x in shlex.split(self.commands[0]))
                return 'ENTRYPOINT [' + ', '.join(s) + ']'

            elif hpccm.config.g_ctype == container_type.SINGULARITY:
                if self._exec:
                    # prepend last command with exec
                    self.commands[-1] = 'exec {0}'.format(self.commands[-1])
                if len(self.commands) == 1 and self._args:
                    # append "$@" to singleton command
                    self.commands[0] = '{} "$@"'.format(self.commands[0])
                # Format:
                # %runscript
                #     cmd1
                #     cmd2
                #     exec cmd3
                if self._app:
                    s = ['%apprun {0}'.format(self._app)]
                else:
                    s = ['%runscript']
                s.extend(['    {}'.format(x) for x in self.commands])
                return '\n'.join(s)
            elif hpccm.config.g_ctype == container_type.BASH:
                logging.warning('runscript primitive does not map into bash')
                return ''
            else:
                raise RuntimeError('Unknown container type')
        else:
            return ''

    def merge(self, lst, _app=None):
        """Merge one or more instances of the primitive into a single
        instance.  Due to conflicts or option differences the merged
        primitive may not be exact.

        """

        if not lst: # pragma: nocover
            raise RuntimeError('no items provided to merge')

        cmds = []
        for item in lst:
            if not item.__class__.__name__ == 'runscript': # pragma: nocover
                logging.warning('item is not the correct type, skipping...')
                continue

            cmds.extend(item.commands)

        return runscript(commands=cmds, _app=_app)
