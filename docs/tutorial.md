# HPC Container Maker Tutorial

- [Reproducing a bare metal environment](#reproducing-a-bare-metal-environment)
- [MPI Bandwidth](#mpi-bandwidth)
- [User Arguments](#user-arguments)
- [Multi-stage Recipes](#multi-stage-recipes)

## Reproducing a bare metal environment

Many HPC systems use [environment
modules](https://en.wikipedia.org/wiki/Environment_Modules_(software))
to manage their software environment.  A user loads the modules
corresponding to the desired software environment.

```
$ module load cuda/9.0
$ module load gcc
$ module load openmpi/1.10.7
```

Modules can depend on each other, and in this case, the `openmpi`
module was built with the gcc compiler and with CUDA support enabled.

The Linux distribution and drivers are typically fixed by the system
administrator, for instance CentOS 7 and Mellanox OFED 3.4.

The system administrator of the HPC system built and installed these
components for their user community.  Including a software component
in a container image requires knowing how to properly configure and
build the component.  This is specialized knowledge and can be further
complicated when applying container best practices.

_How can this software environment be reproduced in a container image?_

The starting point for any container image is a base image.  Since
CUDA is required, the base image should be one of the [publicly
available CUDA base images](https://hub.docker.com/r/nvidia/cuda/).
The CUDA base image corresponding to CUDA 9.0 and CentOS 7 is
`nvidia/cuda:9.0-devel-centos7`.  So the first line of the HPCCM
recipe is:

```python
Stage0 += baseimage(image='nvidia/cuda:9.0-devel-centos7')
```

_Note_: `Stage0` refers to the first stage of a [multi-stage Docker
build](https://docs.docker.com/develop/develop-images/multistage-build/).
Multi-stage builds are a technique that can significantly reduce the
size of container images.  This tutorial section will not use
multi-stage builds, so the `Stage0` prefix can be considered
boilerplate.

The next step is to include the HPCCM [building
blocks](/docs/building_blocks.md) corresponding to the rest of the
desired software environment: [Mellanox
OFED](/docs/building_blocks.md#mlnx_ofed),
[gcc](/docs/building_blocks.md#gnu), and
[OpenMPI](/docs/building_blocks.md#openmpi).

The [`mlnx_ofed` building block](/docs/building_blocks.md#mlnx_ofed)
installs the OpenFabrics user space libraries:

```python
Stage0 += mlnx_ofed(version='3.4-1.0.0.0')
```

The [`gnu` building block](/docs/building_blocks.md#gnu) installs the
GNU compiler suite:

```python
compiler = gnu()
Stage0 += compiler
```

_Note_: The `compiler` variable is defined here so that in the next
step the OpenMPI building block can use the GNU compiler toolchain.
Since the GNU compiler is typically the default compiler, this is just
being explicit about the default behavior.

The [`openmpi` building block](/docs/building_blocks.md#openmpi)
installs OpenMPI, configured to use the desired version, the GNU
compiler, and with CUDA and InfiniBand enabled:

```python
Stage0 += openmpi(cuda=True, infiniband=True, toolchain=compiler.toolchain,
                  version='1.10.7')
```

Bringing it all together, the complete recipe corresponding to the
bare metal software environment is:

```python
Stage0 += baseimage(image='nvidia/cuda:9.0-devel-centos7')
Stage0 += mlnx_ofed(version='3.4-1.0.0.0')
compiler = gnu()
Stage0 += compiler
Stage0 += openmpi(cuda=True, infiniband=True, toolchain=compiler.toolchain,
                  version='1.10.7')
```

The HPCCM recipe has nearly a one-to-one correspondence with the
environment module commands.

Assuming the recipe file is named `cuda-gcc-openmpi.py`, use the
`hpccm` command line tool to generate the corresponding Dockerfile or
Singularity definition file.

```
$ hpccm --recipe cuda-gcc-openmpi.py --format docker
```

```
$ hpccm --recipe cuda-gcc-openmpi.py --format singularity
```

Depending on the desired [workflow](/docs/workflows.md), the next step
might be to use a text editor to add the steps to build an HPC
application to the Dockerfile or Singularity definition file, or it
might be to extend the HPCCM recipe to add the steps to build an HPC
application.

### Extensions

What if instead of the default version GNU compiler, version 7 was
needed?  Change `compiler = gnu()` to `compiler = gnu(version='7')` and
see what happens.

What if instead of the GNU compilers, the bare metal environment was
based on the PGI compilers?  Change `compiler = gnu()` to `compiler =
pgi(eula=True)` and see what happens.  _Note_: The [PGI compiler
EULA](https://www.pgroup.com/doc/LICENSE) must be accepted in order to
use the [PGI building block](/docs/building_blocks.md#pgi).

What if the Linux distribution was Ubuntu instead of CentOS?  Change
the base image from `nvidia/cuda:9.0-devel-centos7` to
`nvidia/cuda:9.0-devel-ubuntu16.04` and see what happens.

What would the equivalent script using the HPCCM Python module look
like?

```python
#!/usr/bin/env python

from __future__ import print_function

import argparse
import hpccm
from hpccm.building_blocks import gnu, mlnx_ofed, openmpi
from hpccm.primitives import baseimage

parser = argparse.ArgumentParser(description='HPCCM Tutorial')
parser.add_argument('--format', type=str, default='docker',
                    choices=['docker', 'singularity'],
                    help='Container specification format (default: docker)')
args = parser.parse_args()

Stage0 = hpccm.Stage()

### Start "Recipe"
Stage0 += baseimage(image='nvidia/cuda:9.0-devel-centos7')
Stage0 += mlnx_ofed(version='3.4-1.0.0.0')
compiler = gnu()
Stage0 += compiler
Stage0 += openmpi(cuda=True, infiniband=True, toolchain=compiler.toolchain,
                 version='1.10.7')
### End "Recipe"

hpccm.config.set_container_format(args.format)

print(Stage0)
```

The "recipe" itself is exactly the same, but the Python script
requires additional code to import the Python modules, parse input,
and print output that is handled automatically by the `hpccm` command
line tool.  However, the script also allows precise control over its
behavior.  [For instance](/recipes/examples/script.py), additional
command line arguments could be added to specify the compiler version,
compiler suite, Linux distribution, and so on.  Note it is also
possible to tailor the behavior of HPCCM recipes with [user
arguments](/docs/recipes.md#userargs).  Another possible enhancement
would be to write the output to a file instead of printing it to
standard output.

## MPI Bandwidth

The [MPI
Bandwidth](https://computing.llnl.gov/tutorials/mpi/samples/C/mpi_bandwidth.c)
sample program from the Lawrence Livermore National Laboratory (LLNL)
will be used as a proxy application to illustrate how to use HPCCM
recipes to create application containers.

The CentOS 7 base image is sufficient for this example.  The Mellanox
OFED user space libraries, a compiler, and MPI library are also
needed.  For this tutorial section, the GNU compiler and OpenMPI will
be used.  The corresponding HPCCM recipe is:

```python
Stage0 += baseimage(image='centos:7')
Stage0 += gnu(fortran=False)
Stage0 += mlnx_ofed()
Stage0 += openmpi(cuda=False)
```

_Note_: `Stage0` refers to the first stage of a [multi-stage Docker
build](https://docs.docker.com/develop/develop-images/multistage-build/).
Multi-stage builds are a technique that can significantly reduce the
size of container images.  This tutorial section will not use
multi-stage builds, so the `Stage0` prefix can be considered
boilerplate.

The next step is to build the MPI Bandwidth program from source.
First the source code must be copied into the container, and then
compiled.  For both of these steps, HPCCM
[primitives](/docs/primitives.md) will be used.  HPCCM primitives are
wrappers around the native container specification operations that
translate the conceptual operation into the corresponding native
container specific syntax.  Primitives also hide many of the
behavioral differences between the Docker and Singularity container
image build processes so that behavior is consistent regardless of the
output configuration specification format.

First, download the MPI Bandwidth source code into the same directory
as the recipe.  Then the local copy of the source code can be copied
into the container image.

```python
Stage0 += copy(src='mpi_bandwidth.c', dest='/var/tmp/mpi_bandwidth.c')
```

_Note_: The MPI Bandwidth source code could also be downloaded as part
of the container build itself, e.g., using `wget`.  The [MPI Bandwidth
example recipe](/recipes/mpi_bandwidth.py) does this.

Finally, compile the program binary using the `mpicc` MPI compiler
wrapper.

```python
Stage0 += shell(commands=[
    'mpicc -o /usr/local/bin/mpi_bandwidth /var/tmp/mpi_bandwidth.c'])
```

_Note_: In a production container image, a cleanup step would
typically also be performed to remove the source code and any other
build artifacts.  That step is skipped here.  [Multi-stage Docker
builds](https://docs.docker.com/develop/develop-images/multistage-build/)
are another approach that separates the application build process from
the application deployment.

The complete [MPI Bandwidth recipe](/recipes/mpi-bandwidth.py) is:

```python
# CentOS base image
Stage0 += baseimage(image='centos:7')

# GNU compilers
Stage0 += gnu(fortran=False)

# Mellanox OFED
Stage0 += mlnx_ofed()

# OpenMPI
Stage0 += openmpi(cuda=False)

# MPI Bandwidth
Stage0 += copy(src='mpi_bandwidth.c', dest='/var/tmp/mpi_bandwidth.c')
Stage0 += shell(commands=[
    'mpicc -o /usr/local/bin/mpi_bandwidth /var/tmp/mpi_bandwidth.c'])
```

Assuming the recipe file is named `mpi_bandwidth.py`, the following
steps generate Docker and Singularity container images and then
demonstrate running the program on a single node.

```
$ hpccm --recipe mpi_bandwidth.py --format docker > Dockerfile
$ sudo docker build -t mpi_bandwidth -f Dockerfile .
$ sudo docker run --rm -it mpirun --allow-run-as-root -n 2 /usr/local/bin/mpi_bandwidth
```

```
$ hpccm --recipe mpi_bandwidth.py --format singularity > Singularity.def
$ sudo singularity build mpi_bandwidth.sif Singularity.def
$ singularity exec mpi_bandwidth.sif mpirun -n 2 /usr/local/bin/mpi_bandwidth
```

_Note_: The exact same container images may also be used for
multi-node runs, but that is beyond the scope of this tutorial
section.  The webinar [GPU Accelerated Multi-Node HPC Workloads with
Singularity](https://www.nvidia.com/content/webinar-portal/src/webinar-portal.html?D2C=1850434&isSocialSharing=Y&partnerref=emailShareFromGateway)
is a good reference for multi-node MPI runs.

## User Arguments

Using Python to express container specifications is one of the key
features of HPCCM.  Python recipes can process user input to generate
multiple container specification permutations from the same source
code.

Consider the case where the CUDA version and OpenMPI version are user
specified values.  If not specified, default values should be used.
In addition, the user supplied values should be verified to be valid
version numbers.

The `hpccm` command line tool has the `--userarg` option.  Values
specified using this option are inserted into a Python dictionary
named `USERARG` that can be accessed inside a recipe.

```python
from distutils.version import StrictVersion

cuda_version = USERARG.get('cuda', '9.1')
if StrictVersion(cuda_version) < StrictVersion('9.0'):
  raise RuntimeError('invalid CUDA version: {}'.format(cuda_version))
Stage0 += baseimage(image='nvidia/cuda:{}-devel-ubuntu16.04'.format(cuda_version))

ompi_version = USERARG.get('ompi', '3.1.2')
if not StrictVersion(ompi_version):
  raise RuntimeError('invalid OpenMPI version: {}'.format(ompi_version))
Stage0 += openmpi(infiniband=False, version=ompi_version)
```

The versions can be set on the command line assuming the recipe file
is named `userargs.py`.

To use the default values:

```
$ hpccm --recipe userargs.py
```

Generate container specifications for specified version combinations:

```
$ hpccm --recipe userargs.py --userarg cuda=9.0 ompi=1.10.7
$ hpccm --recipe userargs.py --userarg cuda=9.1 ompi=2.1.5
$ hpccm --recipe userargs.py --userarg cuda=9.2
$ hpccm --recipe userargs.py --userarg cuda=10.0 ompi=3.1.3
```

Verify that invalid versions are detected:

```
$ hpccm --recipe userargs.py --userarg cuda=nine_point_zero
ERROR: invalid version number 'nine_point_zero'
```

When using the HPCCM Python module, the `argparse` Python module can
provide equivalent functionality.

```
#!/usr/bin/env python

from __future__ import print_function
from distutils.version import StrictVersion

import argparse
import hpccm
from hpccm.building_blocks import openmpi
from hpccm.primitives import baseimage

parser = argparse.ArgumentParser(description='HPCCM Tutorial')
parser.add_argument('--cuda', type=str, default='9.1',
                    help='CUDA version (default: 9.1)')
parser.add_argument('--format', type=str, default='docker',
                    choices=['docker', 'singularity'],
                    help='Container specification format (default: docker)')
parser.add_argument('--ompi', type=str, default='3.1.2',
                    help='OpenMPI version (default: 3.1.2)')
args = parser.parse_args()

Stage0 = hpccm.Stage()

if StrictVersion(args.cuda) < StrictVersion('9.0'):
  raise RuntimeError('invalid CUDA version: {}'.format(args.cuda))
Stage0 += baseimage(image='nvidia/cuda:{}-devel-ubuntu16.04'.format(args.cuda))

if not StrictVersion(args.ompi):
  raise RuntimeError('invalid OpenMPI version: {}'.format(args.ompi))
Stage0 += openmpi(infiniband=False, version=args.ompi)

hpccm.config.set_container_format(args.format)

print(Stage0)
```

Specifying (and verifying) component versions is just scratching the
surface of this powerful HPCCM capability.

## Multi-stage Recipes

[Multi-stage Docker
builds](https://docs.docker.com/develop/develop-images/multistage-build/)
are a very useful capability that separates the application build step
from the deployment step.  The development toolchain, application
source code, and build artifacts are not necessary when deploying the
built application inside a container.  In fact, they can significantly
and unnecessarily increase the size of the container image.

The `hpccm` command line tool automatically creates 2 stages,
`Stage0`, and `Stage1`.  Most [building
blocks](/docs/building_blocks.md) provide a `runtime` method to
install the corresponding runtime version of a component.

The following recipe builds OpenMPI in the first (build) stage, and
then copies the resulting OpenMPI build into the second (deployment)
stage.  Building block settings defined in the first stage are
automatically reflected in the second stage.

```python
Stage0 += baseimage(image='nvidia/cuda:9.0-devel-centos7')
ompi = openmpi(infiniband=False, prefix='/opt/openmpi')
Stage0 += ompi

Stage1 += baseimage(image='nvidia/cuda:9.0-base-centos7')
Stage1 += ompi.runtime()
```

The [MILC example recipe](/recipes/milc/milc.py) demonstrates the
usefulness of multi-stage recipes.  The Docker container image built
from the first stage only is 5.93 GB, whereas the container image is
only 429 MB when employing the multi-stage build process.  

```
$ wget https://raw.githubusercontent.com/NVIDIA/hpc-container-maker/master/recipes/milc/milc.py
$ hpccm --recipe milc.py --single-stage > Dockerfile.single-stage
$ sudo docker build -t milc:single-stage -f Dockerfile.single-stage .

$ hpccm --recipe milc.py > Dockerfile.multi-stage
$ sudo docker build -t milc:multi-stage -f Dockerfile.multi-stage .

$ docker images --format "{{.Repository}}:{{.Tag}}: {{.Size}}" | grep milc
milc:multi-stage: 429MB
milc:single-stage: 5.93GB
```

The Singularity definition file format and image builder do not
support multi-stage builds.  However, Docker images can be easily
converted to Singularity images so Singularity can also (indirectly)
take advantage of multi-stage builds.

```
$ sudo docker run -t --rm --privileged -v /var/run/docker.sock:/var/run/docker.sock -v /tmp:/output singularityware/docker2singularity milc:multi-stage
...
Singularity container built: /tmp/milc_multi-stage-2018-12-03-c2b47902c8a8.simg
...
```
