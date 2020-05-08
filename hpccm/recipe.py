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

# pylint: disable=invalid-name, unused-import

"""Container recipe"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function
from six import raise_from

from distutils.version import StrictVersion
import logging
import os
import sys

import hpccm

import hpccm.config

from hpccm.common import container_type

from hpccm.Stage import Stage

from hpccm.building_blocks import *
from hpccm.primitives import *

def include(recipe_file, _globals=None, _locals=None, prepend_path=True,
            raise_exceptions=False):
    """Include a recipe file

    # Arguments

    recipe_file: path to a recipe file (required)

    _globals: a dictionary representing the global symbol table

    _locals: a dictionary representing the local symbol table

    prepend_path: If True, prepend the path of the main recipe to the
    recipe_file. If the recipe_file is an absolute path, then the path
    is not prepended regardless of the value of this parameter.

    raise_exceptions: If False, do not print stack traces when an
    exception is raised.  The default value is False.

    """

    if _locals is None:
        # caller's locals
        _locals = sys._getframe(1).f_locals
    if _globals is None:
        # caller's globals
        _globals = sys._getframe(1).f_globals

    # If a recipe file is included from another recipe file, some way
    # is needed to find the included recipe if it specified using a
    # relative path (relative to the including recipe file). Since
    # recipe files are exec'ed, the value of __file__ is this file,
    # not the recipe file. In order to make including recipes in other
    # recipes using relative paths more intuitive, prepend the path of
    # the base recipe file.
    if (prepend_path and hasattr(include, 'prepend_path')
        and not os.path.isabs(recipe_file)):
        recipe_file = os.path.join(include.prepend_path, recipe_file)

    try:
        with open(recipe_file) as f:
            # pylint: disable=exec-used
            exec(compile(f.read(), recipe_file, 'exec'), _globals, _locals)
    except Exception as e:
        if raise_exceptions:
            raise_from(e, e)
        else:
            logging.error(e)
            exit(1)

def recipe(recipe_file, ctype=container_type.DOCKER, raise_exceptions=False,
           single_stage=False, singularity_version='2.6', userarg=None):
    """Recipe builder

    # Arguments

    recipe_file: path to a recipe file (required).

    ctype: Enum representing the container specification format.  The
    default is `container_type.DOCKER`.

    raise_exceptions: If False, do not print stack traces when an
    exception is raised.  The default value is False.

    single_stage: If True, only print the first stage of a multi-stage
    recipe.  The default is False.

    singularity_version: Version of the Singularity definition file
    format to use.  Multi-stage support was added in version 3.2, but
    the changes are incompatible with earlier versions of Singularity.
    The default is '2.6'.

    userarg: A dictionary of key / value pairs provided to the recipe
    as the `USERARG` dictionary.

    """

    # Make user arguments available
    USERARG = {} # pylint: disable=unused-variable
    if userarg:
        USERARG = userarg # alias

    # Consider just 2 stages for the time being
    stages = [Stage(), Stage()]
    Stage0 = stages[0] # alias # pylint: disable=unused-variable
    Stage1 = stages[1] # alias # pylint: disable=unused-variable

    # Set the global container type
    hpccm.config.g_ctype = ctype

    # Set the global Singularity version
    hpccm.config.g_singularity_version = StrictVersion(singularity_version)

    # Any included recipes that are specified using relative paths will
    # need to prepend the path to the main recipe in order to be found.
    # Save the path to the main recipe.
    include.prepend_path = os.path.dirname(recipe_file)

    # Load in the recipe file
    include(recipe_file, _locals=locals(), _globals=globals(),
            prepend_path=False, raise_exceptions=raise_exceptions)

    # Only process the first stage of a recipe
    if single_stage:
        del stages[1:]
    elif len(Stage1) > 0:
        if (ctype == container_type.SINGULARITY and
            hpccm.config.g_singularity_version < StrictVersion('3.2')):
            # Singularity prior to version 3.2 did not support
            # multi-stage builds.  If the Singularity version is not
            # sufficient to support multi-stage, provide advice to
            # specify a sufficient Singularity version or disable
            # multi-stage.
            logging.warning('This looks like a multi-stage recipe. '
                            'Singularity 3.2 or later is required for '
                            'multi-stage builds.  Use '
                            '--singularity-version=3.2 to enable this '
                            'feature or --single-stage to get rid of this '
                            'warning.  Only processing the first stage...')
            del stages[1:]
        elif ctype == container_type.BASH:
            logging.warning('This looks like a multi-stage recipe, but '
                            'bash does not support multi-stage builds. '
                            'Use --single-stage to get rid of this warning. '
                            'Only processing the first stage...')
            del stages[1:]

    r = []
    for index, stage in enumerate(stages):
        if index >= 1:
            r.append('')
        r.append(str(stage))

    return '\n'.join(r)
