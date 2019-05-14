# HPC Container Maker Workflows

HPC Container Maker enables three workflows for creating HPC
application container images.

## Application Recipes

The [MPI Bandwidth example](/recipes/mpi_bandwidth.py) shows how the
entire specification of an application container image can be
expressed as a HPCCM recipe.  Examples are also included for
[GROMACS](/recipes/gromacs/gromacs.py) and
[MILC](/recipes/milc/milc.py).

The GROMACS and MILC recipes demonstrate how to use [multi-stage
builds](/docs/recipes.md#multi-stage-recipes) to minimize the
size of the resulting container image.  The first stage includes the
required building blocks and GROMACS source code and then builds the
application binary.  Build artifacts such as the application source
code, compiler, and development versions of the software toolchain are
part of the image at this stage.  Since only the final application
binary and its runtime dependencies are needed when deploying the
container image, the container image size can potentially be reduced
significantly.  The second stage uses a runtime version of the CUDA
base image and copies the application binary and the required runtime
dependencies from the first stage to generate a significantly smaller
container image.  HPCCM building blocks provide a method to easily
copy the runtime from the first stage into the second stage.

This workflow is the most portable since the HPCCM recipe can be used
to generate either a Dockerfile or Singularity definition file, and is
the easiest to maintain.

## Base Image Generation

On a bare metal system using environment modules, the typical workflow
is to first setup the necessary software environment by loading the
appropriate modules.  With the proper software environment loaded, an
application can then be built or run.

This "base" software environment is analogous to the base image used
when building a container image.  A base image with the proper set of
HPC software components present can be used as the starting point for
building an application container image.

HPCCM includes [base recipes](/recipes) for all combinations of the
Ubuntu and CentOS Linux distributions, the GNU and PGI compilers, and
the OpenMPI and MVAPICH2 MPI libraries, plus commonly used software
components such as the Mellanox OpenFabrics Enterprise Distribution,
Python, FFTW, and HDF5.  The provided base recipe can be easily
customized to change component versions or add or subtract building
blocks.

For example:

```
$ wget https://raw.githubusercontent.com/NVIDIA/hpc-container-maker/master/recipes/hpcbase-gnu-openmpi.py
$ hpccm --recipe hpcbase-gnu-openmpi.py > Dockerfile
$ sudo docker build -t hpcbase -f Dockerfile .
```

The `hpcbase` image, with the software development environment, can now
be used in a Dockerfile or Singularity definition file as the base image
for building an application container image.

```
FROM hpcbase

# Application build instructions
...
```

```
BootStrap: docker
From: hpcbase

# Application build instructions
...
```

## Template Generation

Instead of going through the intermediate step of building a base
image with the necessary HPC software components, the container
specification file produced by HPCCM can be extended directly to
include the application build instructions.  In other words, HPCCM
generates the boilerplate container specification syntax to install
the necessary HPC software components with the application specific
content appended by the user.  The drawback to this approach is that
it may be cumbersome to incorporate future HPCCM building block
improvements.
