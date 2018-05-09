"""This example demonstrates user arguments.

The CUDA and OpenMPI versions can be specified on the command line.  If
they are not, then reasonable defaults are used.

Note: no validation is performed on the user supplied information.

Usage:
$ hpccm.py --recipe recipes/examples/userargs.py --userarg cuda=9.0 ompi=2.1.2
"""

# Set the image tag based on the specified version (default to 9.1)
cuda_version = USERARG.get('cuda', '9.1')
image = 'nvidia/cuda:{}-devel-ubuntu16.04'.format(cuda_version)

Stage0.baseimage(image)

# Set the OpenMPI version based on the specified version (default to 3.0.0)
ompi_version = USERARG.get('ompi', '3.0.0')
ompi = openmpi(infiniband=False, version=ompi_version)

Stage0 += ompi
