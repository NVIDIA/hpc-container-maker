"""
MPI Bandwidth

Contents:
  CentOS 7
  GNU compilers (upstream)
  Mellanox OFED
  OpenMPI version 3.0.0
"""

Stage0 += comment(__doc__, reformat=False)

# CentOS base image
Stage0 += baseimage(image='centos:7')

# GNU compilers
Stage0 += gnu(fortran=False)

# Mellanox OFED
Stage0 += mlnx_ofed()

# OpenMPI
Stage0 += openmpi(cuda=False, version='3.0.0')

# MPI Bandwidth
Stage0 += shell(commands=[
    'wget -q -nc --no-check-certificate -P /var/tmp https://computing.llnl.gov/tutorials/mpi/samples/C/mpi_bandwidth.c',
    'mpicc -o /usr/local/bin/mpi_bandwidth /var/tmp/mpi_bandwidth.c'])
