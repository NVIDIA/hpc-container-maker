# hpccm.config

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

# recipe
```python
recipe(recipe_file, ctype=<container_type.DOCKER: 1>, raise_exceptions=False, single_stage=False, userarg=None)
```
Recipe builder

__Arguments__


- __recipe_file__: path to a recipe file (required).

- __ctype__: Enum representing the container specification format.  The
default is `container_type.DOCKER`.

- __raise_exceptions__: If False, do not print stack traces when an
exception is raised.  The default value is False.

- __single_stage__: If True, only print the first stage of a multi-stage
recipe.  The default is False.

- __userarg__: A dictionary of key / value pairs provided to the recipe
as the `USERARG` dictionary.


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

## is_defined
```python
Stage.is_defined(self)
```
Check if any layers have been added to the Stage

__Returns__


True if any layers have been added to the stage, otherwise False

