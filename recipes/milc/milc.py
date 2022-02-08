"""
MILC 7.8.1

Contents:
  Ubuntu 16.04
  CUDA version 11.2
  GNU compilers (upstream)
  OFED (upstream)
  OpenMPI version 3.1.4
  QUDA version 0.8.0
"""
# pylint: disable=invalid-name, undefined-variable, used-before-assignment
# pylama: ignore=E0602

gpu_arch = USERARG.get('GPU_ARCH', 'sm_60')

# add docstring to Dockerfile
Stage0 += comment(__doc__.strip(), reformat=False)

###############################################################################
# Devel stage
###############################################################################
Stage0 += baseimage(image='nvcr.io/nvidia/cuda:11.2.0-devel-ubuntu18.04',
                    _as='devel')

Stage0 += gnu()
Stage0 += cmake(eula=True)
Stage0 += ofed()
Stage0 += openmpi(version='3.1.4')

# build QUDA
Stage0 += packages(ospackages=['ca-certificates', 'git'])
Stage0 += generic_cmake(branch='develop',
                        cmake_opts=['-D CMAKE_BUILD_TYPE=RELEASE',
                                    '-D QUDA_DIRAC_CLOVER=ON',
                                    '-D QUDA_DIRAC_DOMAIN_WALL=ON',
                                    '-D QUDA_DIRAC_STAGGERED=ON',
                                    '-D QUDA_DIRAC_TWISTED_CLOVER=ON',
                                    '-D QUDA_DIRAC_TWISTED_MASS=ON',
                                    '-D QUDA_DIRAC_WILSON=ON',
                                    '-D QUDA_FORCE_GAUGE=ON',
                                    '-D QUDA_FORCE_HISQ=ON',
                                    '-D QUDA_GPU_ARCH={}'.format(gpu_arch),
                                    '-D QUDA_INTERFACE_MILC=ON',
                                    '-D QUDA_INTERFACE_QDP=ON',
                                    '-D QUDA_LINK_HISQ=ON',
                                    '-D QUDA_MPI=ON'],
                        install=False,
                        ldconfig=True,
                        postinstall=['cp -a /var/tmp/quda/build/* /usr/local/quda'],
                        preconfigure=['mkdir -p /usr/local/quda'],
                        prefix='/usr/local/quda',
                        repository='https://github.com/lattice/quda.git')

# build MILC
Stage0 += generic_build(branch='develop',
                        build=['cp Makefile ks_imp_rhmc',
                               'cd ks_imp_rhmc',
                               'make -j 1 su3_rhmd_hisq \
                                CC=/usr/local/openmpi/bin/mpicc \
                                LD=/usr/local/openmpi/bin/mpicxx \
                                QUDA_HOME=/usr/local/quda \
                                WANTQUDA=true \
                                WANT_GPU=true \
                                WANT_CL_BCG_GPU=true \
                                WANT_FN_CG_GPU=true \
                                WANT_FL_GPU=true \
                                WANT_FF_GPU=true \
                                WANT_GF_GPU=true \
                                MPP=true \
                                PRECISION=2 \
                                WANTQIO=""'],
                        install=['mkdir -p /usr/local/milc/bin',
                                 'cp /var/tmp/milc_qcd/ks_imp_rhmc/su3_rhmd_hisq /usr/local/milc/bin'],
                        prefix='/usr/local/milc',
                        repository='https://github.com/milc-qcd/milc_qcd')
Stage0 += environment(variables={'PATH': '/usr/local/milc/bin:$PATH'})

###############################################################################
# Release stage
###############################################################################
Stage1 += baseimage(image='nvcr.io/nvidia/cuda:11.2.0-base-ubuntu18.04')

Stage1 += packages(ospackages=['libcublas-11-2'])

Stage1 += Stage0.runtime()

Stage1 += environment(variables={'PATH': '/usr/local/milc/bin:$PATH'})
