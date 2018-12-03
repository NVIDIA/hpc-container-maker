"""
MILC 7.8.1

Contents:
  Ubuntu 16.04
  CUDA version 9.0
  GNU compilers (upstream)
  OFED (upstream)
  OpenMPI version 3.0.0
  QUDA version 0.8.0
"""
# pylint: disable=invalid-name, undefined-variable, used-before-assignment
# pylama: ignore=E0602
import os
from hpccm.templates.git import git
from hpccm.templates.sed import sed
from hpccm.templates.tar import tar
from hpccm.templates.wget import wget
from hpccm.templates.CMakeBuild import CMakeBuild

gpu_arch = USERARG.get('GPU_ARCH', 'sm_60')

# add docstring to Dockerfile
Stage0 += comment(__doc__.strip(), reformat=False)

###############################################################################
# Devel stage
###############################################################################
Stage0.name = 'devel'
Stage0 += baseimage(image='nvidia/cuda:9.0-devel-ubuntu16.04', _as=Stage0.name)

Stage0 += packages(ospackages=['autoconf', 'automake', 'ca-certificates',
                               'cmake', 'git'])

ofed = ofed()
Stage0 += ofed

ompi = openmpi(configure_opts=['--enable-mpi-cxx'], prefix='/opt/openmpi',
               parallel=32, version='3.0.0')
Stage0 += ompi

# build QUDA
g = git()
cm = CMakeBuild()
quda_cmds = [g.clone_step(repository='https://github.com/lattice/quda',
                          branch='v0.8.0', path='/quda', directory='src'),
             cm.configure_step(directory='/quda/src',
                               build_directory='/quda/build', opts=[
                                   '-DCMAKE_BUILD_TYPE=RELEASE',
                                   '-DQUDA_DIRAC_CLOVER=ON',
                                   '-DQUDA_DIRAC_DOMAIN_WALL=ON',
                                   '-DQUDA_DIRAC_STAGGERED=ON',
                                   '-DQUDA_DIRAC_TWISTED_CLOVER=ON',
                                   '-DQUDA_DIRAC_TWISTED_MASS=ON',
                                   '-DQUDA_DIRAC_WILSON=ON',
                                   '-DQUDA_FORCE_GAUGE=ON',
                                   '-DQUDA_FORCE_HISQ=ON',
                                   '-DQUDA_GPU_ARCH={}'.format(gpu_arch),
                                   '-DQUDA_INTERFACE_MILC=ON',
                                   '-DQUDA_INTERFACE_QDP=ON',
                                   '-DQUDA_LINK_HISQ=ON',
                                   '-DQUDA_MPI=ON']),
             cm.build_step(parallel=32)]
Stage0 += shell(commands=quda_cmds)

# build MILC
milc_version = '7.8.1'
milc_cmds = ['mkdir -p /milc',
             wget().download_step(url='http://www.physics.utah.edu/~detar/milc/milc_qcd-{}.tar.gz'.format(milc_version)),
             tar().untar_step(
                 tarball='/tmp/milc_qcd-{}.tar.gz'.format(milc_version),
                 directory='/milc'),
             'cd /milc/milc_qcd-{}/ks_imp_rhmc'.format(milc_version),
             'cp ../Makefile .',
             sed().sed_step(
                 file='/milc/milc_qcd-{}/ks_imp_rhmc/Makefile'.format(
                     milc_version),
                 patterns=[r's/WANTQUDA\(.*\)=.*/WANTQUDA\1= true/g',
                           r's/\(WANT_.*_GPU\)\(.*\)= .*/\1\2= true/g',
                           r's/QUDA_HOME\(.*\)= .*/QUDA_HOME\1= \/quda\/build/g',
                           r's/CUDA_HOME\(.*\)= .*/CUDA_HOME\1= \/usr\/local\/cuda/g',
                           r's/#\?MPP = .*/MPP = true/g',
                           r's/#\?CC = .*/CC = mpicc/g',
                           r's/LD\(\s+\)= .*/LD\1= mpicxx/g',
                           r's/PRECISION = [0-9]\+/PRECISION = 2/g',
                           r's/WANTQIO = .*/WANTQIO = #true or blank.  Implies HAVEQMP./g',
                           r's/CGEOM =.*-DFIX_NODE_GEOM.*/CGEOM = #-DFIX_NODE_GEOM/g']),
             'C_INCLUDE_PATH=/quda/build/include make su3_rhmd_hisq']
Stage0 += shell(commands=milc_cmds)

###############################################################################
# Release stage
###############################################################################
Stage1 += baseimage(image='nvidia/cuda:9.0-base-ubuntu16.04')

Stage1 += ofed.runtime()

Stage1 += ompi.runtime()

Stage1 += copy(_from=Stage0.name,
               src='/milc/milc_qcd-{}/ks_imp_rhmc/su3_rhmd_hisq'.format(
                   milc_version),
               dest='/milc/su3_rhmd_hisq')
Stage1 += environment(variables={'PATH': '$PATH:/milc'})

# Include examples if they exist in the build context
if os.path.isdir('recipes/milc/examples'):
    Stage1 += copy(src='recipes/milc/examples', dest='/workspace/examples')

Stage1 += workdir(directory='/workspace')
