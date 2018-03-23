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

"""Test cases for the blob module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import os
import unittest

from hpccm.common import container_type
from hpccm.blob import blob

class Test_blob(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    def test_empty(self):
        """No blob specified"""
        b = blob()
        self.assertEqual(b.toString(container_type.DOCKER), '')

    def test_invalid_ctype(self):
        """Invalid container type specified"""
        b = blob()
        self.assertEqual(b.toString(None), '')

    def test_invalid_files(self):
        """Invalid file"""
        b = blob(docker='/path/to/nonexistent/file')
        self.assertEqual(b.toString(container_type.DOCKER), '')

    def test_docker_only(self):
        """Only Docker blob specified"""
        path = os.path.dirname(__file__)
        b = blob(docker=os.path.join(path, 'docker.blob'))
        self.assertEqual(b.toString(container_type.DOCKER),
                         'COPY foo bar\nRUN bar\n')
        self.assertEqual(b.toString(container_type.SINGULARITY), '')

    def test_singularity_only(self):
        """Only Singularity blob specified"""
        path = os.path.dirname(__file__)
        b = blob(singularity=os.path.join(path, 'singularity.blob'))
        self.assertEqual(b.toString(container_type.DOCKER), '')
        self.assertEqual(b.toString(container_type.SINGULARITY),
'''%files
    foo bar

%post
    bar
''')

    def test_all(self):
        """Both Docker and Singularity blobs specified"""
        path = os.path.dirname(__file__)
        b = blob(docker=os.path.join(path, 'docker.blob'),
                 singularity=os.path.join(path, 'singularity.blob'))
        self.assertEqual(b.toString(container_type.DOCKER),
                         'COPY foo bar\nRUN bar\n')
        self.assertEqual(b.toString(container_type.SINGULARITY),
'''%files
    foo bar

%post
    bar
''')
