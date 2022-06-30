"""
Grid[develop] 

Contents:
  Ubuntu 20.04 (LTS)
  CUDA version 11.6
  GNU compilers (upstream; 9.3.0)
  OFED Mellanox 5.6-2.0.9.0 (ConnectX gen 4--6)
  OpenMPI version 4.1.4
"""

# pylint: disable=invalid-name, undefined-variable, used-before-assignment
# pylama: ignore=E0602

# command line options
gpu_arch = USERARG.get('GPU_ARCH', 'sm_80')
use_ucx  = USERARG.get('ucx', 1) == 1       # default is ucx

if gpu_arch not in ( 'sm_80', 'sm_70', 'sm_60', 'sm_37' ):
    print('unknown compute capability:', gpu_arch)
    raise

devel_image   = 'nvcr.io/nvidia/cuda:11.6.2-devel-ubuntu20.04'
runtime_image = 'nvcr.io/nvidia/cuda:11.6.2-base-ubuntu20.04'

# add docstring to Dockerfile
Stage0 += comment(__doc__.strip(), reformat=False)

###############################################################################
# Devel stage
###############################################################################
Stage0 += baseimage(image=devel_image, _as='devel')

# required packages
pkgs = packages(ospackages=[],
                apt=['autoconf', 'automake', 'ca-certificates', 'git',
                     'libgmp-dev', 'libmpfr-dev', 'libssl-dev', 'libnuma-dev' ],
                yum=['autoconf', 'automake', 'ca-certificates', 'git',
                     'gmp-devel',   'mpfr-devel', 'openssl-devel', 'numactl-devel', ])
Stage0 += pkgs

# cmake
Stage0 += cmake(eula=True, version='3.23.2')

# Python3 for scripting in runtime container
py = python(python2=False)
Stage0 += py

# GNU compilers
compiler = gnu()
Stage0 += compiler

# Mellanox OFED 5.6-2.0.9.0
Stage0 += mlnx_ofed(version='5.6-2.0.9.0')

# OpenMPI
if use_ucx:
    # UCX depends on KNEM (use latest versions as of 2022-01-22)
    Stage0 += knem(version='1.1.4')
    # build with gdrcopy
    Stage0 += gdrcopy()
    Stage0 += ucx(cuda=True,gdrcopy=True,knem=True,ofed=True,version='1.12.1')
    pass

Stage0 += openmpi(version='4.1.4',
               cuda=True,
               ucx=use_ucx, infiniband=not use_ucx,
               toolchain=compiler.toolchain)

if not use_ucx:
    Stage0 += shell(commands=[
        'echo "btl_openib_allow_ib = 1" >> /usr/local/openmpi/etc/openmpi-mca-params.conf'])

# build xthi
Stage0 += generic_cmake(branch='feature/gpu',
                        cmake_opts=['-DGPU=NVIDIA', ],
                        install=True,
                        prefix='/usr/local/xthi',
                        repository='https://github.com/james-simone/xthi.git')

# fftw double
Stage0 += fftw(toolchain=compiler.toolchain,
               version='3.3.10',
               configure_opts=[
                   '--enable-type-prefix',
                   '--enable-shared', '--enable-omp',
                   '--enable-sse2', '--enable-avx', '--enable-avx2'])
# fftw float
Stage0 += fftw(toolchain=compiler.toolchain,
               version='3.3.10',
               configure_opts=[
                   '--enable-type-prefix',
                   '--enable-float',
                   '--enable-shared', '--enable-omp',
                   '--enable-sse2', '--enable-avx', '--enable-avx2'])

# mkl
#Stage0 += mkl(eula=True,environment=True)
# BLAS
#Stage0 += openblas(version='0.3.17')

# hdf5
Stage0 += hdf5(version='1.12.2')

# LIME
Stage0 += generic_autotools(branch='c-lime1-3-2',
                            preconfigure=['autoreconf -fi'],
                            install=True,
                            prefix='/usr/local/scidac',
                            runtime=None,
                            repository='https://github.com/usqcd-software/c-lime.git')

# build GRID targeting GPUs
# [DIRAC ITT 2020 Booster compilation](https://github.com/paboyle/Grid/wiki/DIRAC-ITT-2020-Booster-compilation)

if gpu_arch == 'sm_80':
    farch = ' -gencode arch=compute_80,code=sm_80 '
elif gpu_arch == 'sm_70':
    farch = ' -gencode arch=compute_70,code=sm_70 '
elif gpu_arch == 'sm_60':
    farch = ' -gencode arch=compute_60,code=sm_60 '
elif gpu_arch == 'sm_37':
    farch = ' -gencode arch=compute_37,code=sm_37 '
    pass

incdirs = ' -I/usr/local/openmpi/include  -I/usr/local/fftw/include -I/usr/local/hdf5/include -I/usr/local/scidac/include '
libdirs = ' -L/usr/local/openmpi/lib      -L/usr/local/fftw/lib     -L/usr/local/hdf5/lib     -L/usr/local/scidac/lib '

### Grid
Stage0 += generic_autotools(branch='develop',          #commit='135808d',
                            preconfigure=[ './bootstrap.sh', ],
                            build_directory='/var/tmp/Grid/build',
                            build_environment={
                                'CXX': 'nvcc',
                                'MPICXX': 'mpicxx',
                                'CXXFLAGS': '" -std=c++14 ' + farch + incdirs + ' -cudart shared "',
                                'LDFLAGS': '" -cudart shared ' + libdirs + '"',
                                'LIBS': '"-lmpi"',
                            },
                            configure_opts = [
                                '--enable-comms=mpi3-auto',
                                '--disable-unified',
                                '--enable-shm=nvlink',
                                '--enable-simd=GPU',
                                '--enable-gen-simd-width=64',
                                '--enable-accelerator=cuda',
                                '--disable-fermion-reps',
                                '--disable-gparity',
                            ],
                            install=True,
                            prefix='/usr/local/grid',
                            repository='https://github.com/paboyle/Grid')


###############################################################################
# Release stage
###############################################################################

Stage1 += baseimage(image=runtime_image)

Stage1 += Stage0.runtime()
Stage1 += py.runtime()

# numactl tool and libnuma.so.1 needed by xthi
Stage1 += packages(apt=['numactl', 'libnuma1'],yum=['numactl', 'numactl-libs',])

Stage1 += environment(variables={
    'PATH': '/usr/local/xthi/bin:$PATH',
    'LD_LIBRARY_PATH': ':$LD_LIBRARY_PATH', })
