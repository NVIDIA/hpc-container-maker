"""
HPC Base image

Contents:
  CUDA
  FFTW
  GNU compilers
  HDF5
  HPC-X (Open MPI, UCX, etc.)
  NetCDF
  + typical development environment

  Use --userarg cuda_version=X.Y.Z and/or --userarg distro=<value> to
  alter the defaults, where X.Y.Z is 13.2.0, for instance, and the distro
  value is ubuntu24.04 or rockylinux9. 
"""

cuda_version = USERARG.get('cuda_version', '13.2.0')
distro = USERARG.get('distro', 'ubuntu24.04')
runtime = USERARG.get('runtime', False)

######
# Devel stage
######

Stage0 += comment(__doc__, reformat=False)

Stage0 += baseimage(image='nvcr.io/nvidia/cuda:{0}-devel-{1}'.format(cuda_version, distro), _as='devel')

# Typical development environment
common_packages = ['automake', 'autoconf', 'autoconf-archive', 'binutils',
                   'bzip2', 'ca-certificates', 'cmake', 'diffutils', 'file',
                   'gdb', 'git', 'gzip', 'libtool', 'make', 'numactl', 'patch',
                   'tar', 'vim', 'wget']
Stage0 += packages(apt=common_packages + ['libaec-dev', 'libnuma-dev',
                                          'libsz2', 'lmod', 'xz-utils',
                                          'zlib1g-dev'],
                   epel=True,
                   powertools=True if distro == 'rockylinux8' else False,
                   yum=common_packages + ['Lmod', 'libaec-devel',
                                          'numactl-devel', 'xz', 'zlib-devel'])

# GNU compilers
compiler = gnu()
Stage0 += compiler

# OFED
Stage0 += ofed()

# gdrcopy
Stage0 += gdrcopy(ldconfig=True, version='2.4.2', annotate=True)

# HPC-X 
Stage0 += hpcx(version='2.25.1', hpcxinit=False, inbox=True, ldconfig=True)

# FFTW
Stage0 += fftw(version='3.3.10', mpi=True, toolchain=compiler.toolchain,
               annotate=True)

# HDF5
Stage0 += hdf5(version='1.14.5', toolchain=compiler.toolchain, annotate=True)

# NetCDF
Stage0 += netcdf(version='4.9.2', version_cxx='4.3.1', version_fortran='4.6.1',
                 toolchain=compiler.toolchain, annotate=True)

######
# Runtime image
######

if runtime:
  Stage1 += baseimage(image='nvcr.io/nvidia/cuda:{0}-runtime-{1}'.format(cuda_version, distro))

  Stage1 += Stage0.runtime(_from='devel')
