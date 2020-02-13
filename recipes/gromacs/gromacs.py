r"""
GROMACS 2020

Contents:
  Ubuntu 16.04
  CUDA version 10.1
  GNU compilers (upstream)
  OFED (upstream)
  OpenMPI version 3.1.4
"""

gromacs_version = USERARG.get('gromacs', '2020')

Stage0 += comment(__doc__.strip(), reformat=False)
Stage0 += baseimage(image='nvidia/cuda:10.1-devel-ubuntu16.04', _as='build')

Stage0 += python(python3=False)

Stage0 += gnu(fortran=False)

Stage0 += cmake(eula=True)

Stage0 += ofed()

Stage0 += openmpi(version='3.1.4')

Stage0 += generic_cmake(cmake_opts=['-D CMAKE_BUILD_TYPE=Release',
                                    '-D CUDA_TOOLKIT_ROOT_DIR=/usr/local/cuda',
                                    '-D GMX_BUILD_OWN_FFTW=ON',
                                    '-D GMX_GPU=ON',
                                    '-D GMX_MPI=ON',
                                    '-D GMX_OPENMP=ON',
                                    '-D GMX_PREFER_STATIC_LIBS=ON',
                                    '-D MPIEXEC_PREFLAGS=--allow-run-as-root'],
                        prefix='/usr/local/gromacs',
                        url='http://ftp.gromacs.org/pub/gromacs/gromacs-{}.tar.gz'.format(gromacs_version))

Stage0 += environment(variables={'PATH': '$PATH:/usr/local/gromacs/bin'})

Stage0 += label(metadata={'gromacs.version': gromacs_version})

######
# Runtime image stage
######
Stage1 += baseimage(image='nvidia/cuda:10.1-base-ubuntu16.04')

Stage1 += Stage0.runtime(_from='build')

# Singularity 3.5.3 will not copy symlinks from another stage, so
# use the full real path to libcufft.
Stage1 += copy(_from='build',
               src='/usr/local/cuda/targets/x86_64-linux/lib/libcufft.so.10.1.1.243',
               dest='/usr/local/cuda/lib64/libcufft.so.10')

Stage1 += environment(variables={'PATH': '$PATH:/usr/local/gromacs/bin'})

Stage1 += label(metadata={'gromacs.version': gromacs_version})
