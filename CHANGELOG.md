# v18.9.0

- Adds LLVM (`llvm`) building block
- New parameters in the GNU (`gnu`) building block
- Adds support for the  Scientific Filesystem (SCIF) for Singularity recipe
  files
- Resolves an issue with OpenMPI process affinity

# v18.8.0

- Adds Boost (`boost`), CGNS (`cgns`), Intel MPI (`intel_mpi`), and
  OpenBLAS (`openblas`) building blocks
- Adds Spack and MPI Bandwidth reference recipes, refreshes
  the GROMACS and EasyBuild reference recipes
- Adds `user` primitive for setting the active user in Dockerfiles
- Adds `rm` template for cleaning up files and directories
- New parameter in the `git` template for LFS support
- Internal reorganization of `runtime()` methods to consistently output
  strings

# v18.7.0

- Adds Charm++ (`charm`), Intel Parallel Studio XE (`intel_psxe`), and
  PnetCDF (`pnetcdf`) building blocks
- New parameters in the PGI (`pgi`) building block
- Internal reorganization of files into sub-directories for building
  blocks, templates, and primitives

# v18.6.0

- Adds Intel MKL (`mkl`) and NetCDF (`netcdf`) building blocks
- Enhancements and fixes for the Mellanox OFED (`mlnx_ofed`), MVAPICH2
  (`mvapich2`), OpenMPI (`openmpi`), and PGI (`pgi`) building blocks
- New parameters in the `toolchain` template
- Load environment variables from the Docker base image when bootstrapping
  from a Docker image in Singularity
- Resolves a potential conflict with host files in `/tmp` for Singularity
  recipe files

# v18.5.0

- Initial release
