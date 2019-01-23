# Running HPC Container Maker from a Container

Please refer to the [Getting Started](/docs/getting_started.md) guide
for more information on installing HPC Container Maker.

If installing HPCCM on the host is not an option, then the
files in this directory may be used to build a HPCCM container image.
The HPCCM recipe used to generate the Dockerfile and Singularity
definition file is also included.

## Docker

Use the provided Dockerfile to build a HPCCM container image.

```
$ sudo docker build -t hpccm -f Dockerfile .
$ sudo docker run -rm -v $(pwd):/recipes hpccm --recipe /recipes/...
```

## Singularity

Use the provided Singularity definition file to build a HPCCM container
image.

```
$ sudo singularity build hpccm.simg Singularity.def
$ ./hpccm.simg --recipe ...
```
