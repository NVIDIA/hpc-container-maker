"""
HPC Base image

Contents:
  CUDA version 9.0
  FFTW version 3.3.7
  HDF5 version 1.10.1
  Mellanox OFED version 3.4-1.0.0.0
  MVAPICH2 version 2.3b
  PGI compilers version 17.10
  Python 2 and 3 (upstream)
"""
# pylint: disable=invalid-name, undefined-variable, used-before-assignment

# The PGI End-User License Agreement (https://www.pgroup.com/doc/LICENSE)
# must be accepted.
pgi_eula=False
if USERARG.get('pgi_eula_accept', False):
  pgi_eula=True
else:
  raise RuntimeError('PGI EULA not accepted. To accept, use "--userarg pgi_eula_accept=yes"\nSee PGI EULA at https://www.pgroup.com/doc/LICENSE')

######
# Devel stage
######

Stage0 += comment(__doc__, reformat=False)

Stage0 += baseimage(image='nvidia/cuda:9.0-devel', _as='devel')

# Python (use upstream)
Stage0 += apt_get(ospackages=['python', 'python3'])

# PGI compilers
pgi = pgi(eula=pgi_eula, version='17.10')
Stage0 += pgi

# Setup the toolchain.  Use the PGI compiler toolchain as the basis.
tc = pgi.toolchain
tc.CUDA_HOME = '/usr/local/cuda'

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

# Python (use upstream)
Stage1 += apt_get(ospackages=['python', 'python3'])

# PGI compiler
Stage1 += pgi.runtime()

# Mellanox OFED
Stage1 += ofed.runtime()

# MVAPICH2
Stage1 += mv2.runtime()

# FFTW
Stage1 += fftw.runtime()

# HDF5
Stage1 += hdf5.runtime()
