#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Setup script for hpccm."""

import os

from setuptools import find_packages
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
with open(os.path.join(here, 'README.md'), encoding='utf-8') as fp:
    long_description = fp.read()

setup(
    name='hpccm',
    version='',
    description='HPC Container Maker',
    long_description=long_description,
    packages=find_packages(),
    # Make hpccm.hpccm.main available from the command line as `hpccm`.
    install_requires=['enum34', 'six'],
    entry_points={
        'console_scripts': [
            'hpccm=hpccm.hpccm:main']})
