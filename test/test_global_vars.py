
from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest
import os

from helpers import docker, ubuntu

from hpccm.common import container_type
from hpccm.recipe import recipe

class Test_global_vars(unittest.TestCase):
    def test_global_vars(self):
        """Global variables"""
        path = os.path.dirname(__file__)
        rf = os.path.join(path, 'global_vars_recipe.py')
        try:
            recipe(rf, ctype=container_type.SINGULARITY, raise_exceptions=True)
        except Exception as e:
            self.fail(e)
