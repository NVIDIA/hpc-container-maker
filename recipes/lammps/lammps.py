########
# LAMMPS recipe
#
# User arguments:
#  arch: x86_64 or aarch64 (default: x86_64) 
#  build_image
#  gdrcopy (default: 1.3)
#  gpu_arch: Pascal60, Volta70, or Turing75 (default: Volta70)
#  knem (default: 1.1.3)
#  lammps_version (default: patch_19Sep2019)
#  mlnx_ofed (default: 4.6-1.0.1.1)
#  ompi (default: 4.0.2)
#  qemu (default: False)
#  runtime_image
#  ucx (default: 1.6.1)
########

from distutils.version import StrictVersion
import hpccm.version

if StrictVersion(hpccm.__version__) < StrictVersion('19.11.0'):
  raise Exception('requires HPCCM version 19.11.0 or later')

# Use appropriate container base images based on the CPU architecture
arch = USERARG.get('arch', 'x86_64')
if arch == 'aarch64':
  # Early Access images - NGC registration required to use
  default_build_image = 'nvcr.io/ea-cuda-sc19/arm-partners/cuda-aarch64:10.2-devel-ubuntu18.04'
  default_runtime_image = 'nvcr.io/ea-cuda-sc19/arm-partners/cuda-aarch64:10.2-base-ubuntu18.04'
elif arch == 'x86_64':
  default_build_image = 'nvidia/cuda:10.1-devel-ubuntu18.04'
  default_runtime_image = 'nvidia/cuda:10.1-base-ubuntu18.04'
else:
  raise Exception('unrecognized architecture: {}'.format(arch))

########
# Build stage (Stage 0)
########

# Base image
Stage0 += baseimage(image=USERARG.get('build_image', default_build_image),
                    _arch=arch, _as='build')

if arch == 'aarch64' and USERARG.get('qemu', False):
  # Install QEMU emulator for aarch64 container image builds on x86 systems
  Stage0 += copy(_from='multiarch/qemu-user-static',
                 src='/usr/bin/qemu-aarch64-static', dest='/usr/bin')

# Base development environment
Stage0 += gnu(version='8')
Stage0 += cmake(eula=True)

# Communication stack: OpenMPI + UCX + KNEM + Mellanox OFED + gdrcopy
# (x86 only)
Stage0 += mlnx_ofed(version=USERARG.get('mlnx_ofed', '4.6-1.0.1.1'))

if hpccm.config.g_cpu_arch == hpccm.config.cpu_arch.X86_64:
    Stage0 += gdrcopy(ldconfig=True, version=USERARG.get('gdrcopy', '1.3'))

Stage0 += knem(ldconfig=True, version=USERARG.get('knem', '1.1.3'))

Stage0 += ucx(knem='/usr/local/knem', ldconfig=True,
              version=USERARG.get('ucx', '1.6.1'))

mpi = openmpi(ldconfig=True, version=USERARG.get('ompi', '4.0.2'),
              ucx='/usr/local/ucx')
Stage0 += mpi

########
# LAMMPS
########
gpu_arch = USERARG.get('gpu_arch', 'Volta70')
if gpu_arch not in ['Pascal60', 'Volta70', 'Turing75']:
  raise Exception('unrecognized GPU architecture: {}'.format(gpu_arch))

lammps_version = USERARG.get('lammps_version', 'patch_19Sep2019')
compute_capability = 'sm' + gpu_arch[-2:]
srcdir = '/var/tmp/lammps-{}'.format(lammps_version)

Stage0 += comment('LAMMPS version {0} for CUDA compute capability {1}'.format(
  lammps_version, compute_capability))

# LAMMPS dependencies
Stage0 += apt_get(ospackages=['bc', 'git', 'libgomp1', 'libhwloc-dev', 'make',
                              'tar', 'wget'])

# LAMMPS build
Stage0 += generic_cmake(
  build_directory='{0}/build-{1}'.format(srcdir, gpu_arch),
  cmake_opts=['-D BUILD_SHARED_LIBS=ON',
              '-D CUDA_USE_STATIC_CUDA_RUNTIME=OFF',
              '-D KOKKOS_ARCH={}'.format(gpu_arch),
              '-D CMAKE_BUILD_TYPE=Release',
              '-D MPI_C_COMPILER={}'.format(mpi.toolchain.CC),
              '-D BUILD_MPI=yes',
              '-D PKG_MPIIO=on',
              '-D BUILD_OMP=yes',
              '-D BUILD_LIB=no',
              '-D CMAKE_CXX_COMPILER={}/lib/kokkos/bin/nvcc_wrapper'.format(srcdir),
              '-D PKG_USER-REAXC=yes',
              '-D PKG_KSPACE=yes',
              '-D PKG_MOLECULE=yes',
              '-D PKG_REPLICA=yes',
              '-D PKG_RIGID=yes',
              '-D PKG_MISC=yes',
              '-D PKG_MANYBODY=yes',
              '-D PKG_ASPHERE=yes',
              '-D PKG_GPU=no',
              '-D PKG_KOKKOS=yes',
              '-D KOKKOS_ENABLE_CUDA=yes',
              '-D KOKKOS_ENABLE_HWLOC=yes'],
  directory='{}/cmake'.format(srcdir),
  # Force CUDA dynamic linking, see
  # https://github.com/openucx/ucx/wiki/NVIDIA-GPU-Support
  preconfigure=['sed -i \'s/^cuda_args=""/cuda_args="--cudart shared"/g\' {}/lib/kokkos/bin/nvcc_wrapper'.format(srcdir)],
  prefix='/usr/local/lammps-{}'.format(compute_capability),
  url='https://github.com/lammps/lammps/archive/{}.tar.gz'.format(lammps_version))

########
# Runtime stage (Stage 1)
########

Stage1 += baseimage(image=USERARG.get('runtime_image', default_runtime_image))

# Build stage runtime support + LAMMPS
Stage1 += Stage0.runtime()

########
# LAMMPS
########
Stage1 += environment(variables={
  'LD_LIBRARY_PATH': '/usr/local/lammps-{}/lib:$LD_LIBRARY_PATH'.format(
    compute_capability),
  'PATH': '/usr/local/lammps-{}/bin:$PATH'.format(compute_capability),
  # Workaround, see https://github.com/openucx/ucx/wiki/NVIDIA-GPU-Support
  'UCX_MEMTYPE_CACHE': 'n'})
