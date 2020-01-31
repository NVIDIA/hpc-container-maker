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

"""environment variables template"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import hpccm.base_object

class envvars(hpccm.base_object):
    """Template for setting environment variables"""

    def __init__(self, **kwargs):
        """Initialize template"""

        super(envvars, self).__init__(**kwargs)

        self.environment = kwargs.get('environment', True)
        self.environment_variables = {}
        # Use only if the runtime environment is incompatible with the
        # non-runtime environment, e.g., PATH contains different
        # values.  Otherwise, try to use the filtering options.
        self.runtime_environment_variables = {}

    def environment_step(self, include_only=None, exclude=None, runtime=False):
        """Return dictionary of environment variables"""

        if runtime:
            e = self.runtime_environment_variables
        else:
            e = self.environment_variables

        if self.environment:
            if include_only:
                return {x: e[x] for x in e if x in include_only}
            elif exclude:
                return {x: e[x] for x in e if x not in exclude}
            else:
                return e
        else:
            return {}
