#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup script for hpccm."""

import os

from setuptools import find_packages
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

# Get the package version from hpccm/version.py
version = {}
with open(os.path.join(here, 'hpccm', 'version.py')) as fp:
    exec(fp.read(), version)

# Get the long description from the README file
with open(os.path.join(here, 'README.md')) as fp:
    long_description = fp.read()

setup(
    name='hpccm',
    version=version['__version__'],
    description='HPC Container Maker',
    long_description=long_description,
    long_description_content_type='text/markdown',
    maintainer='Scott McMillan',
    maintainer_email='smcmillan@nvidia.com',
    license='Apache License Version 2.0',
    url='https://github.com/NVIDIA/hpc-container-maker',
    packages=find_packages(),
    classifiers=[
      "License :: OSI Approved :: Apache Software License",
      "Programming Language :: Python :: 2",
      "Programming Language :: Python :: 2.7",
      "Programming Language :: Python :: 3",
      "Programming Language :: Python :: 3.4",
      "Programming Language :: Python :: 3.5",
      "Programming Language :: Python :: 3.6"
    ],
    # Make hpccm.cli.main available from the command line as `hpccm`.
    install_requires=['enum34', 'six'],
    entry_points={
        'console_scripts': [
            'hpccm=hpccm.cli:main']})
