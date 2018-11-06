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

"""Test cases for the scif module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import tempfile
import unittest

import hpccm
from helpers import centos, docker

from hpccm.building_blocks.scif_app import scif_app

class Test_scif_app(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)
        hpccm.config.g_output_directory = tempfile.gettempdir()

    @docker
    def test_basic(self):
        """Basic scif app"""
        y = scif_app(
            name='foo',
            run='bar',
            install=['do x'],
            help='Help text',
            test='bar run tests')
        self.assertEqual(str(y),
r'''COPY {0}/foo.scif \
    /scif/recipes/
RUN scif install /scif/recipes/foo.scif'''.format(tempfile.gettempdir()))

        scif_file = open('{0}/foo.scif'.format(tempfile.gettempdir()), "r")
        self.assertEqual(scif_file.read(),
r'''%apphelp foo
    Help text
%appinstall foo
    do x
%apprun foo
    exec bar "$@"
%apptest foo
    bar run tests''')
        scif_file.close()
