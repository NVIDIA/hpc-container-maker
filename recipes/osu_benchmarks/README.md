# OSU Micro-Benchmarks

This example demonstrates how to build a container that is portable
with respect to the host OFED version.  PMI is also included to
simplify running the container on multiple nodes.

The `common.py` recipe builds a generic software environment that
includes multiple versions of OFED and UCX.  The entrypoint script
determines the best match to the host at runtime and configures the
appropriate software environment.

The `osu_benchmarks.py` recipe builds the [OSU
Micro-Benchmarks](http://mvapich.cse.ohio-state.edu/benchmarks/) on
top of this environment.

## Build

```
$ hpccm --recipe osu_benchmarks.py > Dockerfile
$ sudo docker build -t osu_benchmarks -f Dockerfile .
$ singularity build osu_benchmarks.sif docker-daemon://osu_benchmarks:latest
```

## Run

```
$ srun -N 2 -n 2 --mpi=pmix singularity run --nv osu_benchmarks.sif get_local_rank osu_bw
```

On some systems `--mpi=pmi2` may be more appropriate.

Note: Setting the
[`UCX_TLS`](https://github.com/openucx/ucx/wiki/UCX-environment-parameters)
environment variable may be necessary in some cases.
