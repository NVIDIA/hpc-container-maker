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

"""Object base class"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

class base_object(object):
    """Object base class

    This base class is necessary for MRO inheritance to work.  The
    built-in `object` class initializer does not accept keyword
    arguments, so it must be called like `super().__init__()`.
    However, for building blocks to pass keyword arguments to
    templates, the template initializers must be called like
    `super().__init__(**kwargs)`.  There must be a base class at the
    bottom that only inherits from `object` and does not call
    `super()` with keyword arguments.

    """

    def __init__(self, **kwargs):
        """Initialize base class"""
        super(base_object, self).__init__()
