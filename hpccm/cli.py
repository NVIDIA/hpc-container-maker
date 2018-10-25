#!/usr/bin/env python3

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

# pylint: disable=invalid-name

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import argparse
import logging
import os

import hpccm

class KeyValue(argparse.Action): # pylint: disable=too-few-public-methods
    """Extend argparse to handle key value pair options"""
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        """Initializing custom action, i.e., call the base class init"""
        super(KeyValue, self).__init__(option_strings, dest, nargs, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        """Process key value pair arguments"""
        d = {}
        for kv in values:
            key, value = kv.split('=')
            d[key] = value
        setattr(namespace, self.dest, d)

def main(): # pragma: no cover
    parser = argparse.ArgumentParser(description='HPC Container Maker')
    parser.add_argument('--format', type=str, default='docker',
                        choices=[i.name.lower() for i in hpccm.container_type],
                        help='select container format')
    parser.add_argument('--print-exceptions', action='store_true',
                        default=False,
                        help='print exceptions (stack traces)')
    parser.add_argument('--single-stage', action='store_true', default=False,
                        help='only process the first stage of a multi-stage ' +
                        'recipe')
    parser.add_argument('--recipe', required=True,
                        help='generate a container spec for the RECIPE file')
    parser.add_argument('--userarg', action=KeyValue, metavar='key=value',
                        nargs='+', help='specify user parameters')
    parser.add_argument('--out', default=None, help='output directory' +
                        '(default: None)')
    args = parser.parse_args()

    # configure logger
    logging.basicConfig(format='%(levelname)s: %(message)s')

    if args.out:
        if not os.path.exists(args.out):
            os.makedirs(args.out)

    recipe = hpccm.recipe(args.recipe,
                          ctype=hpccm.container_type[args.format.upper()],
                          raise_exceptions=args.print_exceptions,
                          single_stage=args.single_stage,
                          userarg=args.userarg,
                          output_directory=args.out)
    print(recipe)

    if args.out:
        if args.format.upper() == 'DOCKER':
            def_filename = 'Dockerfile'
        else:
            def_filename = 'Singularity.def'

        def_file = open(os.path.join(args.out, def_filename), "w")
        def_file.write(recipe)
        def_file.close()

if __name__ == "__main__": # pragma: no cover
    main()
