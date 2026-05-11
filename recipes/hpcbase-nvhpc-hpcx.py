"""
HPC Base image

Contents:
  FFTW
  HDF5
  NetCDF
  NVIDIA HPC SDK (CUDA, HPC-X, NVIDIA HPC Compilers)
  + typical development environment

  Use --userarg nvhpc_version=X.Y and/or --userarg distro=<value> to
  alter the defaults, where X.Y.Z is 26.3, for instance, and the distro
  value is ubuntu24.04 or rockylinux9. 
"""

nvhpc_version = USERARG.get('nvhpc_version', '26.3')
distro = USERARG.get('distro', 'ubuntu24.04')

Stage0 += comment(__doc__, reformat=False)

Stage0 += baseimage(image='nvcr.io/nvidia/nvhpc:{0}-devel-cuda_multi-{1}'.format(nvhpc_version, distro), _as='devel')

# Create compiler toolchain
tc = hpccm.toolchain(CC='nvc', CXX='nvc++', F77='nvfortran', F90='nvfortran',
                     FC='nvfortran')

# FFTW
Stage0 += fftw(version='3.3.10', mpi=True, toolchain=tc, annotate=True)

# HDF5
# Disable float16 to workaround missing intrinsics in older Linux
# distributions / GCC versions
Stage0 += hdf5(version='1.14.5', toolchain=tc, annotate=True,
               enable_nonstandard_feature_float16='no')

# NetCDF
Stage0 += netcdf(version='4.9.2', version_cxx='4.3.1', version_fortran='4.6.1',
                 toolchain=tc, annotate=True)
