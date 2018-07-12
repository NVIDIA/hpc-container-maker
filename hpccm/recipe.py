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

import logging

import hpccm

import hpccm.config

from hpccm.common import container_type

from hpccm.Stage import Stage

# Primitives
from hpccm.primitives.baseimage import baseimage
from hpccm.primitives.blob import blob
from hpccm.primitives.comment import comment
from hpccm.primitives.copy import copy
from hpccm.primitives.environment import environment
from hpccm.primitives.label import label
from hpccm.primitives.raw import raw
from hpccm.primitives.shell import shell
from hpccm.primitives.workdir import workdir

# Building blocks
from hpccm.apt_get import apt_get
from hpccm.charm import charm
from hpccm.cmake import cmake
from hpccm.fftw import fftw
from hpccm.git import git
from hpccm.gnu import gnu
from hpccm.hdf5 import hdf5
from hpccm.intel_psxe import intel_psxe
from hpccm.mlnx_ofed import mlnx_ofed
from hpccm.mkl import mkl
from hpccm.mvapich2 import mvapich2
from hpccm.mvapich2_gdr import mvapich2_gdr
from hpccm.netcdf import netcdf
from hpccm.ofed import ofed
from hpccm.openmpi import openmpi
from hpccm.packages import packages
from hpccm.pgi import pgi
from hpccm.pnetcdf import pnetcdf
from hpccm.python import python
from hpccm.yum import yum

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
            raise_from(e, e)
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
