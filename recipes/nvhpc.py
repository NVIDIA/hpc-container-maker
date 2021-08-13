"""
Recipe for a NVIDIA HPC SDK container and typical development environment.

$ hpccm --recipe nvhpc.py --userarg eula=yes

$ hpccm --recipe nvhpc.py --userarg eula=yes cuda_multi=no arch=x86_64
"""
from distutils.version import StrictVersion
import platform

# Verify correct version of HPCCM is used
if StrictVersion(hpccm.__version__) < StrictVersion('21.7.0'):
  raise RuntimeError('requires HPCCM version 21.7.0 or later')

arch = USERARG.get('arch', platform.machine())
image = USERARG.get('image', 'ubuntu:20.04')
version = USERARG.get('version', '21.7')
release = '20' + version[:2]
default_cuda = '11.4'

cuda_multi=True
if USERARG.get('cuda_multi', False) in [0, '0', 'no', 'false']:
  cuda_multi=False

# The NVIDIA HPC SDK End-User License Agreement must be accepted.
# https://docs.nvidia.com/hpc-sdk/eula
eula=False
if USERARG.get('eula', False) in [1, '1', 'yes', 'true']:
    eula=True
else:
    raise RuntimeError('NVIDIA HPC SDK EULA not accepted. To accept, use "--userarg eula=yes"\nSee NVIDIA HPC SDK EULA at https://docs.nvidia.com/hpc-sdk/eula')

if cuda_multi is True:
    # CUDA 10.2, 11.0, 11.4
    cuda_driver = '"cuda>=10.2"'
else:
    # CUDA 11.4 only, but enhanced forward compatibility means 11.2 is
    # sufficient
    cuda_driver = '"cuda>=11.2"'

Stage0 += baseimage(image=image, _arch=arch)

# Typical development environment
common_packages = ['automake', 'autoconf', 'autoconf-archive', 'binutils',
                   'bzip2', 'ca-certificates', 'cmake', 'diffutils', 'file',
                   'gdb', 'git', 'gzip', 'libtool', 'make', 'patch', 'tar',
                   'vim', 'wget']
Stage0 += packages(apt=common_packages + ['libaec-dev', 'libncursesw5',
                                          'libsz2', 'libtinfo5', 'lmod',
                                          'xz-utils', 'zlib1g-dev'],
                   epel=True,
                   yum=common_packages + ['Lmod', 'libaec-devel', 'xz',
                                          'zlib-devel'])

# Mellanox OFED
Stage0 += mlnx_ofed(version='5.2-2.2.0.0')

# NVIDIA HPC SDK
Stage0 += nvhpc(cuda=default_cuda, cuda_multi=cuda_multi, eula=eula,
                _hpcx=True, mpi=False, version=version)

# Container metadata
Stage0 += environment(variables={'HPCSDK_VERSION': version,
                                 'HPCSDK_RELEASE': release})
Stage0 += label(
    metadata={'com.nvidia.hpcsdk.version': '"{}"'.format(version),
              'com.nvidia.hpcsdk.release': '"{}"'.format(release)})

# nvidia-container-runtime and enroot
Stage0 += environment(variables={
    'MELLANOX_VISIBLE_DEVICES': 'all', # enroot
    'NVIDIA_VISIBLE_DEVICES': 'all',
    'NVIDIA_DRIVER_CAPABILITIES': 'compute,utility',
    'NVIDIA_REQUIRE_CUDA': cuda_driver})
