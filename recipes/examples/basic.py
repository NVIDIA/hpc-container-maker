"""This example demonstrates recipe basics.

Usage:
$ hpccm.py --recipe recipes/examples/basic.py --format docker
# hpccm.py --recipe recipes/examples/basic.py --format singularity
"""

# Choose a base image
Stage0.baseimage('ubuntu:16.04')

# Install GNU compilers (upstream)
Stage0 += apt_get(ospackages=['gcc', 'g++', 'gfortran'])
