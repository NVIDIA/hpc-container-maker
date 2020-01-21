# v20.1.0

- Adds Mellanox HPC-X (`hpcx`) building block
- Fixes and enhancements for the NetCDF (`netcdf`), SCI-F (`scif`), and
  generic (`generic_autotools`, `generic_build`, `generic_cmake`)
  building blocks
- Add support for non-Docker Singularity bootstrap sources
- New parameter in the `git` template for submodule support
- Set the default platform architecture to match the runtime architecture
- Replaced Python wrapper script with a shell script (`hpccm.sh`)

# v19.12.0

- Adds generic builder (`generic_build`), PMI (`slurm_pmi`), and PMIx
  (`pmix`) building blocks
- Fixes and enhancements for the generic GNU Autotools (`generic_autotools`),
  generic CMake (`generic_cmake`), Intel Parallel Studio XE runtime
  (`intel_psxe_runtime`), and NetCDF (`netcdf`) building blocks
- Minor improvements and clarifications for Singularity multi-stage
  recipes
- Adds LAMMPS example recipe and updates GROMACS, MILC, and MPI bandwidth
  example recipes

# v19.11.0

- Adds generic building blocks for GNU Autotools (`generic_autotools`)
  and CMake (`generic_cmake`) packages
- Refresh default component version for the PGI (`pgi`) building block
- Adds Jupyter notebook example recipe
- Refresh default component versions used in the hpcbase example recipes
- Fix issue with UCX runtime dependencies

# v19.10.0

- Adds Anaconda (`conda`) and Arm Allinea Studio (`arm_allinea_studio`)
  building blocks.
- Adds support for CentOS 8 base images.
- Fixes and enhancements for the Charm++ (`charm`), CMake (`cmake`),
  LLVM (`llvm`), Mellanox OFED (`mlnx_ofed`), and OpenMPI (`openmpi`)
  building blocks.

# v19.9.0

- Adds Julia (`julia`) building block.

# v19.8.0

- Adds experimental support for ARM (aarch64) and POWER (ppc64le)
  processors.
- Enhances the `shell` primitive to support Docker specific 
  experimental `RUN` options.
- Fix issue due to NetCDF package name change.

# v19.7.0

- Refreshes default component versions for the Boost (`boost`),
  ParaView/Catalyst (`catalyst`), CGNS (`cgns`), Charm++ (`charm`),
  CMake (`cmake`), HDF5 (`hdf5`), Intel MPI (`intel_mpi`), Intel
  Parallel Studio XE (`intel_psxe` and `intel_psxe_runtime`), Kokkos
  (`kokkos`), MKL (`mkl`), Mellanox OFED (`mlnx_ofed`), MPICH (`mpich`),
  MVAPICH2 (`mvapich2`), NetCDF (`netcdf`), OpenBLAS (`openblas`),
  OpenMPI (`openmpi`), PnetCDF (`pnetcdf`), and UCX (`ucx`) building
  blocks.
- Adds "Multi OFED" (`multi_ofed`) building block to install multiple,
  side-by-side versions of Mellanox and inbox OFED that can be selected
  at runtime based on the best match with the host InfiniBand driver.
- Adds `envvars` template and updates most building blocks to
  introduce an `environment` parameter to optionally disable setting
  up the component environment.

# v19.6.0

- Enhances the GNU (`gnu`) building block to build the compiler from
  source, optionally with OpenACC support
- Adds support for Windows
- Enhances the `copy` primitive to support the Docker specific `--chown`
  option

# v19.5.1

- Fix issue with installs from PyPi

# v19.5.0

- Adds support for Singularity multi-stage builds (Singularity version 3.2
  or later)
- Fix for the PnetCDF building block (`pnetcdf`)
- Sort packages by name
- Internal refactoring to simplify importing building blocks

# v19.4.0

- Adds Intel Parallel Studio XE runtime (`intel_psxe_runtime`) and SENSEI
  (`sensei`) building blocks
- Updates and enhacements to the Intel Parallel Studio XE (`intel_psxe`)
  and PGI (`pgi`) building blocks
- Refresh default component versions for the MVAPICH2-GDR (`mvapich2_gdr`)
  and PGI (`pgi`) building blocks
- Enhance the Mellanox OFED (`mlnx_ofed`) building block to support
  installing multiple versions in the same container image
- Fix issue with setting the environment when using Docker images as
  Singularity base images
- Adds support for bash script output format

# v19.3.0

- Adds Scientific Filesystem (`scif`) and VisIt/Libsim (`libsim`)
  building blocks
- Consistent interfaces for the `ConfigureMake` and `CMake` templates
- New `files` parameter in the `copy` primitive
- Fix for the Intel Parallel Studio XE building block (`intel_psxe`)
- Internal refactoring including a building block base class and MRO
  inheritance

# v19.2.0

- Adds Kokkos (`kokkos`) and ParaView/Catalyst (`catalyst`) building
  blocks
- Update the MVAPICH2-GDR (`mvapich2_gdr`) building block for
  upstream changes
- Add option to install Python development packages (`python`)
- Fixes and enhancements for the GNU (`gnu`) and pip (`pip`) building
  blocks

# v19.1.0

- Adds MPICH (`mpich`) and pip (`pip`) building blocks
- Simplify specifying runtime stages with the `Stage.runtime()` method
- Add support for configuring library locations with `ldconfig`
- Add container specification files for building a HPCCM container
- Remove the CMake (`cmake`) building block runtime method
- Add an option to specify whether environment variables from the
  Docker base image should be loaded in Singularity
- Update the GROMACS and MILC example recipes to use the new capabilities

# v18.12.0

- Add support for Ubuntu 18 base images
- Refresh the documentation
- Refresh default component version for the Intel MPI (`intel_mpi`)
  building block
- Dynamically select the number of build processes
- Fixes for the PGI (`pgi`) and PnetCDF (`pnetcdf`) building blocks

# v18.11.0

- Adds UCX (`ucx`), gdrcopy (`gdrcopy`), KNEM (`knem`), and XPMEM
  (`xpmem`) building blocks
- Refresh default component versions for the Boost (`boost`),
  CMake (`cmake`), FFTW (`fftw`), HDF5 (`hdf5`), MKL (`mkl`),
  MVAPICH2 (`mvapich2`), OpenBLAS (`openblas`), OpenMPI (`openmpi`),
  and PGI (`pgi`) building blocks
- Improved support for `import hpccm` use cases

# v18.10.0

- Enhancements and fixes for the Boost (`boost`), FFTW (`fftw`),
  HDF5 (`hdf5`), Intel MPI (`intel_mpi`), LLVM (`llvm`),
  MVAPICH2 (`mvapich2`), and PGI (`pgi`) building blocks
- Adds `CMakeBuild` template for working with CMake based components
- Updated the GROMACS and MILC example recipes to use the new `CMakeBuild`
  template
- Fixes for the EasyBuild and Spack example recipes
- Adds workarounds for Singularity specific issue copying files to
  a location that does not exist (see
  https://github.com/sylabs/singularity/issues/1549)
- New parameter in the `tar` template for more flexible argument
  specification

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
