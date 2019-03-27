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

# pylint: disable=invalid-name, too-few-public-methods, bad-continuation

"""Test cases for the scif module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import os
import tempfile
import unittest

from helpers import centos, docker, singularity

from hpccm.building_blocks.python import python
from hpccm.building_blocks.scif import scif

from hpccm.primitives.copy import copy
from hpccm.primitives.comment import comment
from hpccm.primitives.environment import environment
from hpccm.primitives.label import label
from hpccm.primitives.runscript import runscript
from hpccm.primitives.shell import shell

class Test_scif(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @docker
    def test_noname_docker(self):
        """Default scif building block, no name"""
        with self.assertRaises(RuntimeError):
            scif()

    @docker
    def test_defaults_docker(self):
        """Default scif building block"""
        # The scif module generates a SCI-F recipe file.  Use a
        # temporary file location for it rather than polluting the
        # test environment.  This is slightly unrealistic since the
        # Docker build would fail since the file is outside the Docker
        # build environment, but go with it.
        scif_file = tempfile.NamedTemporaryFile(delete=False, suffix='.scif')
        s = scif(name='foo', file=scif_file.name)
        self.assertEqual(str(s),
r'''# SCI-F "foo"
COPY {0} /scif/recipes/{1}
RUN scif install /scif/recipes/{1}'''.format(scif_file.name,
                                             os.path.basename(scif_file.name)))
        os.unlink(scif_file.name)

    @singularity
    def test_defaults_singularity(self):
        """Default scif building block"""
        s = scif(name='foo')
        self.assertEqual(str(s), '%apprun foo\n    eval "if [[ $# -eq 0 ]]; then exec /bin/bash; else exec $@; fi"')

    @singularity
    def test_allsections_singularity(self):
        """One of each SCI-f section type"""
        s = scif(name='foo')
        s += copy(src='file', dest='/tmp/file')
        s += comment('My app')
        s += environment(variables={'ONE': '1'})
        s += label(metadata={'A': 'B'})
        s += runscript(commands=['default_program'])
        s += shell(commands=['build_cmds'])
        s += shell(commands=['test_program'], _test=True)
        self.assertEqual(str(s), 
r'''%appenv foo
    export ONE=1
%appfiles foo
    file /tmp/file
%apphelp foo
My app
%appinstall foo
    for f in /.singularity.d/env/*; do . $f; done
    build_cmds
%applabels foo
    A B
%apprun foo
    exec default_program "$@"
%apptest foo
    test_program''')

    @docker
    def test_allsections_docker(self):
        """One of each SCI-f section type"""
        # See comment in the test_defaults_docker test case
        scif_file = tempfile.NamedTemporaryFile(delete=False, suffix='.scif')
        s = scif(name='foo', file=scif_file.name)
        s += copy(src='file', dest='/tmp/file')
        s += comment('My app')
        s += environment(variables={'ONE': '1'})
        s += label(metadata={'A': 'B'})
        s += runscript(commands=['default_program'])
        s += shell(commands=['build_cmds'])
        s += shell(commands=['test_program'], _test=True)

        str(s) # Force writing the SCI-F recipe file

        # slurp file content
        with open(scif_file.name) as f:
            content = f.read()
        os.unlink(scif_file.name)
        
        self.assertEqual(content,
r'''%appenv foo
    export ONE=1

%appfiles foo
    file /tmp/file

%apphelp foo
My app

%appinstall foo
    build_cmds

%applabels foo
    A B

%apprun foo
    exec default_program "$@"

%apptest foo
    test_program''')

    @centos
    @singularity
    def test_building_block_singularity(self):
        """test building block"""
        s = scif(name='foo')
        s += [python()] # list not required, but tests a code branch
        self.assertEqual(str(s),
r'''%apphelp foo
Python
%appinstall foo
    for f in /.singularity.d/env/*; do . $f; done
    yum install -y epel-release
    yum install -y \
        python \
        python34
    rm -rf /var/cache/yum/*
%apprun foo
    eval "if [[ $# -eq 0 ]]; then exec /bin/bash; else exec $@; fi"''')

    @docker
    def test_runtime(self):
        """Runtime"""
        s = scif(name='foo')
        r = s.runtime()
        self.assertEqual(r, 'COPY --from=0 /scif /scif')
