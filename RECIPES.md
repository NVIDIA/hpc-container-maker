# Recipes

Recipes are a container implementation independent way to specify the
steps to construct a container image.  For example, the same recipe
may be used as the basis for both Docker and Singularity containers.

A recipe is structured Python code, which is described below.

The following is simple example that illustrate the basic ideas.
Based on the [Dockerhub CUDA
image](https://hub.docker.com/r/nvidia/cuda/), it installs some basic
OS packages, the PGI compiler, and OpenMPI.  This single recipe can be
converted into a Dockerfile or a Singularity recipe file simply by
specifying the `--format` command line option.

```python
# OpenMPI 3.0.0, with InfiniBand and CUDA enabled, using the latest
# PGI community edition compiler (17.10)
Stage0.baseimage('nvidia/cuda:9.0-devel')

ospackages = ['make', 'wget']
Stage0 += apt_get(ospackages=ospackages)

p = pgi(eula=True, version='17.10')
Stage0 += p

# Use the PGI toolchain to build OpenMPI                                
Stage0 += openmpi(toolchain=p.toolchain, version='3.0.0')
```

Please see the [recipes](recipes/) sub-directory for additional
working examples.

# Quick Start

If you are already familiar with writing Dockerfiles or Singularity
recipe files, this section will answer the question "How do I express
X in a recipe?"

Please see the [Reference](#Reference) section below for a complete
description of the recipe syntax.

Note that for several common operations, such as GNU Autotools
configure / make workflows, and common core HPC components, such as
[FFTW](#fftw), [OFED](#ofed), [OpenMPI](#openmpi), etc., using the
provided [templates](#Templates) and [building blocks](#Building
Blocks) are *strongly* recommended over directly translating an
existing Dockerfile or Singularity recipe file using
[primitives](#Primitives).

## Docker

| Docker                      | Recipe                                        |
| --------------------------- | --------------------------------------------- |
| `FROM image:tag`            | `baseimage(image='image:tag')`                |
| `FROM image:tag AS build`   | `baseimage(image='image:tag', AS='build')`    |
| `COPY foo bar`              | `copy(src='foo', dest='bar')`                 |
| `COPY a b c z/`             | `copy(src=['a', 'b', 'c'], dest='z/')`        |
| `RUN a`                     | `shell(commands=['a'])`                       |
| `RUN a && b && c`           | `shell(commands=['a', 'b', 'c'])`             |
| `RUN apt-get install a b c` | `apt_get(ospackages=['a', 'b', 'c'])`         |
| `ENV FOO=BAR`               | `environment(variables={'FOO': 'BAR'})`       |
| `ENV A=B C=D`               | `environment(variables={'A': 'B', 'C': 'D'})` |
| `WORKDIR /path/to`          | `workdir(directory='/path/to')`               |
| `LABEL FOO=BAR`             | `label(metadata={'FOO': 'BAR'})`              |

As a last resort, use the `raw` primitive to express a Dockerfile
concept with no direct recipe equivalent.

```
raw(docker='MAINTAINER jane@doe')
```

## Singularity

| Singularity                 | Recipe                                        |
| --------------------------- | --------------------------------------------- |
| `BootStrap: docker`<br>`From: image:tag` | `baseimage(image='image:tag')`   |
| `%files`<br>`foo bar`                    | `copy(src='foo', dest='bar')`    |
| `%post`<br>`a`                           | `shell(commands=['a'])`          |
| `%post`<br>`a`<br>`b`<br>`c`       | `shell(commands=['a', 'b', 'c'])`      |
| `%post`<br>`apt-get install a b c` | `apt_get(ospackages=['a', 'b', 'c'])`  |
| `%environment`<br>`export FOO=BAR` | `environment(variables={'FOO': 'BAR'})` |
| `%post`<br>`mkdir -p /path/to`<br>`cd /path/to` | `workdir(directory='/path/to')` |
| `%labels`<br>`foo bar`                   | `label(metadata={'foo': 'bar'})` |

As a last resort, use the `raw` primitive to express a Singularity
recipe file concept with no direct recipe equivalent.

```
raw(singularity='%labels\n   Maintainer jane@doe')
```

# Reference

## Structure

A recipe consists of one or more stages.  A basic recipe will contain
a single stage.  Stages are the same concept as [Docker multistage
builds](https://docs.docker.com/develop/develop-images/multistage-build/).

A stage consists of one or more operations.  A basic recipe will contain
several operations.

The aliases `Stage0` and `Stage1` are automatically created by
Container Maker.  Initially, both stages are empty.  Within a stage,
operations are evaluated in the same order they are added.

### Examples

The following recipe example would construct a container specification
file with operation A followed by operation B.

```python
Stage0 += A
Stage0 += B
```

The following recipe example illustrates 2 stages.  The container
specification file would contain, in order, contain operations A, B,
Y, and Z.

```python
Stage0 += A
Stage1 += Y
Stage1 += Z
Stage0 += B
```

## Stages

### Methods

The `baseimage` method may be used to set the base image for the
Stage.

This method is essentially equivalent to the `baseimage` building
block, but this method guarantees that the base image instruction will
be the first instruction in the stage.

For example, the following Dockerfile and Singularity recipe files
would be generated from this recipe.

| Recipe                          | Docker           | Singularity |
| ------------------------------- | ---------------- | ----------- |
| `Stage0.baseimage('image:tag')` | `FROM image:tag` | `Bootstrap: docker`<br>`From: image:tag` |

### Properties

The `name` property may be used to assign a name to the Stage.  If
set, the name is used when generating Dockerfiles as the name of the
stage.  The name is ignored when generating Singularity recipe files.

For example, the following Dockerfile would be generated from this
recipe.

| Recipe                          | Docker           | Singularity |
| ------------------------------- | ---------------- | ----------- |
| `Stage0.name = 'devel'`<br>`Stage0.baseimage('image:tag')` | `FROM image:tag AS devel` | `Bootstrap: docker`<br>`From: image:tag` |

The name may be referenced in subsequent stages to copy files, etc.

```python
Stage0.name = '...'
...
Stage1 += copy(_from=Stage0.name, src='...', dest='...')
```

## User arguments

Users may specify one or more parameters via the `--userarg` command
line option, e.g., `--userarg a=b c=d`.

The user arguments are passed to the recipe in the form a `USERARG`
dictionary.  A recipe may behave conditionally based on the value
of a user argument.

Example:

```python
a = USERARG.get('a', 'default')
if a == 'b':
  ...
else:
  ...
```

## Building Blocks

Building blocks are high level abstractions of the multiple steps
needed to containerize a component.

Where available, building blocks should always be used rather than
recreating the equivalent steps with lower level concepts.

Building blocks are automatically included in the recipe namespace.

### apt_get

The `apt_get` building block specifies the set of operating system
packages to install.  This building block should only be on images
that use the Debian package manager (e.g., Ubuntu).

Parameters:

- `ospackages`: A list of packages to install.  The default is an
  empty list.

Example:

```python
apt_get(ospackages=['make', 'wget'])
```

### cmake

The `cmake` building block downloads and installs the
[CMake](https://cmake.org) component.

Parameters:

- `eula`: By setting this value to `True`, you agree to the [CMake
  End-User License
  Agreement](https://gitlab.kitware.com/cmake/cmake/raw/master/Copyright.txt).
  The default value is `False`.

- `ospackages`: List of OS packages to install prior to installing.
  The default value is `wget`.

- `prefix`: The top level install location.  The default value is
  `/usr/local`.

- `version`: The version of CMake to download.  The default value is
  `3.11.1`.

Examples:

```python
cmake(eula=True)
```

```python
cmake(eula=True, version='3.10.3')
```

### fftw

The `fftw` building block down configures, builds, and installs the
[FFTW](http://www.fftw.org) component.  Depending on the parameters,
the source will be downloaded from the web (default) or copied from a
source directory in the local build context.

As a side effect, this building block modifies `LD_LIBRARY_PATH` to
include the FFTW build.

Parameters:

- `check`: Boolean flag to specify whether the `make check` step
  should be performed.  The default is False.

- `configure_opts`: List of options to pass to `configure`.  The
  default values are `--enable-shared`, `--enable-openmp`,
  `--enable-threads`, and `--enable-sse2`.

- `directory`: Path to the unpackaged source directory relative to the
  local build context.  The default value is empty.  If this is
  defined, the source in the local build context will be used rather
  than downloading the source from the web.

- `ospackages`: List of OS packages to install prior to configuring
  and building.  The default values are `file`, `make`, and `wget`.

- `prefix`: The top level install location.  The default value is
  `/usr/local/fftw`.

- `toolchain`: The toolchain object.  This should be used if
  non-default compilers or other toolchain options are needed.  The
  default is empty.

- `version`: The version of FFTW source to download.  This value is
  ignored if `directory` is set.  The default value is `3.3.7`.

Methods:

- `runtime(_from='...')`: Generate the set of instructions to install
  the runtime specific components from a build in a previous stage.

Examples:

```python
fftw(prefix='/opt/fftw/3.3.7', version='3.3.7')
```

```python
fftw(directory='sources/fftw-3.3.7')
```

```python
p = pgi(eula=True)
fftw(toolchain=p.toolchain)
```

```python
fftw(check=True, configure_opts=['--enable-shared', '--enable-threads',
                                 '--enable-sse2', '--enable-avx'])
```

```python
f = fftw()
Stage0 += f
...
Stage1 += f.runtime()
```

### hdf5

The `hdf5` building block down configures, builds, and installs the
[HDF5](http://www.hdfgroup.org) component.  Depending on the
parameters, the source will be downloaded from the web (default) or
copied from a source directory in the local build context.

As a side effect, this building block modifies `PATH`,
`LD_LIBRARY_PATH` to include the HDF5 build, and sets `HDF5_DIR`.

Parameters:

- `check`: Boolean flag to specify whether the `make check` step
  should be performed.  The default is False.

- `configure_opts`: List of options to pass to `configure`.  The
  default values are `--enable-cxx` and `--enable-fortran`.

- `directory`: Path to the unpackaged source directory relative to the
  local build context.  The default value is empty.  If this is
  defined, the source in the local build context will be used rather
  than downloading the source from the web.

- `ospackages`: List of OS packages to install prior to configuring
  and building.  The default values are `file`, `make`, `wget`, and
  `zlib1g-dev`.

- `prefix`: The top level install location.  The default value is
  `/usr/local/hdf5`.

- `toolchain`: The toolchain object.  This should be used if
  non-default compilers or other toolchain options are needed.  The
  default is empty.

- `version`: The version of HDF5 source to download.  This value is
  ignored if `directory` is set.  The default value is `1.10.1`.

Methods:

- `runtime(_from='...')`: Generate the set of instructions to install
  the runtime specific components from a build in a previous stage.

Example:

```python
hdf5(prefix='/opt/hdf5/1.10.1', version='1.10.1')
```

```python
hdf5(directory='sources/hdf5-1.10.1')
```

```python
p = pgi(eula=True)
hdf5(toolchain=p.toolchain)
```

```python
hdf5(check=True, configure_opts=['--enable-cxx', '--enable-fortran',
                                 '--enable-profiling=yes'])
```

```python
h = hdf5()
Stage0 += h
...
Stage1 += h.runtime()
```

### mlnx_ofed

The `mlnx_ofed` building block downloads and installs the [Mellanox
OpenFabrics Enterprise Distribution for
Linux](http://www.mellanox.com/page/products_dyn?product_family=26).

Parameters:

- `ospackages`: List of OS packages to install prior to installing
  OFED.  The default values are `libnl-3-200`, `libnl-route-3-200`,
  `libnuma1`, and `wget`.

- `packages`: List of packages to install from Mellanox OFED.  The
  default values are `libibverbs1`, `libibverbs-dev`, `libmlx5-1`, and
  `ibverbs-utils`.

- `version`: The version of Mellanox OFED to download.  The default
  value is `3.4-1.0.0.0`.  Only versions that provide an Ubuntu 16.04
  package should be specified.

Methods:

- `runtime(_from='...')`: Generate the set of instructions to install
   the runtime specific components from a build in a previous stage.

Examples:

```python
mlnx_ofed(version='4.2-1.0.0.0')
```

```python
mofed = mlnx_ofed()
Stage0 += mofed
...
Stage1 += mofed.runtime()
```

### mvapich2

The `mvapich2` building block configures, builds, and installs the
[MVAPICH2](http://mvapich.cse.ohio-state.edu) component.  Depending on
the parameters, the source will be downloaded from the web (default)
or copied from a source directory in the local build context.

An InfiniBand building block ([OFED](#ofed) or [Mellanox
OFED](#mlnx_ofed)) should be installed prior to this building block.

As a side effect, this building block modifies `PATH` and
`LD_LIBRARY_PATH` to include the MVAPICH2 build.

Parameters:

- `check`: Boolean flag to specify whether the `make check` step
  should be performed.  The default is False.

- `configure_opts`: List of options to pass to `configure`.  The
  default values are `--disable-mcast`.

- `cuda`: Boolean flag to control whether a CUDA aware build is
  performed.  If True, adds `--with-cuda` to the list of `configure`
  options, otherwise adds `--without-cuda`.  If the toolchain
  specifies `CUDA_HOME`, then that path is used.  The default value is
  True.

- `directory`: Path to the unpackaged source directory relative to the
  local build context.  The default value is empty.  If this is
  defined, the source in the local build context will be used rather
  than downloading the source from the web.

- `ospackages`: List of OS packages to install prior to configuring
  and building.  The default values are `byacc`, `file`,
  `openssh-client`, and `wget`.

- `prefix`: The top level install location.  The default value is
  `/usr/local/mvapich2`.

- `toolchain`: The toolchain object.  This should be used if
  non-default compilers or other toolchain options are needed.  The
  default is empty.

- `version`: The version of MVAPICH2 source to download.  This value
  is ignored if `directory` is set.  The default value is `2.3b`.

Methods:

- `runtime(_from='...')`: Generate the set of instructions to install
  the runtime specific components from a build in a previous stage.

Examples:

```python
mvapich2(cuda=False, prefix='/opt/mvapich2/2.3a', version='2.3a')
```

```python
mvapich2(directory='sources/mvapich2-2.3b')
```

```python
p = pgi()
mvapich2(toolchain=p.toolchain)
```

```python
mvapich2(configure_opts=['--disable-fortran', '--disable-mcast'],
         ospackages=['byacc','file','openssh-client','wget'])
```

```python
mv2 = mvapich2()
Stage0 += mv2
...
Stage1 += mv2.runtime()
```

### ofed

The `ofed` building block installs the OpenFabrics Enterprise
Distribution packages that are part of the Linux distribution.

Parameters:

- `ospackages`: List of OS packages to install.  The default values
  are `dapl2-utils`, `ibutils`, `ibverbs-utils`, `infiniband-diags`,
  `libdapl-dev`, `libibcm-dev`, `libibmad5`, `libibmad-dev`,
  `libibverbs1`, `libibverbs-dev`, `libmlx4-1`, `libmlx4-dev`,
  `libmlx5-1`, `libmlx5-dev`, `librdmacm1`, `librdmacm-dev`, `opensm`,
  and `rdmacm-utils`.

Methods:

- `runtime(_from='...')`: Generate the set of instructions to install
   the runtime specific components from a build in a previous stage.

Examples:

```python
ofed()
```

```python
o = ofed()
Stage0 += o
...
Stage1 += o.runtime()
```

### openmpi

The `openmpi` building block configures, builds, and installs the
[OpenMPI](https://www.open-mpi.org) component.  Depending on the
parameters, the source will be downloaded from the web (default) or
copied from a source directory in the local build context.

As a side effect, this building block modifies `PATH` and
`LD_LIBRARY_PATH` to include the OpenMPI build.

Parameters:

- `check`: Boolean flag to specify whether the `make check` step
  should be performed.  The default is False.

- `configure_opts`: List of options to pass to `configure`.  The
  default values are `--disable-getpwuid` and
  `--enable-orterun-prefix-by-default`.

- `cuda`: Boolean flag to control whether a CUDA aware build is
  performed.  If True, adds `--with-cuda` to the list of `configure`
  options, otherwise adds `--without-cuda`.  If the toolchain
  specifies `CUDA_HOME`, then that path is used.  The default value is
  True.

- `directory`: Path to the unpackaged source directory relative to the
  local build context.  The default value is empty.  If this is
  defined, the source in the local build context will be used rather
  than downloading the source from the web.

- `infiniband`: Boolean flag to control whether InfiniBand
  capabilities are included.  If True, adds `--with-verbs` to the list
  of `configure` options, otherwise adds `--without-verbs`.  The
  default value is True.

- `ospackages`: List of OS packages to install prior to configuring
  and building.  The default values are `file`, `hwloc`,
  `openssh-client`, and `wget`.

- `prefix`: The top level install location.  The default value is
  `/usr/local/openmpi`.

- `toolchain`: The toolchain object.  This should be used if
  non-default compilers or other toolchain options are needed.  The
  default is empty.

- `version`: The version of OpenMPI source to download.  This value is
  ignored if `directory` is set.  The default value is `3.0.0`.

Methods:

- `runtime(_from='...')`: Generate the set of instructions to install
  the runtime specific components from a build in a previous stage.

Examples:

```python
openmpi(cuda=False, infiniband=False, prefix='/opt/openmpi/2.1.2',
        version='2.1.2')
```

```python
openmpi(directory='sources/openmpi-3.0.0')
```

```python
p = pgi(eula=True)
openmpi(toolchain=p.toolchain)
```

```python
openmpi(configure_opts=['--disable-getpwuid', '--with-slurm'],
        ospackages=['file','hwloc','libslurm-dev'])
```

```python
ompi = openmpi()
Stage0 += ompi
...
Stage1 += ompi.runtime()
```

### pgi

The `pgi` building block downloads and installs the PGI compiler.
Currently, the only option is to install the latest community edition.

You must agree to the [PGI End-User License
Agreement](https://www.pgroup.com/doc/LICENSE.txt) to use this
building block.

As a side effect, this building block modifies `PATH` and
`LD_LIBRARY_PATH` to include the PGI compiler.

As a side effect, a toolchain is created containing the PGI compilers.
The tool can be passed to other operations that want to build using
the PGI compilers.

```python
p = pgi(eula=True)

operation(..., toolchain=p.toolchain, ...)
```

Parameters:

- `eula`: By setting this value to `True`, you agree to the [PGI
  End-User License Agreement](https://www.pgroup.com/doc/LICENSE.txt).
  The default value is `False`.

- `ospackages`: List of OS packages to install prior to installing the
  PGI compiler.  The default values are `libnuma1`, and `wget` (if
  downloading the PGI compiler rather than using a tarball in the
  local build context).

- `tarball`: Path to the PGI compiler tarball relative to the local
  build context.  The default value is empty.  If this is defined, the
  tarball in the local build context will be used rather than
  downloading the tarball from the web.

- `version`: The version of the PGI compiler to use.  Note this value
  is currently only used when setting the environment and does not
  control the version of the compiler downloaded.  The default value
  is `17.10`.

Methods:

- `runtime(_from='...')`: Generate the set of instructions to install
  the runtime specific components from a build in a previous stage.

Examples:

```python
pgi(eula=True, version='2017')
```

```python
p = pgi(eula=True)
Stage0 += p
...
Stage1 += p.runtime()
```

```python
pgi(eula=True, tarball='pgilinux-2017-1710-x86_64.tar.gz')
```

## Templates

Templates are abstractions of common operations, such as downloading
files, configuring and making source packages distributed with
autotools, working with archives, and controlling the toolchain.

Templates are not automatically included in the recipe namespace.  The
`hpccm` prefix must be used when referring to a template in a recipe.

- `ConfigureMake`: Configure and make packages from source

- `git`: Clone git repositories

- `sed`: Modify files

- `tar`: Work with tarball files

- `toolchain`: Development toolchain environment

- `wget`: Download files

## Primitives

Primitives are the low level implementation of specific container
instructions.  Generally, primitives map directly to a Docker or
Singularity concept, but express the concept in a container
implementation neutral way.  Since primitives map to multiple
container implementations, they sometimes reflect a 'lowest common
denominator' set of capabilities.

### baseimage

The `baseimage` primitive defines the base image to be used.

Parameters:

- `_as`: Name for the build stage (Docker specific).  The default
  value is empty.

- `image`: The image identifier to use as the base image.  The default
  value is `nvcr.io/nvidia/cuda:9.0-cudnn7-devel-ubuntu16.04`

- `AS`: Name for the build stage (Docker specific).  The default value
  is empty.  This parameter is deprecated; use `_as` instead.

Example:

```python
baseimage(image='nvidia/cuda:9.1-devel')
```

### blob

The `blob` primitive inserts a file, without modification, into the
corresponding place in the container specification file.  If a
relative path is specified, the path is relative to current directory.

Generally, the blob should be functionally equivalent for each
container format.

Wherever possible, the blob primitive should be avoided and other,
more portable, operations should be used instead.

Parameters:

- `docker`: Path to the file containing the Dockerfile blob (Docker
  specific).

- `singularity`: Path to the file containing the Singularity blob
  (Singularity specific).

Example:

```python
blob(docker='path/to/foo.docker', singularity='path/to/foo.singularity')
```

### comment

The `comment` primitive inserts a comment into the corresponding
place in the container specification file.

Parameters:

- `reformat`: Boolean flag to specify whether the comment string
  should be wrapped to fit into lines not exceeding 80 characters.
  The default is True.

Example:

```python
comment('libfoo version X.Y')
```

### copy

The `copy` primitive copies files, typically from the host to the
container image.

Parameters:

- `dest`: Path in the container image to copy the file(s)

- `src`: A file, or a list of files, to copy

- `_from`: Set the source location to a previous build stage rather
  than the host filesystem (Docker specific).

Examples:

```python
copy(src='component', dest='/opt/component')
```

```python
copy(src=['a', 'b', 'c'], dest='/tmp')
```

### environment

The `environment` primitive sets the corresponding environment
variables.  Note, for Singularity, this primitive may set environment
variables for the container runtime but not for the container build
process (see this
[rationale](https://github.com/singularityware/singularity/issues/1053)).
See the `_export` parameter for more information.

Parameters:

- `_export`: A Boolean flag to specify whether the environment should
  also be set for the Singularity build context (Singularity
  specific).  Variables defined in the Singularity `%environment`
  section are only defined when the container is run and not for
  subsequent build steps (unlike the analogous Docker `ENV`
  instruction).  If this flag is true, then in addition to the
  `%environment` section, a identical `%post` section is generated to
  export the variables for subsequent build steps.  The default value
  is True.

- `variables`: A dictionary of key / value pairs.  The default is an
  empty dictionary.

Example:

```python
environment(variables={'PATH': '/usr/local/bin:$PATH'})
```

### label

The `label` primitive sets container metadata.

Parameters:

- `metadata`: A dictionary of key / value pairs.  The default is an
  empty dictionary.

Example:

```python
label(metadata={'maintainer': 'jane@doe'})
```

### raw

The `raw` primitive inserts the specified string, without
modification, into the corresponding place in the container
specification file.

Generally, the string should be functionally equivalent for each
container format.

Wherever possible, the raw primitive should be avoided and other, more
portable, primitives should be used instead.

Parameters:

- `docker`: String containing the Dockerfile instruction (Docker
  specific).

- `singularity`: String containing the Singularity instruction
  (Singularity specific).

Example:

```python
raw(docker='COPY --from=0 /usr/local/openmpi /usr/local/openmpi',
    singularity='# no equivalent to --from')
```

### shell

The `shell` primitive specifies a series of shell commands to execute.

Parameters:

- `commands`: A list of commands to execute.  The default is an empty
  list.

Example:

```python
shell(commands=['cd /path/to/src', './configure', 'make install'])
```

### workdir

The `workdir` primitive sets the working directory for any
subsequent operations.  As a side effect, if the directory does not
exist, it is created.

Parameters:

- `directory`: The directory path.

Example:

```python
workdir(directory='/path/to/directory')
```
