"""
Grid[develop] 

Contents:
  Ubuntu 20.04 (LTS)
  ROCM 5.1.3
  GNU compilers (upstream; 9.3.0)
  OFED Mellanox 5.6-2.0.9.0 (ConnectX gen 4--6)
  OpenMPI version 4.1.4
"""

# pylint: disable=invalid-name, undefined-variable, used-before-assignment
# pylama: ignore=E0602

# command line options
use_ucx  = USERARG.get('ucx', 1) == 1 # default is ucx

base_distro = 'ubuntu20'
devel_image   = 'rocm/dev-ubuntu-20.04:5.1.3-complete'
runtime_image = 'library/ubuntu:20.04'

# add docstring to Dockerfile
Stage0 += comment(__doc__.strip(), reformat=False)

###############################################################################
# Devel stage
###############################################################################
Stage0 += baseimage(image=devel_image, _distro=base_distro, _as='devel')

# required packages
pkgs = packages(ospackages=[],
                apt=['wget', 'autoconf', 'automake', 'ca-certificates', 'git',
                     'libgmp-dev', 'libmpfr-dev', 'libssl-dev', 'libnuma-dev' ],
                yum=['wget', 'autoconf', 'automake', 'ca-certificates', 'git',
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

# Mellanox OFED
Stage0 += mlnx_ofed(version='5.6-2.0.9.0')

# OpenMPI
if use_ucx:
    # UCX depends on KNEM (use latest versions as of 2022-01-22)
    Stage0 += knem(version='1.1.4')
    Stage0 += ucx(cuda=False,with_rocm='/opt/rocm',gdrcopy=False,knem=True,ofed=True,version='1.12.1')
    pass

Stage0 += openmpi(version='4.1.4',
               cuda=False,
               ucx=use_ucx, infiniband=not use_ucx,
               toolchain=compiler.toolchain)

if not use_ucx:
    Stage0 += shell(commands=[
        'echo "btl_openib_allow_ib = 1" >> /usr/local/openmpi/etc/openmpi-mca-params.conf'])

# build xthi
Stage0 += generic_cmake(branch='feature/gpu',
                        cmake_opts=['-DGPU=AMD', ],
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

# hdf5
Stage0 += hdf5()

# LIME
Stage0 += generic_autotools(branch='c-lime1-3-2',
                            preconfigure=['autoreconf -fi'],
                            install=True,
                            prefix='/usr/local/scidac',
                            runtime=None,
                            repository='https://github.com/usqcd-software/c-lime.git')

# build GRID targeting GPUs
# [DIRAC ITT 2020 Booster compilation](https://github.com/paboyle/Grid/wiki/DIRAC-ITT-2020-Booster-compilation)

incdirs = ' -I/opt/rocm/rocthrust/include -I/usr/local/openmpi/include  -I/usr/local/fftw/include -I/usr/local/hdf5/include -I/usr/local/scidac/include '
libdirs = ' -L/opt/rocm/rocthrust/lib     -L/usr/local/openmpi/lib      -L/usr/local/fftw/lib     -L/usr/local/hdf5/lib     -L/usr/local/scidac/lib '

# AMD gpus and llvm  https://llvm.org/docs/AMDGPUUsage.html#processors
# MI50: gfx906; MI100: gfx908; "Arcturis (MI200 series)": gfx90a
### Grid
Stage0 += generic_autotools(branch='develop',   # commit='135808d',
                            preconfigure=[ './bootstrap.sh', ],
                            build_directory='/var/tmp/Grid/build',
                            build_environment={
                                'CXX': 'hipcc',
                                'MPICXX': 'mpicxx',
                                'CXXFLAGS': '" -std=c++14 -fPIC --amdgpu-target=gfx906,gfx908,gfx90a ' + incdirs + '"',
                                'LDFLAGS': '"' + libdirs + '"',
                                'LIBS': '"-lmpi"',
                            },
                            configure_opts = [
                                '--enable-comms=mpi3-auto',
                                '--disable-unified',
                                '--enable-shm=nvlink',
                                '--enable-simd=GPU',
                                '--enable-gen-simd-width=64',
                                '--enable-accelerator=hip',
                                '--disable-fermion-reps',
                                '--disable-gparity',
                            ],
                            install=True,
                            prefix='/usr/local/grid',
                            repository='https://github.com/paboyle/Grid')


###############################################################################
# Release stage
###############################################################################

# centos8 /etc/yum.repos.d/rocm.repo
rocm_centos8 = """
[rocm]
name=rocm
baseurl=https://repo.radeon.com/rocm/centos8/5.1.3/
enabled=1
gpgcheck=1
gpgkey=https://repo.radeon.com/rocm/rocm.gpg.key
"""

Stage1 += baseimage(image=runtime_image, _distro=base_distro)

Stage1 += packages(ospackages=[ 'wget', 'gnupg2', 'ca-certificates',])

# libnuma.so.1 needed by xthi
Stage1 += packages(apt=['libmpfr6', 'libgmp10', 'libnuma1'],yum=['mpfr', 'gmp', 'numactl-libs',])

# ubuntu add rocm repo
if base_distro == 'ubuntu20':
    Stage1 += shell(commands=[
        'wget -q -O - https://repo.radeon.com/rocm/rocm.gpg.key | apt-key add -',
        'echo \'deb [arch=amd64] https://repo.radeon.com/rocm/apt/5.1.3/ ubuntu main\' | tee /etc/apt/sources.list.d/rocm.list',])
elif base_distro == 'centos8':
    Stage1 += shell(commands=[
        'mkdir -p /etc/yum.repos.d/',
        'echo "' + rocm_centos8 + '" > /etc/yum.repos.d/rocm.repo', ])

# rocm runtime
Stage1 += packages(ospackages=[ 'rocm-opencl-runtime', 'rocm-hip-runtime', 'rocm-language-runtime', ])

# copy runtime libomp
d = '/opt/rocm-5.1.3/llvm/lib/'
Stage1 += copy(_from='devel',
               src= [d+'libomp.so', d+'libompstub.so', d+'libomptarget.rtl.amdgpu.so', d+'libomptarget.rtl.x86_64.so', d+'libomptarget.so', ],
               dest=d)

Stage1 += Stage0.runtime()
Stage1 += py.runtime()

Stage1 += environment(variables={
    'PATH': '/usr/local/grid/bin:/usr/local/xthi/bin:$PATH',
    'LD_LIBRARY_PATH': '/opt/rocm/lib:/opt/rocm/hip/lib:$LD_LIBRARY_PATH', })

