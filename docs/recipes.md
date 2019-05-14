# HPC Container Maker Recipes

Recipes are a container implementation independent way to specify the
steps to construct a container image.  For example, the same HPCCM
recipe may be used as the basis for both Docker and Singularity
container images.

A HPCCM recipe is Python code.  A recipe uses HPCCM [building
blocks](/docs/building_blocks.md) and
[primitives](/docs/primitives.md), as well as other Python code to
specify the content of a container image.  Since a HPCCM recipe is
Python code, it is possible to create dynamic recipes depending on
validated user input.  A single HPCCM recipe can generate multiple
container images.

This simple HPCCM recipe uses the `baseimage` HPCCM primitive to
specify the container base image and the `gnu` HPCCM building block is
install the GNU compiler suite.

```python
Stage0 += baseimage(image='centos:7')
Stage0 += gnu()
```

_Note_: `Stage0` refers to the first stage of a [multi-stage
build](https://docs.docker.com/develop/develop-images/multistage-build/).
Multi-stage builds are a technique that can significantly reduce the
size of container images.  This section will not use multi-stage
builds, so the `Stage0` prefix can be considered boilerplate.  See the
section on [multi-stage recipes](#multi-stage-recipes) for more
information.

The `hpccm` command line tool processes recipes and generates the
corresponding Dockerfile or Singularity definition file.

```
$ hpccm --recipe simple.py
FROM centos:7

# GNU compiler
RUN yum install -y \
        gcc \
        gcc-c++ \
        gcc-gfortran && \
    rm -rf /var/cache/yum/*
```

```
$ hpccm --recipe simple.py --format singularity
BootStrap: docker
From: centos:7
%post
    . /.singularity.d/env/10-docker*.sh

# GNU compiler
%post
    yum install -y \
        gcc \
        gcc-c++ \
        gcc-gfortran
    rm -rf /var/cache/yum/*
```

The HPCCM output is the container specification, so save the output to
a file.  By convention, the container specification files are named
`Dockerfile` or `Singularity.def` for Docker and Singularity,
respectively.  To generate a container image, use your preferred
container image builder.

Using [Docker](https://docs.docker.com/engine/reference/commandline/build/):

```
$ hpccm --recipe simple.py --format docker > Dockerfile
$ sudo docker build -t simple -f Dockerfile .
```

Using [Singularity](https://www.sylabs.io/guides/latest/user-guide/build_a_container.html):

```
$ hpccm --recipe simple.py --format singularity > Singularity.def
$ sudo singularity build simple.sif Singularity.def
```

## Building Blocks

A key feature of HPCCM is its set of [building
blocks](/docs/building_blocks.md), high-level abstractions of key HPC
software components. Building blocks are roughly equivalent to
environment modules, except that building blocks are configurable and
composable.

HPCCM building blocks are Linux distribution aware.  The output of a
building block will reflect the Linux distribution of the base image.
Ubuntu and RedHat derived distributions (e.g., CentOS) are supported.
For example, if the base image is derived from the Ubuntu Linux
distribution, the apt package manager is used to install any required
packages.  However, if the base image is derived from CentOS, the yum
package manager would be used instead.  The base image Linux
distribution detection is automatic and normally requires no action by
the user.

Most building blocks also have [configuration
options](/docs/building_blocks.md) to enable customization.  For
instance, the [openmpi building
block](/docs/building_blocks.md#openmpi) has options to specify the
version, the installation path, the compiler toolchain to use, whether
to enable CUDA and InfiniBand support, and so on.  Reasonable defaults
are set so configuration is usually optional.

Some building blocks may require a license to use.  In those cases,
HPCCM expects the user to provide a valid license and the license
information can be specified via a building block configuration
option.  By using [multi-stage recipes](#multi-stage-recipes),
licensed software can be used to build an application without needing
to redistribute the licensed software or the license itself.

## Primitives

While the container specification file syntax may differ depending on
the container runtime, the same types of operations are performed,
e.g., executing shell commands, copying files into the container
image, setting the environment, etc.  HPCCM
[primitives](/docs/primitives.md) are wrappers around these basic
operations that translate the operation into the corresponding
container specific syntax.  All the building blocks are implemented on
top of primitives to simplify supporting multiple container
specification output formats.  Where a building block is available it
should be used instead of the primitive equivalent.

Some key primitive operations, and their
[Dockerfile](https://docs.docker.com/engine/reference/builder/) and
[Singularity definition
file](https://www.sylabs.io/guides/latest/user-guide/quick_start.html#singularity-definition-files)
equivalents are shown in the following table.  Please refer to the
[primitives](/docs/primitives.md) documentation for the complete list
of primitives and their configuration options.

| Primitive                                     | Docker                      | Singularity                 |
| --------------------------------------------- | --------------------------- | --------------------------- |
| `baseimage(image='image:tag')`                | `FROM image:tag`            | `BootStrap: docker`<br>`From: image:tag` |
| `copy(src='foo', dest='bar')`                 | `COPY foo bar`              | `%files`<br>`foo bar`                    |
| `copy(src=['a', 'b', 'c'], dest='z/')`        | `COPY a b c z/`             | `%files`<br>`a z/`<br>`b z/`<br>`c z/`   |
| `shell(commands=['a'])`                       | `RUN a`                     | `%post`<br>`a`                           |
| `shell(commands=['a', 'b', 'c'])`             | `RUN a && b && c`           | `%post`<br>`a`<br>`b`<br>`c`             |
| `environment(variables={'FOO': 'BAR'})`       | `ENV FOO=BAR`               | `%environment`<br>`export FOO=BAR`<br>`%post`<br>`export FOO=BAR` |
| `environment(variables={'A': 'B', 'C': 'D'}, _export=False)` | `ENV A=B C=D`               | `%environment`<br>`export A=B`<br>`export C=D` |
| `workdir(directory='/path/to')`               | `WORKDIR /path/to`          | `%post`<br>`mkdir -p /path/to`<br>`cd /path/to` |
| `label(metadata={'FOO': 'BAR'})`              | `LABEL FOO=BAR`             | `%labels`<br>`foo bar`                   |

Primitives also hide many of the differences between the Docker and
Singularity container image build processes so that behavior is
consistent regardless of the output configuration specification
format.  For example, the Dockerfile `ENV` instruction sets
environment variables immediately, i.e., the value of an environment
variable can be used in any subsequent instructions, while the
Singularity `%environment` block sets environment variables only when
the container is running.  Therefore the `environment` primitive
generates an additional Singularity `%post` block by default (the
behavior can be disabled with a [configuration
option](/docs/primitives.md#environment).)

## Templates

Some operations are very common and invoked by multiple building
blocks, such as cloning a git repository or executing the configure /
make / make install workflow.  HPCCM templates abstract these basic
operations for consistency and to avoid code duplication.

Templates are primarily intended to be used by building blocks and
thus are not exported by default for use in recipes.  However,
templates can be manually imported and used in recipes, e.g., the
[MILC](/recipes/milc/milc.py) recipe.

## User Arguments

Using Python to express container specifications is one of the key
features of HPCCM.  HPCCM recipes can process user input to generate
multiple container specification permutations from the same source
code.  Because of the flexibility of Python, HPCCM user arguments are
a much more powerful flavor of the [Dockerfile `ARG`
instruction](https://docs.docker.com/engine/reference/builder/#arg).

The `hpccm` command line tool has the `--userarg` option.  Values
specified using this option are inserted into a Python dictionary
named `USERARG` that can be accessed inside a recipe.

```python
ompi_version = USERARG.get('ompi', '3.1.2')
Stage0 += openmpi(infiniband=False, version=ompi_version)
```

```
$ hpccm --recipe userargs.py --userarg ompi=3.0.0
```

## Multi-stage Recipes

[Multi-stage
builds](https://docs.docker.com/develop/develop-images/multistage-build/)
are a technique that can significantly reduce the size of container
images.  Multi-stage recipes can also be used with licensed software
to build an application without needing to redistribute the licensed
development software or source code.

A recipe consists of one or more stages, although many recipes will
only contain a single stage.  The `Stage0` and `Stage1` variables are
automatically created for use in HPCCM recipes.

Most [building blocks](/docs/building_blocks.md) provide a `runtime`
method to install the corresponding runtime version of a component in
another stage.  The `Stage` class also provides a `runtime` method
that calls the `runtime` method of every building block.  Building
block settings defined in the first stage are automatically reflected
in the second stage using the `runtime` method.

```python
Stage0 += baseimage(image='nvidia/cuda:9.0-devel-centos7', _as='devel')
Stage0 += openmpi(infiniband=False, prefix='/opt/openmpi')

Stage1 += baseimage(image='nvidia/cuda:9.0-base-centos7')
Stage1 += Stage0.runtime(_from='devel')
```

```
$ hpccm --recipe multi-stage.py
FROM nvidia/cuda:9.0-devel-centos7 AS devel

...

FROM nvidia/cuda:9.0-base-centos7

# OpenMPI
RUN yum install -y \
        hwloc \
        openssh-clients && \
    rm -rf /var/cache/yum/*
COPY --from=devel /opt/openmpi /opt/openmpi
ENV LD_LIBRARY_PATH=/opt/openmpi/lib:$LD_LIBRARY_PATH \
    PATH=/opt/openmpi/bin:$PATH
```

Singularity version 3.2 and later supports multi-stage Singularity
definition files.  However, the multi-stage definition file syntax is
incompatible with earlier versions of Singularity.  Use the HPCCM
`--singularity-version <version>` command line option to specify the
Singularity definition file version to generate.  A `version` of 3.2
or later will generate a multi-stage definition file that will only
build with Singularity version 3.2 or later.  A `version` less than
3.2 will generate a portable definition file that works with any
version of Singularity, but will not support multi-stage builds.

```
$ hpccm --recipe multi-stage.py --format singularity --singularity-version 3.2
# NOTE: this definition file depends on features only available in
# Singularity 3.2 and later.
BootStrap: docker
From: nvidia/cuda:9.0-devel-centos7
Stage: devel

...

BootStrap: docker
From: nvidia/cuda:9.0-base-centos7

# OpenMPI
%post
    yum install -y \
        hwloc \
        openssh-clients
    rm -rf /var/cache/yum/*
%files from devel
    /opt/openmpi /opt/openmpi
%environment
    export LD_LIBRARY_PATH=/opt/openmpi/lib:$LD_LIBRARY_PATH
    export PATH=/opt/openmpi/bin:$PATH
%post
    export LD_LIBRARY_PATH=/opt/openmpi/lib:$LD_LIBRARY_PATH
    export PATH=/opt/openmpi/bin:$PATH
```

If Singularity version 3.2 or later is not an option, Docker images
can be easily converted to Singularity images so older versions of
Singularity can also (indirectly) take advantage of multi-stage
builds.

```
$ sudo docker run -t --rm --privileged -v /var/run/docker.sock:/var/run/docker.sock -v /tmp:/output singularityware/docker2singularity <docker-tag>
```

## Scripts Using the HPCCM Module

HPCCM recipes automatically handle some common tasks, such as creating
[stages](#multi-stage-recipes), [user arguments](#user-arguments), and
specifying the output container specification format.  For those
unfamiliar with Python, HPCCM recipes provide a seemingly higher level
interface.

It is also possible to write a "native" Python script and import HPCCM
as a module.  This provides more flexibility, but the user is
responsible for managing input and output.  A script using HPCCM as a
module could implement a more sophisticated user input handling than
`hpccm --userarg`, write to a file instead of standard output, or
combine HPCCM with other Python modules.

Building blocks and primitives are implemented using the Python
`__str__` function, so it is possible to simply call a building block
or primitive in string context, e.g., `print()`.  There are
[additional APIs](/docs/misc_api.md) that are useful for this use
case, e.g., to set the configuration specification output format.

```python
#!/usr/bin/env python

from __future__ import print_function

import hpccm

# Set to 'docker' to generate a Dockerfile or set to 'singularity' to
# generate a Singularity definition file
hpccm.config.set_container_format('docker')

print(hpccm.primitives.baseimage(image='centos:7'))
compiler = hpccm.building_blocks.gnu()
print(compiler)
```

A [basic example](/recipes/examples/script.py) of using HPCCM as a
library is provided.
