# hpccm.config

## get_cpu_architecture
```python
get_cpu_architecture()
```
Return the architecture string for the currently configured CPU
architecture, e.g., `aarch64`, `ppc64le`, or `x86_64`.


## get_cpu_optimization_flags
```python
get_cpu_optimization_flags(compiler, version='9999')
```
Return the CPU optimization flags for the target and compiler
combination.

__Arguments__


- __compiler__: A compiler family string recognized by archspec.

- __version__: The version of the compiler.  The default version is
`9999`, i.e., assume the compiler supports the latest optimization
flags.

## get_format
```python
get_format()
```
Return the container format string for the currently configured
format, e.g., `bash`, `docker`, or `singularity`.
## set_container_format
```python
set_container_format(ctype)
```
Set the container format

__Arguments__


- __ctype (string)__: 'docker' to specify the Dockerfile format, or
'singularity' to specify the Singularity definition file format

__Raises__


- `RuntimeError`: invalid container type argument

## set_cpu_architecture
```python
set_cpu_architecture(arch)
```
Set the CPU architecture

In most cases, the `baseimage` primitive should be relied upon to
set the CPU architecture.  Only use this function if you really
know what you are doing.

__Arguments__


- __arch (string)__: Value values are `aarch64`, `ppc64le`, and `x86_64`.
`arm` and `arm64v8` are aliases for `aarch64`, `power` is an alias
for `ppc64le`, and `amd64` and `x86` are aliases for `x86_64`.

## set_cpu_target
```python
set_cpu_target(target)
```
Set the CPU optimization target

__Arguments__


- __target (string)__: A CPU microarchitecture string recognized by
archspec.

## set_linux_distro
```python
set_linux_distro(distro)
```
Set the Linux distribution and version

In most cases, the `baseimage` primitive should be relied upon to
set the Linux distribution.  Only use this function if you really
know what you are doing.

__Arguments__


- __distro (string)__: Valid values are `centos7`, `centos8`, `rhel7`,
`rhel8`, `rockylinux8`, `ubuntu16`, `ubuntu18`, and `ubuntu20`.
`ubuntu` is an alias for `ubuntu16`, `centos` is an alias for
`centos7`, and `rhel` is an alias for `rhel7`.


## set_singularity_version
```python
set_singularity_version(ver)
```
Set the Singularity definition file format version

The Singularity definition file format was extended in version 3.2
to enable multi-stage builds.  However, these changes are not
backwards compatible.

__Arguments__


- __ver (string)__: Singularity definition file format version.


## set_working_directory
```python
set_working_directory(wd)
```
Set the working directory to use for staging inside the container

__Arguments__


- __wd (string)__: working directory path


## test_cpu_feature_flag
```python
test_cpu_feature_flag(flag)
```
Return True or False depending on whether the CPU supports the
given feature flag

__Arguments__


- __flag__: A CPU feature flag, e.g., `avx`.

# recipe
```python
recipe(recipe_file, cpu_target=None, ctype=<container_type.DOCKER: 1>, raise_exceptions=False, single_stage=False, singularity_version=u'2.6', userarg=None, working_directory=u'/var/tmp')
```
Recipe builder

__Arguments__


- __recipe_file__: path to a recipe file (required).

- __cpu_target__: A CPU microarchitecture string recognized by archspec.

- __ctype__: Enum representing the container specification format.  The
default is `container_type.DOCKER`.

- __raise_exceptions__: If False, do not print stack traces when an
exception is raised.  The default value is False.

- __single_stage__: If True, only print the first stage of a multi-stage
recipe.  The default is False.

- __singularity_version__: Version of the Singularity definition file
format to use.  Multi-stage support was added in version 3.2, but
the changes are incompatible with earlier versions of Singularity.
The default is '2.6'.

- __userarg__: A dictionary of key / value pairs provided to the recipe
as the `USERARG` dictionary.

- __working_directory__: path to use as the working directory in the
container specification


# Stage
```python
Stage(self, **kwargs)
```
Class for container stages.

Docker may have one or more stages,
   Singularity will always have a single stage.

__Parameters__


- __name__: Name to use when refering to the stage (Docker specific).
The default is an empty string.

- __separator__: Separator to insert between stages.  The default is
'\n\n'.


## baseimage
```python
Stage.baseimage(self, image, _distro=u'')
```
Insert the baseimage as the first layer

__Arguments__


- __image (string)__: The image identifier to use as the base image.
The value is passed to the `baseimage` primitive.

- ___distro__: The underlying Linux distribution of the base image.
The value is passed to the `baseimage` primitive.

## runtime
```python
Stage.runtime(self, _from=None, exclude=[])
```
Generate the set of instructions to install the runtime specific
components from a previous stage.

This method invokes the runtime() method for every layer in
the stage.  If a layer does not have a runtime() method, then
it is skipped.

__Arguments__


- ___from__: The name of the stage from which to copy the runtime.
The default is `0`.

- __exclude__: List of building blocks to exclude when generating
the runtime. The default is an empty list.

__Examples__

```python
Stage0 += baseimage(image='nvidia/cuda:9.0-devel')
Stage0 += gnu()
Stage0 += boost()
Stage0 += ofed()
Stage0 += openmpi()
...
Stage1 += baseimage(image='nvidia/cuda:9.0-base')
Stage1 += Stage0.runtime(exclude=['boost'])
```


