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

"""Container stage"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import

import hpccm.config

from hpccm.common import container_type
from hpccm.primitives.baseimage import baseimage

class Stage(object):
    """Class for container stages.

    Docker may have one or more stages,
       Singularity will always have a single stage.

    # Parameters

    name: Name to use when refering to the stage (Docker specific).
    The default is an empty string.

    separator: Separator to insert between stages.  The default is
    '\\n\\n'.

    """

    def __init__(self, **kwargs):
        """Initialize stage"""

        self.__layers = []
        self.name = kwargs.get('name', '')
        self.__separator = kwargs.get('separator', '\n\n')

    def __iadd__(self, layer):
        """Add the layer to the stage.  Allows "+=" syntax."""

        # The name of the stage should reflect the name the user
        # provided in the baseimage primitive (via the _as parameter).
        # This violates the encapsulation of the baseimage primitive.
        if layer.__class__.__name__ == 'baseimage' and not self.name:
          self.name = layer._baseimage__as

        if isinstance(layer, list):
            self.__layers.extend(layer)
        else:
            self.__layers.append(layer)
        return self

    def __len__(self):
        """Return number of layers"""
        return len(self.__layers)

    def __str__(self):
        """String representation of the stage"""
        return self.__separator.join(str(x) for x in self.__layers)

    def baseimage(self, image, _distro=''):
        """Insert the baseimage as the first layer

        # Arguments

        image (string): The image identifier to use as the base image.
        The value is passed to the `baseimage` primitive.

        _distro: The underlying Linux distribution of the base image.
        The value is passed to the `baseimage` primitive.
        """
        if image:
            self.__layers.insert(0, baseimage(image=image, _as=self.name,
                                              _distro=_distro))

    def runtime(self, _from=None, exclude=[]):
        """Generate the set of instructions to install the runtime specific
        components from a previous stage.

        This method invokes the runtime() method for every layer in
        the stage.  If a layer does not have a runtime() method, then
        it is skipped.

        # Arguments

        _from: The name of the stage from which to copy the runtime.
        The default is `0`.

        exclude: List of building blocks to exclude when generating
        the runtime. The default is an empty list.

        # Examples
        ```python
        Stage0 += baseimage(image='nvidia/cuda:9.0-devel')
        Stage0 += gnu()
        Stage0 += boost()
        Stage0 += ofed()
        Stage0 += openmpi()
        ...
        Stage1 += baseimage(image='nvidia/cuda:9.0-base')
        Stage1 += Stage0.runtime(exclude=['boost'])
        ```

        """

        # If the name of the stage is not explicitly specified, use
        # the name of the Stage if available, otherwise 0 (Docker's
        # default)
        if not _from and self.name:
            _from = self.name
        elif not _from:
            if hpccm.config.g_ctype == container_type.SINGULARITY:
                logging.warning('Multi-stage Singularity containers require a named first stage')
            _from = '0'

        instructions = []
        for layer in self.__layers:
            runtime = getattr(layer, 'runtime', None)
            if callable(runtime) and layer.__class__.__name__ not in exclude:
                inst = layer.runtime(_from=_from)
                if inst:
                    instructions.append(inst)

        return self.__separator.join(instructions)
