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

from hpccm.baseimage import baseimage

class Stage(object):
    """Class for the container stage.  Docker may have one or more stages,
       Singularity will always have a single stage."""

    def __init__(self, **kwargs):
        """Initialize stage"""

        self.__layers = []
        self.name = kwargs.get('name', '')
        self.__separator = kwargs.get('separator', '\n\n')

    def __iadd__(self, layer):
        """Add the layer to the stage.  Allows "+=" syntax."""
        if isinstance(layer, list):
            self.__layers.extend(layer)
        else:
            self.__layers.append(layer)
        return self

    def __str__(self):
        """String representation of the stage"""
        return self.__separator.join(str(x) for x in self.__layers)

    def baseimage(self, image, _distro=''):
        """Insert the baseimage as the first layer"""
        if image:
            self.__layers.insert(0, baseimage(image=image, _as=self.name,
                                              _distro=_distro))

    def is_defined(self):
        """Return True if any layers have been defined, otherwise False"""
        return bool(self.__layers)
