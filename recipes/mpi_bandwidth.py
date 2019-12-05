"""
MPI Bandwidth

Contents:
  CentOS 7
  GNU compilers (upstream)
  Mellanox OFED
  OpenMPI
  PMI2 (SLURM)
  UCX

Building:
  1. Docker to Singularity
     $ hpccm --recipe mpi_bandwidth.py > Dockerfile
     $ sudo docker build -t mpi_bw -f Dockerfile .
     $ singularity build mpi_bw.sif docker-daemon://mpi_bw:latest

  2. Singularity
     $ hpccm --recipe mpi_bandwidth.py --format singularity --singularity-version=3.2 > Singularity.def
     $ sudo singularity build mpi_bw.sif Singularity.def

Running with Singularity:
  1. Using a compatible host MPI runtime
     $ mpirun -n 2 singularity run mpi_bw.sif mpi_bandwidth

  2. Using the MPI runtime inside the container
     $ singularity run mpi_bw.sif mpirun -n 2 -H node1:1,node2:1 --launch-agent "singularity exec \$SINGULARITY_CONTAINER orted" mpi_bandwidth

  3. Using SLURM srun
     $ srun -n 2 --mpi=pmi2 singularity run mpi_bw.sif mpi_bandwidth
"""

Stage0 += comment(__doc__, reformat=False)

# CentOS base image
Stage0 += baseimage(image='centos:7', _as='build')

# GNU compilers
Stage0 += gnu(fortran=False)

# Mellanox OFED
Stage0 += mlnx_ofed()

# UCX
Stage0 += ucx(cuda=False)

# PMI2
Stage0 += slurm_pmi2()

# OpenMPI (use UCX instead of IB directly)
Stage0 += openmpi(cuda=False, infiniband=False, pmi='/usr/local/slurm-pmi2',
                  ucx='/usr/local/ucx')

# MPI Bandwidth
Stage0 += shell(commands=[
    'wget -q -nc --no-check-certificate -P /var/tmp https://computing.llnl.gov/tutorials/mpi/samples/C/mpi_bandwidth.c',
    'mpicc -o /usr/local/bin/mpi_bandwidth /var/tmp/mpi_bandwidth.c'])

### Runtime distributable stage
Stage1 += baseimage(image='centos:7')
Stage1 += Stage0.runtime()
Stage1 += copy(_from='build', src='/usr/local/bin/mpi_bandwidth',
               dest='/usr/local/bin/mpi_bandwidth')
