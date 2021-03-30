# Use the generic OFED+UCX+OpenMPI recipe
hpccm.include('common.py')

# Build the OSU Micro-Benchmarks in the development stage
Stage0 += generic_autotools(
    build_environment={'CC': 'mpicc', 'CXX': 'mpicxx'},
    enable_cuda=True,
    prefix='/usr/local/osu',
    url='http://mvapich.cse.ohio-state.edu/download/mvapich/osu-micro-benchmarks-5.7.tar.gz',
    with_cuda='/usr/local/cuda')

# Copy the OSU Micro-Benchmark binaries into the deployment stage
Stage1 += copy(_from='devel', src='/usr/local/osu', dest='/usr/local/osu')

# Add the OSU Micro-Benchmarks to the default PATH
base_path = '/usr/local/osu/libexec/osu-micro-benchmarks'
Stage1 += environment(variables={'PATH': '{0}:{0}/mpi/collective:{0}/mpi/one-sided:{0}/mpi/pt2pt:{0}/mpi/startup:$PATH'.format(base_path)})
