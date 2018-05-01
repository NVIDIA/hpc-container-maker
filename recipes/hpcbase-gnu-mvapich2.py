"""
HPC Base image

Contents:
  CUDA version 9.0
  FFTW version 3.3.7
  GNU compilers (upstream)
  HDF5 version 1.10.1
  Mellanox OFED version 3.4-1.0.0.0
  MVAPICH version 2.3b
  Python 2 and 3 (upstream)
"""
# pylint: disable=invalid-name, undefined-variable, used-before-assignment

######
# Devel stage
######

Stage0 += comment(__doc__, reformat=False)

Stage0 += baseimage(image='nvidia/cuda:9.0-devel', _as='devel')

# Python
python = python()
Stage0 += python

# Compilers (use upstream)
Stage0 += apt_get(ospackages=['gcc', 'g++', 'gfortran'])

# Create a toolchain
tc = hpccm.toolchain(CC='gcc', CXX='g++', F77='gfortran', F90='gfortran',
                     FC='gfortran', CUDA_HOME='/usr/local/cuda')

# Mellanox OFED
ofed = mlnx_ofed(version='3.4-1.0.0.0')
Stage0 += ofed

# MVAPICH2
mv2 = mvapich2(version='2.3b', toolchain=tc)
Stage0 += mv2

# FFTW
fftw = fftw(version='3.3.7', toolchain=tc)
Stage0 += fftw

# HDF5
hdf5 = hdf5(version='1.10.1', toolchain=tc)
Stage0 += hdf5

######
# Runtime image
######

Stage1 += baseimage(image='nvidia/cuda:9.0-runtime')

# Python
Stage1 += python.runtime()

# Compiler runtime (use upstream)
Stage1 += apt_get(ospackages=['libgfortran3', 'libgomp1'])

# Mellanox OFED
Stage1 += ofed.runtime()

# MVAPICH2
Stage1 += mv2.runtime()

# FFTW
Stage1 += fftw.runtime()

# HDF5
Stage1 += hdf5.runtime()
