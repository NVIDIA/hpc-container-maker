"""
Build the CUDA-STREAM benchmark for multiple CUDA compute capabilities.

Make each build available as a SCI-F application.
"""
Stage0 += baseimage(image='nvidia/cuda:9.1-devel-centos7')

# Install the GNU compiler
Stage0 += gnu(fortran=False)

# Install SCI-F
Stage0 += pip(packages=['scif'])

# Download a single copy of the source code
Stage0 += packages(ospackages=['ca-certificates', 'git'])
Stage0 += shell(commands=['cd /var/tmp',
                          'git clone --depth=1 https://github.com/bcumming/cuda-stream.git cuda-stream'])

# Build CUDA-STREAM as a SCI-F application for each CUDA compute capability
for cc in ['35', '60', '70']:
  binpath = '/scif/apps/cc{}/bin'.format(cc)

  stream = scif(name='cc{}'.format(cc))
  stream += comment('CUDA-STREAM built for CUDA compute capability {}'.format(cc))
  stream += shell(commands=['nvcc -std=c++11 -ccbin=g++ -gencode arch=compute_{0},code=\\"sm_{0},compute_{0}\\" -o {1}/stream /var/tmp/cuda-stream/stream.cu'.format(cc, binpath)])
  stream += environment(variables={'PATH': '{}:$PATH'.format(binpath)})
  stream += label(metadata={'COMPUTE_CAPABILITY': cc})
  stream += shell(commands=['stream'], _test=True)
  stream += runscript(commands=['stream'])

  Stage0 += stream

# Runtime stage
Stage1 += baseimage(image='nvidia/cuda:9.1-base-centos7')

# Install SCI-F
Stage1 += pip(packages=['scif'])

# Install runtime components from the first stage
Stage1 += Stage0.runtime()
