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

from helpers import centos, docker, singularity

from hpccm.building_blocks.scif import scif
from hpccm.building_blocks.packages import packages
from hpccm.primitives.copy import copy
from hpccm.primitives.environment import environment
from hpccm.primitives.label import label
from hpccm.primitives.shell import shell
from hpccm.primitives.runscript import runscript

import hpccm

class Test_scif(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)
        hpccm.config.g_output_directory = tempfile.gettempdir()

    @centos
    @docker
    def test_basic(self):
        """Basic scif app with initialization"""
        app = scif(name="foo")
        # app += packages(ospackages=['gcc']) # not possible
        app += shell(commands=['do x'])
        app += runscript(commands=['foo'])
        self.assertEqual(str(app),
r'''# SCIF app foo
# Begin SCI-F installtion
RUN yum install -y \
        python-pip \
        python-setuptools && \
    rm -rf /var/cache/yum/*
RUN pip install wheel && \
    pip install scif==0.0.76
# End SCI-F installtion
COPY {0}/foo.scif \
    /scif/recipes/
RUN scif install /scif/recipes/foo.scif'''.format(tempfile.gettempdir()))

        scif_file = open('{0}/foo.scif'.format(tempfile.gettempdir()), "r")
        self.assertEqual(scif_file.read(),
r'''%appinstall foo
    do x

%apprun foo
    exec foo''')
        scif_file.close()

    @docker
    def test_basic_second_app(self):
        """Basic decond scif app without initialization"""
        app = scif(name="bar")
        app += shell(commands=['do y'])
        app += runscript(commands=['bar'])
        self.assertEqual(str(app),
r'''# SCIF app bar
COPY {0}/bar.scif \
    /scif/recipes/
RUN scif install /scif/recipes/bar.scif'''.format(tempfile.gettempdir()))

        scif_file = open('{0}/bar.scif'.format(tempfile.gettempdir()), "r")
        self.assertEqual(scif_file.read(),
r'''%appinstall bar
    do y

%apprun bar
    exec bar''')
        scif_file.close()

    @singularity
    def test_basic_app_singularity(self):
        app = scif(name="bar")
        app += shell(commands=['gcc bar.c'])
        app += runscript(commands=['bar'])
        app += environment(variables={'BAR_VAR': 1})
        app += copy(src='a', dest='/opt/a')
        app += label(metadata={'ONE': 1})
        self.assertEqual(str(app),
r'''# SCIF app bar
%appinstall bar
    gcc bar.c

%apprun bar
    exec bar

%appenv bar
    export BAR_VAR=1

%appfiles bar
    a /opt/a

%applabels bar
    ONE 1''')

    @singularity
    def test_basic_app_list_singularity(self):
        app = scif(name="bar")
        app += [
            shell(commands=['gcc bar.c']),
            runscript(commands=['bar'])
        ]
        self.assertEqual(str(app),
r'''# SCIF app bar
%appinstall bar
    gcc bar.c

%apprun bar
    exec bar''')

