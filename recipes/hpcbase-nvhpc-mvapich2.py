"""
HPC Base image

Contents:
  FFTW version 3.3.8
  HDF5 version 1.10.6
  Mellanox OFED version 5.0-2.1.8.0
  MVAPICH version 2.3.3
  NVIDIA HPC SDK version 20.7
  Python 2 and 3 (upstream)
"""
# pylint: disable=invalid-name, undefined-variable, used-before-assignment

# The NVIDIA HPC SDK End-User License Agreement must be accepted.
# https://docs.nvidia.com/hpc-sdk/eula
nvhpc_eula=False
if USERARG.get('nvhpc_eula_accept', False):
  nvhpc_eula=True
else:
  raise RuntimeError('NVIDIA HPC SDK EULA not accepted. To accept, use "--userarg nvhpc_eula_accept=yes"\nSee NVIDIA HPC SDK EULA at https://docs.nvidia.com/hpc-sdk/eula')

# Choose between either Ubuntu 18.04 (default) or CentOS 8
# Add '--userarg centos=true' to the command line to select CentOS
image = 'ubuntu:18.04'
if USERARG.get('centos', False):
  image = 'centos:8'

######
# Devel stage
######

Stage0 += comment(__doc__, reformat=False)

Stage0 += baseimage(image=image, _as='devel')

# Python
Stage0 += python()

# NVIDIA HPC SDK
compiler = nvhpc(eula=nvhpc_eula, mpi=False, redist=['compilers/lib/*'],
                 version='20.7')
Stage0 += compiler

# Mellanox OFED
Stage0 += mlnx_ofed(version='5.0-2.1.8.0')

# MVAPICH2
Stage0 += mvapich2(cuda=False, version='2.3.3', toolchain=compiler.toolchain)

# FFTW
Stage0 += fftw(version='3.3.8', mpi=True, toolchain=compiler.toolchain)

# HDF5
Stage0 += hdf5(version='1.10.6', toolchain=compiler.toolchain)

# nvidia-container-runtime
Stage0 += environment(variables={
  'NVIDIA_VISIBLE_DEVICES': 'all',
  'NVIDIA_DRIVER_CAPABILITIES': 'compute,utility',
  'NVIDIA_REQUIRE_CUDA': '"cuda>=10.1 brand=tesla,driver>=384,driver<385 brand=tesla,driver>=396,driver<397 brand=tesla,driver>=410,driver<411"'})

######
# Runtime image
######

Stage1 += baseimage(image=image)

Stage1 += Stage0.runtime(_from='devel')

# nvidia-container-runtime
Stage0 += environment(variables={
  'NVIDIA_VISIBLE_DEVICES': 'all',
  'NVIDIA_DRIVER_CAPABILITIES': 'compute,utility',
  'NVIDIA_REQUIRE_CUDA': '"cuda>=10.1 brand=tesla,driver>=384,driver<385 brand=tesla,driver>=396,driver<397 brand=tesla,driver>=410,driver<411"'})
