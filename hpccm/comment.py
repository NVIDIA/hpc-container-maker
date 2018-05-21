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

"""Comment primitive"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import logging  # pylint: disable=unused-import
import re
import textwrap

class comment(object):
    """Comment primitive"""

    def __init__(self, *args, **kwargs):
        """Initialize primitive"""

        #super(comment, self).__init__()

        try:
            self.__string = args[0]
        except IndexError:
            self.__string = ''

        self.__reformat = kwargs.get('reformat', True)

    def __str__(self):
        """String representation of the primitive"""
        if self.__string:
            # Comments are universal (so far...)
            if self.__reformat:
                # Wrap comments
                return textwrap.fill(self.__string, initial_indent='# ',
                                     subsequent_indent='# ', width=70)
            else:
                # Just prepend but otherwise apply no formatting
                return re.sub('^', '# ', self.__string, flags=re.MULTILINE)
        else:
            return ''
