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

"""Documentation TBD"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import

from .baseimage import baseimage

class Stage(object):
    """Documentation TBD"""

    def __init__(self, **kwargs):
        """Documentation TBD"""

        self.__layers = []
        self.name = kwargs.get('name', '')
        self.__separator = kwargs.get('separator', '\n\n')

    def __iadd__(self, layer):
        """Documentation TBD"""
        if isinstance(layer, list):
            self.__layers.extend(layer)
        else:
            self.__layers.append(layer)
        return self

    def baseimage(self, image):
        """Documentation TBD"""
        if image:
            self.__layers.insert(0, baseimage(image=image, _as=self.name))

    def is_defined(self):
        """Documentation TBD"""
        if self.__layers:
            return True
        else:
            return False

    def toString(self, ctype):
        """Documentation TBD"""
        l = []
        for layer in self.__layers:
            l.append(layer.toString(ctype))

        return self.__separator.join(l)
