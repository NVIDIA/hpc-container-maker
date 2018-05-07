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

# pylint: disable=invalid-name

"""Container recipe"""

from __future__ import unicode_literals
from __future__ import print_function

import logging

import hpccm # pylint: disable=unused-import

import hpccm.config

from .common import container_type

from .Stage import Stage

from .apt_get import apt_get         # pylint: disable=unused-import
from .baseimage import baseimage     # pylint: disable=unused-import
from .blob import blob               # pylint: disable=unused-import
from .cmake import cmake             # pylint: disable=unused-import
from .comment import comment         # pylint: disable=unused-import
from .copy import copy               # pylint: disable=unused-import
from .environment import environment # pylint: disable=unused-import
from .fftw import fftw               # pylint: disable=unused-import
from .git import git                 # pylint: disable=unused-import
from .gnu import gnu                 # pylint: disable=unused-import
from .hdf5 import hdf5               # pylint: disable=unused-import
from .label import label             # pylint: disable=unused-import
from .mlnx_ofed import mlnx_ofed     # pylint: disable=unused-import
from .mvapich2 import mvapich2       # pylint: disable=unused-import
from .mvapich2_gdr import mvapich2_gdr # pylint: disable=unused-import
from .ofed import ofed               # pylint: disable=unused-import
from .openmpi import openmpi         # pylint: disable=unused-import
from .pgi import pgi                 # pylint: disable=unused-import
from .python import python           # pylint: disable=unused-import
from .raw import raw                 # pylint: disable=unused-import
from .shell import shell             # pylint: disable=unused-import
from .workdir import workdir         # pylint: disable=unused-import
from .yum import yum                 # pylint: disable=unused-import

def recipe(recipe_file, ctype=container_type.DOCKER, raise_exceptions=False,
           single_stage=False, userarg=None):
    """Recipe builder"""

    # Make user arguments available
    USERARG = {} # pylint: disable=unused-variable
    if userarg:
        USERARG = userarg # alias

    # Consider just 2 stages for the time being
    stages = [Stage(name='stage0'), Stage()]
    Stage0 = stages[0] # alias # pylint: disable=unused-variable
    Stage1 = stages[1] # alias # pylint: disable=unused-variable

    try:
        with open(recipe_file) as f:
            # pylint: disable=exec-used
            exec(compile(f.read(), recipe_file, 'exec'))
    except Exception as e:
        if raise_exceptions:
            raise e from e
        else:
            logging.error(e)
            exit(1)

    # Set the global container type
    hpccm.config.g_ctype = ctype

    # Only process the first stage of a recipe
    if single_stage:
        del stages[1:]
    else:
        # Singularity does not support multi-stage builds.  Ignore
        # anything beyond the first stage.
        if ctype == container_type.SINGULARITY and Stage1.is_defined():
            logging.warning('This looks like a multi-stage recipe, but '
                            'Singularity does not support multi-stage builds. '
                            'Use --single-stage to get rid of this warning. '
                            'Only processing the first stage...')
            del stages[1:]

    r = []
    for index, stage in enumerate(stages):
        if index >= 1:
            r.append('')
        r.append(str(stage))

    return '\n'.join(r)
