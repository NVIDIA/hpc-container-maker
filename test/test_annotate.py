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

"""Test cases for the annotate module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from hpccm.templates.annotate import annotate

class Test_annotate(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    def test_no_annotations(self):
        """No variables specified"""
        a = annotate()

        self.assertDictEqual(a.annotate_step(), {})

    def test_no_base(self):
        """Basic annotations"""
        a = annotate(annotate=True, base_annotation=False)
        a.add_annotation('A', 'a')
        a.add_annotation('one', 1)

        self.assertDictEqual(a.annotate_step(), {'A': 'a', 'one': '1'})

    def test_default_base(self):
        """Basic annotations"""
        a = annotate(annotate=True, base_annotation=True)
        a.add_annotation('A', 'a')
        a.add_annotation('one', 1)

        self.assertDictEqual(a.annotate_step(), {'hpccm.annotate.A': 'a',
                                                 'hpccm.annotate.one': '1'})

    def test_custom_base(self):
        """Basic annotations"""
        a = annotate(annotate=True, base_annotation='foo')
        a.add_annotation('A', 'a')
        a.add_annotation('one', 1)

        self.assertDictEqual(a.annotate_step(), {'hpccm.foo.A': 'a',
                                                 'hpccm.foo.one': '1'})

    def test_no_annotations(self):
        """Basic annotations"""
        a = annotate(annotate=False)
        a.add_annotation('A', 'a')
        a.add_annotation('one', 1)

        self.assertDictEqual(a.annotate_step(), {})

