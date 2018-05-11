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

# pylint: disable=invalid-name, too-few-public-methods, bad-continuation

"""Test cases for the python module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import centos, docker, ubuntu

from hpccm.python import python

class Test_python(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @ubuntu
    @docker
    def test_defaults_ubuntu(self):
        """Default python building block"""
        p = python()
        self.assertEqual(str(p),
r'''# Python
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        python \
        python3 && \
    rm -rf /var/lib/apt/lists/*''')

    @centos
    @docker
    def test_defaults_centos(self):
        """Default python building block"""
        p = python()
        self.assertEqual(str(p),
r'''# Python
RUN yum install -y epel-release && \
    yum install -y \
        python \
        python34 && \
    rm -rf /var/cache/yum/*''')

    @ubuntu
    @docker
    def test_runtime(self):
        """Runtime"""
        p = python()
        r = p.runtime()
        s = '\n'.join(str(x) for x in r)
        self.assertEqual(s,
r'''# Python
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        python \
        python3 && \
    rm -rf /var/lib/apt/lists/*''')
