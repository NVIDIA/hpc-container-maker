# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
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

"""annotate template"""

from shlex import quote as shlex_quote

import hpccm.base_object

class annotate(hpccm.base_object):
    """Template for setting annotations"""

    def __init__(self, **kwargs):
        """Initialize template"""

        super(annotate, self).__init__(**kwargs)

        self.annotate = kwargs.get('annotate', False)
        self.base_annotation = kwargs.get('base_annotation', True)
        self.__labels = {}

    def add_annotation(self, key, value):
        if isinstance(self.base_annotation, str):
            key = 'hpccm.' + self.base_annotation + '.' + key
        elif self.base_annotation:
            key = 'hpccm.' + self.__class__.__name__ + '.' + key

        self.__labels[key] = shlex_quote(str(value))

    def annotate_step(self):
        """Return dictionary of annotations"""

        if self.annotate:
            return self.__labels
        else:
            return {}
