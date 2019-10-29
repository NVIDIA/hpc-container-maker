# Getting Started with HPC Container Maker

## Installation

HPCCM can be installed from [PyPi](https://pypi.org/project/hpccm/)
or [Conda](https://anaconda.org/conda-forge/hpccm).

```
$ sudo pip install hpccm
```

```
$ conda install -c conda-forge hpccm
```

## Using HPCCM

HPCCM can be used as a Python module or via the `hpccm` command line
interface.

### Python Module

The HPCCM Python module is a set of routines to generate container
specification files.

```python
#!/usr/bin/env python

import hpccm

# Set to 'docker' to generate a Dockerfile or set to 'singularity' to
# generate a Singularity definition file
hpccm.config.set_container_format('docker')

print(hpccm.primitives.baseimage(image='centos:7'))
print(hpccm.building_blocks.gnu())
```

The Python module provides the most flexibility, but you are
responsible for managing input and output.

### Command Line Tool

The `hpccm` command line tool processes HPCCM recipe files to generate
container specification files.

```python
Stage0 += baseimage(image='centos:7')
Stage0 += gnu()
```

The command line tool manages input and output for you.

```
$ hpccm --recipe <recipe_file> --format docker
```

```
$ hpccm --recipe <recipe_file> --format singularity
```

HPCCM recipes are Python scripts, so you can incorporate Python code in
the recipe.

### Building Container Images

The HPCCM output is the container specification, so save the output to
a file.  By convention, the container specification files are named
`Dockerfile` or `Singularity.def` for Docker and Singularity,
respectively.  To generate a container image, use your preferred
container image builder.

Using [Docker](https://docs.docker.com/engine/reference/commandline/build/):

```
$ hpccm --recipe <recipe.py> --format docker > Dockerfile
$ sudo docker build -t <tag> -f Dockerfile .
```

Using [Singularity](https://www.sylabs.io/guides/latest/user-guide/build_a_container.html):

```
$ hpccm --recipe <recipe.py> --format singularity > Singularity.def
$ sudo singularity build <image_file.sif> Singularity.def
```

Other container builders that understand Dockerfiles or Singularity
definition files may also be used.

A bash script can also be generated from a recipe:

```
$ hpccm --recipe <recipe.py> --format bash > script.sh
```

## Next Steps

Go through the [tutorial](/docs/tutorial.md) for some more in depth
examples.

A few [simple examples](/recipes/examples) are included to illustrate
some of the basic concepts.

Several [example recipes](/recipes) are also included.

The "hpcbase" recipes provide representative HPC development
environments including a compiler, MPI library, and common HPC
libraries.  These recipes are a great starting point for building an
HPC application container.  Choose the recipe with the compiler / MPI
library combination that best matches the application requirements and
add the application specific build instructions.

A few complete application examples are also provided, including
[GROMACS](/recipes/gromacs/gromacs.py), [MILC](/recipes/milc/milc.py),
and [MPI Bandwidth](/recipes/mpi_bandwidth.py).

Read the rest of the [documentation](/docs) for more information on
creating recipes, customizing building block behavior, the API
reference, and more.
