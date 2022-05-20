# Generic recipe to build a OFED+UCX+MPI+CUDA container environment
# that supports both OFED 4.x and 5.x.

# Development stage
Stage0 += baseimage(image='nvcr.io/nvidia/cuda:11.0-devel-ubuntu18.04',
                    _as='devel')

# Compiler
Stage0 += gnu()

# Communication libraries
Stage0 += gdrcopy(ldconfig=True)
Stage0 += knem(ldconfig=True)

# Mellanox legacy OFED support
mlnx_versions=['4.2-1.5.1.0', '4.3-1.0.1.0', '4.4-1.0.0.0', '4.5-1.0.1.0',
               '4.6-1.0.1.1', '4.7-3.2.9.0', '4.9-0.1.7.0']
Stage0 += multi_ofed(inbox=False, mlnx_versions=mlnx_versions,
                     prefix="/usr/local/ofed", symlink=False)

# RDMA-core based OFED support
Stage0 += mlnx_ofed(version="5.2-2.2.0.0", symlink=False)

# UCX default - RDMA-core based OFED
Stage0 += ucx(version='1.10.0', cuda=True,
              gdrcopy='/usr/local/gdrcopy', knem='/usr/local/knem',
              disable_static=True, enable_mt=True)

# UCX - Mellanox legacy support
Stage0 += ucx(version='1.10.0',
              build_environment={
                  "LD_LIBRARY_PATH": "/usr/local/ofed/4.6-1.0.1.1/lib:${LD_LIBRARY_PATH}"},
              cuda=True, environment=False, gdrcopy='/usr/local/gdrcopy',
              knem='/usr/local/knem', prefix='/usr/local/ucx-mlnx-legacy',
              disable_static=True, enable_mt=True,
              with_verbs='/usr/local/ofed/4.6-1.0.1.1/usr',
              with_rdmacm='/usr/local/ofed/4.6-1.0.1.1/usr')

# Symlink legacy UCX into legacy OFED versions
Stage0 += shell(commands=[
    'ln -s /usr/local/ucx-mlnx-legacy/{1}/* /usr/local/ofed/{0}/usr/{1}'.format(version, directory) for version in mlnx_versions for directory in ['bin', 'lib']])

# PMI2 support
Stage0 += slurm_pmi2(prefix="/usr/local/pmi", version='20.11.9')

# OpenMPI
Stage0 += openmpi(cuda=True, infiniband=False, ldconfig=True, ucx=True,
                  version='4.0.5',
                  disable_oshmem=True, disable_static=True,
                  enable_mca_no_build='btl-uct', with_slurm=False,
                  with_pmi='/usr/local/pmi')

# Deployment stage
Stage1 += baseimage(image='nvcr.io/nvidia/cuda:11.0-base-ubuntu18.04')
Stage1 += Stage0.runtime(_from='devel')

# Allow running MPI as root
Stage1 += environment(variables={'OMPI_ALLOW_RUN_AS_ROOT': '1',
                                 'OMPI_ALLOW_RUN_AS_ROOT_CONFIRM': '1'})

# Entrypoint
Stage1 += copy(src='entrypoint.sh', dest='/usr/local/bin/entrypoint.sh')
Stage1 += runscript(commands=['/usr/local/bin/entrypoint.sh'])

# Performance and compatibility tuning
Stage1 += environment(variables={'CUDA_CACHE_DISABLE': '1',
                                 'MELLANOX_VISIBLE_DEVICES': 'all', # enroot
                                 'OMPI_MCA_pml': 'ucx'})
