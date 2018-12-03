# Getting Started with HPC Container Maker

## Installation

HPCCM can be installed from PyPi.

```
$ sudo pip install hpccm
```

## Using HPCCM

HPCCM can be used as a Python library or via the `hpccm` command line
interface.

### Python Library

The HPCCM Python library is a set of routines to generate container
specification files.

```python
#!/usr/bin/env python

import hpccm

# Set to 'docker' to generate a Dockerfile or set to 'singularity' to
# generate a Singularity defintion file
hpccm.config.set_container_format('docker')

print(hpccm.primitives.baseimage(image='centos:7'))
print(hpccm.building_blocks.gnu())
```

The Python library provides the most flexibility, but you are
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
$ hpccm --recipe *file* --format docker
```

```
$ hpccm --recipe *file* --format singularity
```

HPCCM recipes are Python scripts, so you can incorporate Python code in
the recipe.

### Building Container Images

The HPCCM output is the container specification, so save it to a file.
By convention, the container specification files are named
`Dockerfile` or `Singularity.def`.  To generate a container image, use
your prefered container image builder.

Using [Docker](https://docs.docker.com/engine/reference/commandline/build/):

```
$ sudo docker build -t *tag* -f Dockerfile .
```

Using [Singularity](https://www.sylabs.io/guides/latest/user-guide/build_a_container.html):

```
$ sudo singularity build *image.sif* Singularity.def
```

Other container builders may also be used.

## Next Steps

Several [example recipes](../recipes) are included.

A few [simple examples](../recipes/examples) illustrate some of the
basic concepts.

The ["hpcbase" recipes](../recipes) provide representative HPC
development environments including a compiler, MPI library, and common
HPC libraries.  These recipes are a great starting point for building
an HPC application container.  Choose the recipe with the compiler /
MPI library combination that best matches the application requirements
and add the application specific build instructions.

A few complete [application examples](../recipes) are also provided.

Read the rest of the [documentation](docs/) for more information on
creating recipes, customizing building block behavior, and more.
