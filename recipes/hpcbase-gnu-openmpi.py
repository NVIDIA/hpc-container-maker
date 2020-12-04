"""
HPC Base image

Contents:
  CUDA version 10.1
  FFTW version 3.3.8
  GNU compilers (upstream)
  HDF5 version 1.10.5
  Mellanox OFED version 4.6-1.0.1.1
  OpenMPI version 4.0.2
  Python 2 and 3 (upstream)
"""
# pylint: disable=invalid-name, undefined-variable, used-before-assignment

# Choose between either Ubuntu 16.04 (default) or CentOS 7
# Add '--userarg centos=true' to the command line to select CentOS
devel_image = 'nvcr.io/nvidia/cuda:10.1-devel-ubuntu16.04'
runtime_image = 'nvcr.io/nvidia/cuda:10.1-runtime-ubuntu16.04'
if USERARG.get('centos', False):
    devel_image = 'nvcr.io/nvidia/cuda:10.1-devel-centos7'
    runtime_image = 'nvcr.io/nvidia/cuda:10.1-runtime-centos7'

######
# Devel stage
######

Stage0 += comment(__doc__, reformat=False)

Stage0 += baseimage(image=devel_image, _as='devel')

# Python
Stage0 += python()

# GNU compilers
compiler = gnu()
Stage0 += compiler

# Mellanox OFED
Stage0 += mlnx_ofed(version='4.6-1.0.1.1')

# OpenMPI
Stage0 += openmpi(version='4.0.2', toolchain=compiler.toolchain)

# FFTW
Stage0 += fftw(version='3.3.8', mpi=True, toolchain=compiler.toolchain)

# HDF5
Stage0 += hdf5(version='1.10.5', toolchain=compiler.toolchain)

######
# Runtime image
######

Stage1 += baseimage(image=runtime_image)

Stage1 += Stage0.runtime(_from='devel')
