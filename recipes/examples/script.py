#!/usr/bin/env python

"""This example demonstrates importing hpccm in a Python script.

Rather than using the hpccm command line tool to convert a recipe into
a container specification, import hpccm directly.

The script is responsible for handling user arguments, managing
layers, and printing the output.

Note: HPCCM must be installed via pip prior to using this script.

Usage:
$ python recipes/examples/script.py --help
$ python recipes/examples/script.py --linux ubuntu
$ python recipes/examples/script.py --format singularity

"""

from __future__ import unicode_literals
from __future__ import print_function

import argparse
import hpccm

### Parse command line arguments
parser = argparse.ArgumentParser(description='HPCCM example')
parser.add_argument('--compiler', type=str, default='gnu',
                    choices=['gnu', 'llvm', 'pgi'],
                    help='Compiler choice (default: gnu)')
parser.add_argument('--format', type=str, default='docker',
                    choices=['docker', 'singularity'],
                    help='Container specification format (default: docker)')
parser.add_argument('--linux', type=str, default='centos',
                    choices=['centos', 'ubuntu'],
                    help='Linux distribution choice (default: centos)')
parser.add_argument('--pgi_eula_accept', action='store_true',
                    default=False,
                    help='Accept PGI EULA (default: false)')
args = parser.parse_args()

### Create Stage
Stage0 = hpccm.Stage()

### Linux distribution
if args.linux == 'centos':
    Stage0 += hpccm.primitives.baseimage(image='centos:7')
elif args.linux == 'ubuntu':
    Stage0 += hpccm.primitives.baseimage(image='ubuntu:16.04')

### Compiler
if args.compiler == 'gnu':
    Stage0 += hpccm.building_blocks.gnu()
elif args.compiler == 'llvm':
    Stage0 += hpccm.building_blocks.llvm()
elif args.compiler == 'pgi':
    if not args.pgi_eula_accept:
        print('PGI EULA not accepted. To accept, use "--pgi_eula_accept".\n'
              'See PGI EULA at https://www.pgroup.com/doc/LICENSE')
        exit(1)
    Stage0 += hpccm.building_blocks.pgi(eula=args.pgi_eula_accept)

### Set container specification output format
hpccm.config.set_container_format(args.format)

### Output container specification
print(Stage0)
