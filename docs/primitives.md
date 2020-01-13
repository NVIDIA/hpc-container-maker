# baseimage
```python
baseimage(self, **kwargs)
```
The `baseimage` primitive defines the base image to be used.

__Parameters__


- ___arch__: The underlying CPU architecture of the base image.  Valid
values are `aarch64`, `ppc64le`, and `x86_64`.  By default, the
primitive attemps to figure out the CPU architecture by inspecting
the image identifier, and falls back to `x86_64` if unable to
determine the CPU architecture automatically.

- ___as__: Name for the stage.  When using Singularity multi-stage
recipes, this value must be specified.  The default value is
empty.

- ___bootstrap__: The Singularity bootstrap agent.  This default value
is `docker` (Singularity specific).

- ___distro__: The underlying Linux distribution of the base image.
Valid values are `centos`, `centos7`, `centos8`, `redhat`, `rhel`,
`rhel7`, `rhel8, `ubuntu`, `ubuntu16`, and `ubuntu18`.  By
default, the primitive attempts to figure out the Linux
distribution by inspecting the image identifier, and falls back to
`ubuntu` if unable to determine the Linux distribution
automatically.

- ___docker_env__: Boolean specifying whether to load the Docker base
 image environment, i.e., source
 `/.singularity.d/env/10-docker*.sh` (Singularity specific).  The
 default value is True.

- __image__: The image identifier to use as the base image.  The default value is `nvidia/cuda:9.0-devel-ubuntu16.04`.

- __AS__: Name for the build stage (Docker specific).  The default value
is empty.  This parameter is deprecated; use `_as` instead.

__Examples__


```python
baseimage(image='nvidia/cuda:9.1-devel')
```


# blob
```python
blob(self, **kwargs)
```
The `blob` primitive inserts a file, without modification, into the
corresponding place in the container specification file.  If a
relative path is specified, the path is relative to current
directory.

Generally, the blob should be functionally equivalent for each
container format.

Wherever possible, the blob primitive should be avoided and other,
more portable, operations should be used instead.

__Parameters__


- __docker__: Path to the file containing the Dockerfile blob (Docker
specific).

- __singularity__: Path to the file containing the Singularity blob
(Singularity specific).

__Example__


```python
blob(docker='path/to/foo.docker', singularity='path/to/foo.singularity')
```

# comment
```python
comment(self, *args, **kwargs)
```
The `comment` primitive inserts a comment into the corresponding
place in the container specification file.

__Parameters__


- ___app__: String containing the
- __[SCI-F](https__://www.sylabs.io/guides/2.6/user-guide/reproducible_scif_apps.html)
identifier.  This also causes the comment to be enclosed in a
Singularity block to named `%apphelp` (Singularity specific).

- __reformat__: Boolean flag to specify whether the comment string
should be wrapped to fit into lines not exceeding 80 characters.
The default is True.

__Examples__


```python
comment('libfoo version X.Y')
```


# copy
```python
copy(self, **kwargs)
```
The `copy` primitive copies files from the host to the container
image.

__Parameters__


- ___app__: String containing the [SCI-F](https://www.sylabs.io/guides/2.6/user-guide/reproducible_scif_apps.html)
identifier.  This also causes the Singularity block to named
`%appfiles` rather than `%files` (Singularity specific).

- ___chown__: Set the ownership of the file(s) in the container image
(Docker specific).

- __dest__: Path in the container image to copy the file(s)

- __files__: A dictionary of file pairs, source and destination, to copy
into the container image.  If specified, has precedence over
`dest` and `src`.

- ___from__: Set the source location to a previous build stage rather
than the host filesystem (Docker specific).

- ___mkdir__: Boolean flag specifying that the destination directory
should be created in a separate `%setup` step.  This can be used
to work around the Singularity limitation that the destination
directory must exist in the container image prior to copying files
into the image.  The default is False (Singularity specific).

- ___post__: Boolean flag specifying that file(s) should be first copied
to `/` and then moved to the final destination by a `%post` step.
This can be used to work around the Singularity limitation that
the destination must exist in the container image prior to copying
files into the image.  The default is False (Singularity
specific).

- __src__: A file, or a list of files, to copy

__Examples__


```python
copy(src='component', dest='/opt/component')
```

```python
copy(src=['a', 'b', 'c'], dest='/tmp')
```

```python
copy(files={'a': '/tmp/a', 'b': '/opt/b'})
```


# environment
```python
environment(self, **kwargs)
```
The `environment` primitive sets the corresponding environment
variables.  Note, for Singularity, this primitive may set
environment variables for the container runtime but not for the
container build process (see this
[rationale](https://github.com/singularityware/singularity/issues/1053)).
See the `_export` parameter for more information.

__Parameters__


- ___app__: String containing the [SCI-F](https://www.sylabs.io/guides/2.6/user-guide/reproducible_scif_apps.html)
identifier.  This also causes the Singularity block to named
`%appenv` rather than `%environment` (Singularity specific).

- ___export__: A Boolean flag to specify whether the environment should
also be set for the Singularity build context (Singularity
specific).  Variables defined in the Singularity `%environment`
section are only defined when the container is run and not for
subsequent build steps (unlike the analogous Docker `ENV`
instruction).  If this flag is true, then in addition to the
`%environment` section, a identical `%post` section is generated
to export the variables for subsequent build steps.  The default
value is True.

- __variables__: A dictionary of key / value pairs.  The default is an
empty dictionary.

__Examples__


```python
environment(variables={'PATH': '/usr/local/bin:$PATH'})
```

# label
```python
label(self, **kwargs)
```
The `label` primitive sets container metadata.

__Parameters__


- ___app__: String containing the [SCI-F](https://www.sylabs.io/guides/2.6/user-guide/reproducible_scif_apps.html)
identifier.  This also causes the Singularity block to named
`%applabels` rather than `%labels` (Singularity specific).

- __metadata__: A dictionary of key / value pairs.  The default is an
empty dictionary.

__Examples__


```python
label(metadata={'maintainer': 'jane@doe'})
```

# raw
```python
raw(self, **kwargs)
```
The `raw` primitive inserts the specified string, without
modification, into the corresponding place in the container
specification file.

Generally, the string should be functionally equivalent for each
container format.

Wherever possible, the raw primitive should be avoided and other,
more portable, primitives should be used instead.

__Parameters__


- __docker__: String containing the Dockerfile instruction (Docker
specific).

- __singularity__: String containing the Singularity instruction
(Singularity specific).

__Examples__


```python
raw(docker='COPY --from=0 /usr/local/openmpi /usr/local/openmpi',
    singularity='# no equivalent to --from')
