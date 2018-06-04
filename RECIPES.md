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
# PGI community edition compiler (18.4)
Stage0.baseimage('nvidia/cuda:9.0-devel')

ospackages = ['make', 'wget']
Stage0 += apt_get(ospackages=ospackages)

p = pgi(eula=True, version='18.4')
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
packages to install.  This building block should only be used on
images that use the Debian package manager (e.g., Ubuntu).

In most cases, the [`packages` building block](#packages) should be
used instead of `apt_get`.

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

The `fftw` building block downloads, configures, builds, and installs
the [FFTW](http://www.fftw.org) component.  Depending on the
parameters, the source will be downloaded from the web (default) or
copied from a source directory in the local build context.

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

### gnu

The `gnu` building block installs the GNU compilers from the upstream
Linux distribution.

As a side effect, a toolchain is created containing the GNU compilers.
The toolchain can be passed to other operations that want to build
using the GNU compilers.

```python
g = gnu()

operation(..., toolchain=g.toolchain, ...)
```

Parameters:

- `cc`: Boolean flag to specify whether to install `gcc`.  The default
  is True.

- `cxx`: Boolean flag to specify whether to install `g++`.  The
  default is True.

- `fortran`: Boolean flag to specify whether to install `gfortran`.
  The default is True.

Methods:

- `runtime(_from='...')`: Generate the set of instructions to install
  the runtime specific components from a build in a previous stage.

Examples:

```python
gnu()
```

```python
g = gnu()
Stage0 += g
...
Stage1 += g.runtime()
```

```python
gnu(fortran=False)
```

### hdf5

The `hdf5` building block downloads, configures, builds, and installs
the [HDF5](http://www.hdfgroup.org) component.  Depending on the
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
  and building.  For Ubuntu, the default values are `file`, `make`,
  `wget`, and `zlib1g-dev`.  For RHEL-based Linux distributions the
  default values are `bzip2`, `file`, `make`, `wget` and `zlib-devel`.

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

### mkl

The `mkl` building block downloads and installs the [Intel Math Kernel
Library](http://software.intel.com/mkl).

You must agree to the [Intel End User License
Agreement](https://software.intel.com/en-us/articles/end-user-license-agreement)
to use this building block.

As a side effect, this building block modifies `LIBRARY_PATH`,
`LD_LIBRARY_PATH`, and other environment variables to include MKL.

Parameters:

- `eula`: By setting this value to `True`, you agree to the [Intel End
  User License
  Agreement](https://software.intel.com/en-us/articles/end-user-license-agreement).
  The default value is `False`.

- `mklvars`: MKL provides an environment script (`mklvars.sh`) to
  setup the MKL environment.  If this value is `True`, the bashrc is
  modified to automatically source this environment script.  However,
  the MKL environment is not automatically available to subsequent
  container image build steps; the environment is available when the
  container image is run.  To set the MKL environment in subsequent
  build steps you can explicitly call `source
  /opt/intel/mkl/bin/mklvars.sh intel64` in each build step.  If this
  value is to set `False`, then the environment is set such that the
  environment is visible to both subsequent container image build
  steps and when the container image is run.  However, the environment
  may differ slightly from that set by `mklvars.sh`.  The default
  value is `True`.

- `ospackages`: List os OS packages to install prior to installing
  MKL.  For Ubuntu, the default values are `apt-transport-https`,
  `ca-certificates`, and `wget`.  For RHEL-based Linux distributions,
  the default is an empty list.

- `version`: The version of MKL to install.  The default value is
  `2018.3-051`.

Methods:

- `runtime(_from='...')`: Generate the set of instructions to install
  the runtime specific components from a build in a previous stage.

Examples:

```python
mkl(eula=True, version='2018.3-051')
```

```python
m = mkl(eula=True)
Stage0 += m
...
Stage1 += m.runtime()
```

### mlnx_ofed

The `mlnx_ofed` building block downloads and installs the [Mellanox
OpenFabrics Enterprise Distribution for
Linux](http://www.mellanox.com/page/products_dyn?product_family=26).

Parameters:

- `oslabel`: The Linux distribution label assigned by Mellanox to the
  tarball.  For Ubuntu, the default value is `ubuntu16.04`.  For
  RHEL-based Linux distributions, the default value is `rhel7.2`.

- `ospackages`: List of OS packages to install prior to installing
  OFED.  For Ubuntu, the default values are `libnl-3-200`,
  `libnl-route-3-200`, `libnuma1`, and `wget`.  For RHEL-based Linux
  distributions, the default values are `libnl`, `libnl3`,
  `numactl-libs`, and `wget`.

- `packages`: List of packages to install from Mellanox OFED.  For
  Ubuntu, the default values are `libibverbs1`, `libibverbs-dev`,
  `libibmad`, `libibmad-devel`, `libibumad`, `libibumad-devel`,
  `libmlx5-1`, and `ibverbs-utils`.  For RHEL-based Linux
  distributions, the default values are `libibverbs`,
  `libibverbs-devel`, `libibverbs-utils`, `libibmad`,
  `libibmad-devel`, `libibumad`, `libibumad-devel`, and `libmlx5`.

- `version`: The version of Mellanox OFED to download.  The default
  value is `3.4-1.0.0.0`.

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

As a side effect, a toolchain is created containing the MPI compiler
wrappers.  The tool can be passed to other operations that want to
build using the MPI compiler wrappers.

```python
mv2 = mvapich2()

operation(..., toolchain=mv2.toolchain, ...)
```

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
  and building.  For Ubuntu, the default values are `byacc`, `file`,
  `openssh-client`, and `wget`.  For RHEL-based Linux distributions,
  the default values are `byacc`, `file`, `make`, `openssh-clients`,
  and `wget`.

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
mvapich2(configure_opts=['--disable-fortran', '--disable-mcast'])
```

```python
mv2 = mvapich2()
Stage0 += mv2
...
Stage1 += mv2.runtime()
```

### mvapich2_gdr

The `mvapich2_gdr` building blocks installs the
[MVAPICH2-GDR](http://mvapich.cse.ohio-state.edu) component.
Depending on the parameters, the package will be downloaded from the
web (default) or copied from the local build context.

MVAPICH2-GDR is distributed as a binary package, so certain
dependencies need to be met and only certain combinations of recipe
components are supported; please refer to the MVAPICH2-GDR
documentation for more information.

The [GNU compiler](#gnu) building block should be installed prior to
this building block.

The [Mellanox OFED](#mlnx_ofed) building block should be installed
prior to this building block.

As a side effect, this building block modifies `PATH` and
`LD_LIBRARY_PATH` to include the MVAPICH2-GDR build.

As a side effect, a toolchain is created containing the MPI compiler
wrappers.  The toolchain can be passed to other operations that want
to build using the MPI compiler wrappers.

```python
mv2 = mvapich2_gdr()

operation(..., toolchain=mv2.toolchain, ...)
```

Parameters:

- `cuda_version`: The version of CUDA the MVAPICH2-GDR package was
  built against.  The version string format is X.Y.  The version
  should match the version of CUDA provided by the base image.  This
  value is ignored if `package` is set.  The default value is `9.0`.

- `mlnx_ofed_version`: The version of Mellanox OFED the MVAPICH2-GDR
  package was built against.  The version string format is X.Y.  The
  version should match the version of Mellanox OFED installed by the
  `mlnx_ofed` building block.  This value is ignored if `package` is
  set.  The default value is `3.4`.

- `ospackages`: List of OS packages to install prior to installation.
  For Ubuntu, the default values are `openssh-client` and `wget`.  For
  RHEL-based Linux distributions, the default values are
  `openssh-clients`, `perl` and `wget`.

- `package`: Path to the package file relative to the local build
  context.  The default value is empty.  If this is defined, the
  package in the local build context will be used rather than
  downloading the package from the web.  The package should correspond
  to the other recipe components (e.g., compiler version, CUDA
  version, Mellanox OFED version).

- `version`: The version of MVAPICH2-GDR to download.  The value is
  ignored if `package` is set.  The default value is `2.3a`.

Methods:

- `runtime(_from='...')`: Generate the set of instructions to install
  the runtime specific components from a build in a previous stage.

Examples:

```python
mvapich2_gdr(version='2.3a')
```

```python
mvapich2_gdr(package='mvapich2-gdr-mcast.cuda9.0.mofed3.4.gnu4.8.5_2.3a-1.el7.centos_amd64.deb')
```

```python
mv2 = mvapich2_gdr()
Stage0 += mv2
...
Stage1 += mv2.runtime()
```

### ofed

The `ofed` building block installs the OpenFabrics Enterprise
Distribution packages that are part of the Linux distribution.

For Ubuntu, the following packages are installed: `dapl2-utils`,
`ibutils`, `ibverbs-utils`, `infiniband-diags`, `libdapl-dev`,
`libibcm-dev`, `libibmad5`, `libibmad-dev`, `libibverbs1`,
`libibverbs-dev`, `libmlx4-1`, `libmlx4-dev`, `libmlx5-1`,
`libmlx5-dev`, `librdmacm1`, `librdmacm-dev`, `opensm`, and
`rdmacm-utils`.

For RHEL-based Linux distributions, the following packages are
installed: `dapl`, `dapl-devel`, `ibutils`, `libibcm`, `libibmad`,
`libibmad-devel`, `libmlx5`, `libibumad`, `libibverbs`,
`libibverbs-utils`, `librdmacm`, `opensm`, `rdma-core`, and
`rdma-core-devel`.

Parameters:

None

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

As a side effect, a toolchain is created containing the MPI compiler
wrappers.  The tool can be passed to other operations that want to
build using the MPI compiler wrappers.

```python
ompi = openmpi()

operation(..., toolchain=ompi.toolchain, ...)
```

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
  and building.  For Ubuntu, the default values are `file`, `hwloc`,
  `openssh-client`, and `wget`.  For RHEL-based Linux distributions,
  the default values are `bzip2`, `file`, `hwloc`, `make`,
  `openssh-clients`, `perl`, and `wget`.

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

### packages

The `packages` building block specifies the set of operating system
packages to install.  Based on the Linux distribution, the building
block invokes either `apt-get` (Ubuntu) or `yum` (RHEL-based).

This building block is preferred over directly using the
[`apt_get`](#apt_get) or [`yum`](#yum) building blocks.

Parameters:

- `apt`: A list of Debian packages to install.  The default is an
  empty list.

- `_epel`: Boolean flag to specify whether to enable the Extra
  Packages for Enterprise Linux (EPEL) repository.  The default is
  False.  This parameter is ignored if the Linux distribution is not
  RHEL-based.

- `ospackages`: A list of packages to install.  The list is used for
   both Ubuntu and RHEL-based Linux distributions, therefore only
   packages with the consistent names across Linux distributions
   should be specified.  This parameter is ignored if `apt` or `yum`
   is specified.  The default value is an empty list.

- `yum`: A list of RPM packages to install.  The default value is an
  empty list.

Examples:

```python
packages(ospackages=['make', 'wget'])
```

```python
packages(apt=['zlib1g-dev'], yum=['zlib-devel'])
```

```python
packages(apt=['python3'], yum=['python34'], _epel=True)
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
  PGI compiler.  For Ubuntu, the default values are `libnuma1` and
  `perl`, and also `wget` (if downloading the PGI compiler rather than
  using a tarball in the local build context).  For RHEL-based Linux
  distributions, the default values are `numactl-libs` and `perl`, and
  also `wget` (if downloading the PGI compiler rather than using a
  tarball in the local build context).

- `system_cuda`: Boolean flag to specify whether the PGI compiler
  should use the system CUDA.  If False, the version(s) of CUDA
  bundled with the PGI compiler will be installed.  The default value
  is False.

- `tarball`: Path to the PGI compiler tarball relative to the local
  build context.  The default value is empty.  If this is defined, the
  tarball in the local build context will be used rather than
  downloading the tarball from the web.

- `version`: The version of the PGI compiler to use.  Note this value
  is currently only used when setting the environment and does not
  control the version of the compiler downloaded.  The default value
  is `18.4`.

Methods:

- `runtime(_from='...')`: Generate the set of instructions to install
  the runtime specific components from a build in a previous stage.

Examples:

```python
pgi(eula=True, version='18.4')
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

### python

The `python` building block installs Python from the upstream Linux
distribution.

Parameters:

- `python2`: Boolean flag to specify whether to install Python version
  2.  The default is True.

- `python3`: Boolean flag to specify whether to install Python version
  3.  The default is True.

Methods:

- `runtime(_from='...')`: Generate the set of instructions to install
  the runtime specific components from a build in a previous stage.

Examples:

```python
python()
```

```python
p = python()
Stage0 += p
...
Stage1 += p.runtime()
```

```python
python(python3=False)
```

### yum

The `yum` building block specifies the set of operating system
packages to install.  This building block should only be used on
images that use the Red Hat package manager (e.g., CentOS).

In most cases, the [`packages` building block](#packages) should be
used instead of `yum`.

Parameters:

- `ospackages`: A list of packages to install.  The default is an
  empty list.

Example:

```python
yum(ospackages=['make', 'wget'])
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

- `_distro': The underlying Linux distribution of the base image.
  Valid values are `centos`, `redhat`, `rhel`, and `ubuntu`.  By
  default, the primitive attempts to figure out the Linux distribution
  by inspecting the image identifier, and falls back to `ubuntu` if
  unable to determine the Linux distribution automatically.

- `image`: The image identifier to use as the base image.  The default
  value is `nvidia/cuda:9.0-devel-ubuntu16.04`

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
