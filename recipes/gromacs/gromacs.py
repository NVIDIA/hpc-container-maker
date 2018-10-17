r"""
GROMACS 2018.2

Contents:
  Ubuntu 16.04
  CUDA version 9.0
  GNU compilers (upstream)
  OFED (upstream)
  OpenMPI version 3.0.0
"""
# pylint: disable=invalid-name, undefined-variable, used-before-assignment
# pylama: ignore=E0602
import os
from hpccm.templates.CMakeBuild import CMakeBuild
from hpccm.templates.git import git

gromacs_version = USERARG.get('GROMACS_VERSION', '2018.2')

Stage0 += comment(__doc__.strip(), reformat=False)
Stage0.name = 'devel'
Stage0 += baseimage(image='nvidia/cuda:9.0-devel-ubuntu16.04', _as=Stage0.name)

python = python(python3=False)
Stage0 += python

gnu = gnu(fortran=False)
Stage0 += gnu

Stage0 += packages(ospackages=['ca-certificates', 'cmake', 'git'])

ofed = ofed()
Stage0 += ofed

ompi = openmpi(configure_opts=['--enable-mpi-cxx'], parallel=32,
               prefix="/opt/openmpi", version='3.0.0')
Stage0 += ompi

cm = CMakeBuild()
build_cmds = [git().clone_step(
                  repository='https://github.com/gromacs/gromacs',
                  branch='v' + gromacs_version, path='/gromacs',
                  directory='src'),
              cm.configure_step(directory='/gromacs/src',
                                build_directory='/gromacs/build',
                                opts=[
                                  '-DCMAKE_BUILD_TYPE=Release',
                                  '-DCMAKE_INSTALL_PREFIX=/gromacs/install',
                                  '-DCUDA_TOOLKIT_ROOT_DIR=/usr/local/cuda',
                                  '-DGMX_BUILD_OWN_FFTW=ON',
                                  '-DGMX_GPU=ON',
                                  '-DGMX_MPI=OFF',
                                  '-DGMX_OPENMP=ON',
                                  '-DGMX_PREFER_STATIC_LIBS=ON',
                                  '-DMPIEXEC_PREFLAGS=--allow-run-as-root',
                                  '-DREGRESSIONTEST_DOWNLOAD=ON']),
              cm.build_step(),
              cm.build_step(target='install'),
              cm.build_step(target='check')]
Stage0 += shell(commands=build_cmds)

######
# Runtime image stage
######
Stage1.baseimage('nvidia/cuda:9.0-runtime-ubuntu16.04')

Stage1 += python.runtime(_from=Stage0.name)

Stage1 += gnu.runtime(_from=Stage0.name)

Stage1 += ofed.runtime(_from=Stage0.name)

Stage1 += ompi.runtime(_from=Stage0.name)

Stage1 += copy(_from=Stage0.name, src='/gromacs/install',
               dest='/gromacs/install')

# Include examples if they exist in the build context
if os.path.isdir('recipes/gromacs/examples'):
    Stage1 += copy(src='recipes/gromacs/examples', dest='/workspace/examples')

Stage1 += environment(variables={'PATH': '$PATH:/gromacs/install/bin'})

Stage1 += label(metadata={'com.nvidia.gromacs.version': gromacs_version})

Stage1 += workdir(directory='/workspace')
