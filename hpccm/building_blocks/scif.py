# Copyright (c) 2019, NVIDIA CORPORATION.  All rights reserved.
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

"""SCI-F building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import os
import posixpath

import hpccm.base_object
import hpccm.config

from hpccm.common import container_type
from hpccm.primitives.comment import comment
from hpccm.primitives.copy import copy
from hpccm.primitives.shell import shell

class scif(hpccm.base_object):
    """The `scif` building blocks installs components using the
    [Scientific Filesystem (SCI-F)](https://sci-f.github.io).

    Other building blocks and / or primitives should be added to
    the `scif` building block using the `+=` syntax.

    If not generating a Singularity definition file, SCI-F should be
    installed using the [`pip`](#pip) building block prior to this
    building block.

    If not generating a Singularity definition file, this module
    creates SCI-F recipe files in the current directory (see also the
    `file` parameter).

    # Parameters

    _arguments: Specify additional [Dockerfile RUN arguments](https://github.com/moby/buildkit/blob/master/frontend/dockerfile/docs/experimental.md) (Docker specific).

    _env: Boolean flag to specify whether the general container
    environment should be also be loaded when executing a SCI-F
    `%appinstall` block.  The default is False (Singularity specific).

    file: The SCI-F recipe file name.  The default value is the name
    parameter with the `.scif` suffix.

    name: The name to use to label the SCI-F application.  This
    parameter is required.

    _native: Boolean flag to specify whether to use the native
    Singularity support for SCI-F when generating Singularity
    definition files.  The default is True (Singularity specific).

    # Examples

    ```python
    pip(packages=['scif'])
    s = scif(name='example')
    s += openmpi(prefix='/scif/apps/example')
    s += shell(commands=[...])
    ```

    """

    __runtime_called = False

    def __init__(self, **kwargs):
        """Initialize scif building block"""

        super(scif, self).__init__(**kwargs)

        self.__appenv = []
        self.__appfiles = []
        self.__apphelp = []
        self.__appinstall = []
        self.__applabels = []
        self.__apprun = []
        self.__apptest = []
        self.__arguments = kwargs.get('_arguments')
        self.__env = kwargs.get('_env', False)
        self.__name = kwargs.get('name', None)
        if not self.__name:
            raise RuntimeError('"name" must be defined')
        self.__native = kwargs.get('_native', True)
        self.__scif_file = kwargs.get('file', '{}.scif'.format(self.__name))

    def __iadd__(self, item):
        """Add the item to the corresponding type list.  Allows "+=" syntax."""
        if isinstance(item, list):
            for i in item:
                self.__add(i)
        else:
            self.__add(item)
        return self

    def __add(self, item):
        """Break the item down into its constituent primitives and append each
        primitive to the appropriate list"""

        primitives = self.__primitives(item)
        for p in primitives:
            ptype = p.__class__.__name__
            if ptype == 'comment':
                self.__apphelp.append(p)
            elif ptype == 'copy':
                self.__appfiles.append(p)
            elif ptype == 'environment':
                self.__appenv.append(p)
            elif ptype == 'label':
                self.__applabels.append(p)
            elif ptype == 'runscript':
                self.__apprun.append(p)
            elif ptype == 'shell':
                if p._test:
                    self.__apptest.append(p)
                else:
                    self.__appinstall.append(p)
            else:
                raise RuntimeError('unrecognized primitive type: {}'.format(ptype))

    def __scif_recipe(self):
        """Generate the SCI-F recipe instructions, merging primitives of the
        same type because SCI-F does not support duplicate
        sections."""

        recipe = []

        if self.__appenv:
            appenv = self.__appenv[0].merge(self.__appenv,
                                            _app=self.__name)
            recipe.append(appenv)

        if self.__appfiles:
            appfiles = self.__appfiles[0].merge(self.__appfiles,
                                                _app=self.__name)
            recipe.append(appfiles)

        if self.__apphelp:
            apphelp = self.__apphelp[0].merge(self.__apphelp,
                                              _app=self.__name)
            recipe.append(apphelp)

        if self.__appinstall:
            appinstall = self.__appinstall[0].merge(self.__appinstall,
                                                    _app=self.__name,
                                                    _appenv=self.__env)
            recipe.append(appinstall)

        if self.__applabels:
            applabels = self.__applabels[0].merge(self.__applabels,
                                                  _app=self.__name)
            recipe.append(applabels)

        if self.__apprun:
            apprun = self.__apprun[0].merge(self.__apprun,
                                            _app=self.__name)
            recipe.append(apprun)

        if self.__apptest:
            apptest = self.__apptest[0].merge(self.__apptest,
                                              _app=self.__name, _test=True)
            recipe.append(apptest)

        return recipe

    def __primitives(self, item):
        """Item is a building block or a primitive.  A building block consists
        of one or more other building blocks or primitives.
        Ultimately, every building block consists of primitives.

        "Flatten" the item to a list of its constituent primitives.

        """
        return [i for i in self.__iter_flatten(item)]

    def __iter_flatten(self, iterable):
        """Recursively flatten"""
        try:
            for i in iter(iterable):
                for f in self.__iter_flatten(i):
                    yield f
        except TypeError:
            # not iterable
            yield iterable

    def __str__(self):
        """String representation of the building block"""

        scif_recipe = self.__scif_recipe()

        if (self.__native and
            hpccm.config.g_ctype == container_type.SINGULARITY):
            # Take advantage of Singularity's native support for SCI-F.
            return '\n'.join(str(x) for x in scif_recipe)
        else:
            # Generate an external SCI-F recipe file and manually call scif

            # Temporarily switch container format to Singularity to write
            # the SCI-F recipe file
            preserved_ctype = hpccm.config.g_ctype
            hpccm.config.set_container_format('singularity')

            logging.info('Writing {}'.format(self.__scif_file))
            with open(self.__scif_file, 'w') as f:
                f.write('\n\n'.join(str(x) for x in scif_recipe))

            # Restore original container format
            hpccm.config.g_ctype = preserved_ctype

            # Container instructions to copy the SCI-F recipe file
            # into the container and then run scif
            c_scif_file = posixpath.join('/scif/recipes',
                                         os.path.basename(self.__scif_file))
            instructions = []
            instructions.append(comment('SCI-F "{}"'.format(self.__name)))
            instructions.append(
                copy(src=self.__scif_file, dest=c_scif_file))
            instructions.append(
                shell(_arguments = self.__arguments,
                      chdir=False,
                      commands=['scif install {}'.format(c_scif_file)]))

            return '\n'.join(str(x) for x in instructions)

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        The entire `/scif` directory is copied into the runtime stage
        on the first call.  Subsequent calls do nothing.

        # Examples
        ```python
        s = scif(...)
        Stage0 += s
        Stage1 += s.runtime()
        ```

        """

        if not scif.__runtime_called:
            scif.__runtime_called = True
            return str(copy(_from=_from, src='/scif', dest='/scif'))
        else:
            return ''