```


# runscript
```python
runscript(self, **kwargs)
```
The `runscript` primitive specifies the commands to be invoked
when the container starts.

__Parameters__


- ___args__: Boolean flag to specify whether `"$@"` should be appended
to the command.  If more than one command is specified, nothing is
appended regardless of the value of this flag.  The default is
True (Singularity specific).

- ___app__: String containing the [SCI-F](https://www.sylabs.io/guides/2.6/user-guide/reproducible_scif_apps.html)
identifier.  This also causes the Singularity block to named `%apprun`
rather than `%runscript` (Singularity specific).

- __commands__: A list of commands to execute.  The default is an empty
list.

- ___exec__: Boolean flag to specify whether `exec` should be inserted
to preface the final command.  The default is True (Singularity
specific).

__Examples__


```python
runscript(commands=['cd /workdir', 'source env.sh'])
```

```python
runscript(commands=['/usr/local/bin/entrypoint.sh'])
```


# shell
```python
shell(self, **kwargs)
```
The `shell` primitive specifies a series of shell commands to
execute.

__Parameters__


- ___app__: String containing the [SCI-F](https://www.sylabs.io/guides/2.6/user-guide/reproducible_scif_apps.html)
identifier.  This also causes the Singularity block to named
`%appinstall` rather than `%post` (Singularity specific).

- ___appenv__: Boolean flag to specify whether the general container
environment should be also be loaded when executing a SCI-F
`%appinstall` block.  The default is False.

- ___arguments__: Specify additional [Dockerfile RUN arguments](https://github.com/moby/buildkit/blob/master/frontend/dockerfile/docs/experimental.md) (Docker specific).

- __chdir__: Boolean flag to specify whether to change the working
directory to `/` before executing any commands.  Docker
automatically resets the working directory for each `RUN`
instruction.  Setting this option to True makes Singularity behave
the same.  This option is ignored for Docker.  The default is
True.

- __commands__: A list of commands to execute.  The default is an empty
list.

- ___test__: Boolean flag to specify whether to use `%test` instead of
`%post` and `%apptest` instead of `%appinstall` as the Singularity
section headings (Singularity specific).

__Examples__


```python
shell(commands=['cd /path/to/src', './configure', 'make install'])
```

```python
# Cache Go packages
shell(_arguments=['--mount=type=cache,target=/root/.cache/go-build']
      commands=['cd /path/to/go-src', 'go build'])
```


# user
```python
user(self, **kwargs)
```
The `user` primitive sets the user name to use for any subsequent
steps.

This primitive is the null operation for Singularity.

__Parameters__


- __user__: The user name to use.  The default is an empty string.

__Examples__


```python
user(user='ncognito')
```

# workdir
```python
workdir(self, **kwargs)
```
The `workdir` primitive sets the working directory for any
subsequent operations.  As a side effect, if the directory does
not exist, it is created.

__Parameters__


- __directory__: The directory path.

__Examples__


```python
workdir(directory='/path/to/directory')
```

