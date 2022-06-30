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
use_ucx  = USERARG.get('ucx', 1) == 1    # default is ucx

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

# Python3 for scripting in container
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
    # build without(!!) gdrcopy; FAIL with gdrcopy 2.x not needed for rocm??
    #Stage0 += gdrcopy()
    Stage0 += ucx(cuda=False,with_rocm='/opt/rocm',gdrcopy=False,knem=True,ofed=True,version='1.12.1')
    pass

Stage0 += openmpi(version='4.1.4',
               cuda=False,
               ucx=use_ucx, infiniband=not use_ucx,
               toolchain=compiler.toolchain)

if not use_ucx:
    Stage0 += shell(commands=[
        'echo "btl_openib_allow_ib = 1" >> /usr/local/openmpi/etc/openmpi-mca-params.conf'])


