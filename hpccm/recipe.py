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
from hpccm.primitives.runscript import runscript
from hpccm.primitives.shell import shell
from hpccm.primitives.user import user
from hpccm.primitives.workdir import workdir

# Building blocks
from hpccm.building_blocks.apt_get import apt_get
from hpccm.building_blocks.boost import boost
from hpccm.building_blocks.cgns import cgns
from hpccm.building_blocks.charm import charm
from hpccm.building_blocks.cmake import cmake
from hpccm.building_blocks.fftw import fftw
from hpccm.building_blocks.gdrcopy import gdrcopy
from hpccm.building_blocks.gnu import gnu
from hpccm.building_blocks.hdf5 import hdf5
from hpccm.building_blocks.intel_mpi import intel_mpi
from hpccm.building_blocks.intel_psxe import intel_psxe
from hpccm.building_blocks.knem import knem
from hpccm.building_blocks.llvm import llvm
from hpccm.building_blocks.mlnx_ofed import mlnx_ofed
from hpccm.building_blocks.mkl import mkl
from hpccm.building_blocks.mvapich2 import mvapich2
from hpccm.building_blocks.mvapich2_gdr import mvapich2_gdr
from hpccm.building_blocks.netcdf import netcdf
from hpccm.building_blocks.ofed import ofed
from hpccm.building_blocks.openblas import openblas
from hpccm.building_blocks.openmpi import openmpi
from hpccm.building_blocks.packages import packages
from hpccm.building_blocks.pgi import pgi
from hpccm.building_blocks.pnetcdf import pnetcdf
from hpccm.building_blocks.python import python
from hpccm.building_blocks.ucx import ucx
from hpccm.building_blocks.xpmem import xpmem
from hpccm.building_blocks.yum import yum

def recipe(recipe_file, ctype=container_type.DOCKER, raise_exceptions=False,
           single_stage=False, userarg=None):
    """Recipe builder

    # Arguments

    recipe_file: path to a recipe file (required).

    ctype: Enum representing the container specification format.  The
    default is `container_type.DOCKER`.

    raise_exceptions: If False, do not print stack traces when an
    exception is raised.  The default value is False.

    single_stage: If True, only print the first stage of a multi-stage
    recipe.  The default is False.

    userarg: A dictionary of key / value pairs provided to the recipe
    as the `USERARG` dictionary.

    """

    # Make user arguments available
    USERARG = {} # pylint: disable=unused-variable
    if userarg:
        USERARG = userarg # alias

    # Consider just 2 stages for the time being
    stages = [Stage(name='stage0'), Stage()]
    Stage0 = stages[0] # alias # pylint: disable=unused-variable
    Stage1 = stages[1] # alias # pylint: disable=unused-variable

    # Set the global container type
    hpccm.config.g_ctype = ctype

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
