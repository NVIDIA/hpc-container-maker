#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import argparse
import hpccm

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Jupyter notebook container generator')
    parser.add_argument('--format', type=str, default='docker',
                        choices=['docker', 'singularity'],
                        help='Container specification format (default: docker)')
    parser.add_argument('--image', type=str, default='ubuntu:18.04',
                        help='Base container image (default: ubuntu:18.04)')
    parser.add_argument('--notebook', required=True, type=str,
                        help='Jupyter notebook file')
    parser.add_argument('--requirements', type=str,
                        help='Python requirements file')
    args = parser.parse_args()

    ### Create Stage
    stage = hpccm.Stage()

    ### Base image
    stage += hpccm.primitives.baseimage(image=args.image, _docker_env=False)

    ### Install Python and Jupyter
    stage += hpccm.building_blocks.python(python2=False)
    stage += hpccm.building_blocks.pip(packages=['ipython', 'jupyter'],
                                       pip='pip3')
    stage += hpccm.primitives.environment(
        variables={'PYTHONIOENCODING': 'utf-8'}, _export=False)

    ### Make the port accessible (Docker only)
    stage += hpccm.primitives.raw(docker='EXPOSE 8888')

    if args.requirements:
        ### Install required packages
        stage += hpccm.primitives.copy(src=args.requirements,
                                       dest='/var/tmp/requirements.txt')
        stage += hpccm.primitives.shell(
            commands=['pip3 install -r /var/tmp/requirements.txt'])

    ### Add the notebook itself
    stage += hpccm.primitives.copy(src=args.notebook, dest='/notebook/',
                                   _mkdir=True)

    ### Run Jupyter
    stage += hpccm.primitives.runscript(
        commands=['jupyter notebook --no-browser --notebook-dir /notebook --allow-root'])

    ### Set container specification output format
    hpccm.config.set_container_format(args.format)

    ### Output container specification
    print(stage)

