"""
Grid[develop] 

Contents:
  Ubuntu 20.04 (LTS)
  ROCM 4.5.2
  GNU compilers (upstream; 9.3.0)
  OFED Mellanox 5.4-1.0.3.0 (ConnectX gen 4--6)
  OpenMPI version 4.1.2
"""

# pylint: disable=invalid-name, undefined-variable, used-before-assignment
# pylama: ignore=E0602

# command line options
use_ucx  = USERARG.get('ucx', None) is not None

base_distro = 'ubuntu20'
devel_image   = 'rocm/dev-ubuntu-20.04:4.5.2-complete'
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

# GNU compilers
compiler = gnu()
Stage0 += compiler

# Mellanox OFED
Stage0 += mlnx_ofed(version='5.4-1.0.3.0')

# OpenMPI
if use_ucx:
    # UCX depends on KNEM (use latest versions as of 2022-01-22)
    Stage0 += knem(version='1.1.4')
    Stage0 += ucx(cuda=False, version='1.12.0')
    pass

Stage0 += openmpi(version='4.1.2',
               cuda=False,
               ucx=use_ucx, infiniband=not use_ucx,
               toolchain=compiler.toolchain)

if not use_ucx:
    Stage0 += shell(commands=[
        'echo "btl_openib_allow_ib = 1" >> /usr/local/openmpi/etc/openmpi-mca-params.conf'])

# build xthi
Stage0 += generic_build(branch='master',
                        build=['make all CC=gcc MPICC=/usr/local/openmpi/bin/mpicc', ],
                        install=['mkdir -p /usr/local/xthi/bin',
                                 'cp /var/tmp/xthi/xthi /var/tmp/xthi/xthi.nompi /usr/local/xthi/bin'],
                        prefix='/usr/local/xthi',
                        repository='https://git.ecdf.ed.ac.uk/dmckain/xthi.git')
Stage0 += environment(variables={'PATH': '/usr/local/xthi/bin:$PATH'})

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
# MI100:  gfx908  "Arcturis": gfx90a
### Grid
if True:
    Stage0 += generic_autotools(branch='develop',   # commit='135808d',
                                preconfigure=[ './bootstrap.sh', ],
                                build_directory='/var/tmp/Grid/build',
                                build_environment={
                                    'CXX': 'hipcc',
                                    'MPICXX': 'mpicxx',
                                    'CXXFLAGS': '" -std=c++14 -fPIC --amdgpu-target=gfx906,gfx908 ' + incdirs + '"',
                                    'LDFLAGS': '"' + libdirs + '"',
                                    'LIBS': '"-lmpi"',
                                },
                                configure_opts = [
                                    '--disable-fermion-reps',
                                    '--disable-gparity',
                                    '--enable-unified=no',
                                    '--enable-simd=GPU',
                                    '--enable-accelerator=hip',
                                    '--enable-gen-simd-width=64',
                                    '--enable-comms=mpi3-auto',
                                ],
                                install=True,
                                prefix='/usr/local/grid',
                                repository='https://github.com/paboyle/Grid')
    pass

###############################################################################
# Release stage
###############################################################################

# centos8 /etc/yum.repos.d/rocm.repo
rocm_centos8 = """
[rocm]
name=rocm
baseurl=https://repo.radeon.com/rocm/centos8/4.5.2/
enabled=1
gpgcheck=1
gpgkey=https://repo.radeon.com/rocm/rocm.gpg.key
"""

if True:
    Stage1 += baseimage(image=runtime_image, _distro=base_distro)

    Stage1 += packages(ospackages=[ 'wget', 'gnupg2', 'ca-certificates',])

    # libnuma.so.1 needed by xthi
    Stage1 += packages(apt=['libmpfr6', 'libgmp10', 'libnuma1'],yum=['mpfr', 'gmp', 'numactl-libs',])

    # ubuntu add rocm repo
    if base_distro == 'ubuntu20':
        Stage1 += shell(commands=[
            'wget -q -O - https://repo.radeon.com/rocm/rocm.gpg.key | apt-key add -',
            'echo \'deb [arch=amd64] https://repo.radeon.com/rocm/apt/4.5.2/ ubuntu main\' | tee /etc/apt/sources.list.d/rocm.list',])
    elif base_distro == 'centos8':
        Stage1 += shell(commands=[
            'mkdir -p /etc/yum.repos.d/',
            'echo "' + rocm_centos8 + '" > /etc/yum.repos.d/rocm.repo', ])

    # rocm runtime
    Stage1 += packages(ospackages=[ 'rocm-opencl-runtime', 'rocm-hip-runtime', 'rocm-language-runtime', ])

    # copy runtime libomp
    d = '/opt/rocm-4.5.2/llvm/lib/'
    Stage1 += copy(_from='devel',src= [d+'libomp.so', d+'libompstub.so', d+'libomptarget.rtl.amdgpu.so', d+'libomptarget.rtl.x86_64.so', d+'libomptarget.so', ],
                   dest=d)

    Stage1 += Stage0.runtime()

    Stage1 += environment(variables={
        'PATH': '/usr/local/grid/bin:/usr/local/xthi/bin:$PATH',
        'LD_LIBRARY_PATH': ':$LD_LIBRARY_PATH', })
    pass
