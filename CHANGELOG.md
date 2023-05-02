# v23.5.0
- Add the ability to export the build environment to the generic
  Autotools building block (`generic_autotools`).
- Update the Anaconda (`conda`) package for the new upstream versioning
  scheme, and refreshes the default component version.
- Fix the Python building block (`python`) to use the correct name of the
  Python 2 package on Ubuntu 22.04

# v23.3.0
- Refreshes default component version for the LLVM ('llvm') building block.

# v23.2.0
- Refreshes default component versions for the CMake (`cmake`), OpenBLAS
  (`openblas`), Nsight Compute (`nsight_compute`), Nsight Systems
  (`nsight_systems`), and NVIDIA HPC SDK (`nvhpc`) building blocks.
- Fallback to the same system architecture as the current system rather
  then defaulting to x86_64 if the image architecture cannot be determined.
- Enhances the CMake (`cmake`) building block to use the precompiled packages
  for Arm.

# v22.10.0
- Refreshes default component versions for the NVIDIA HPC SDK (`nvhpc`)
  building block.
- Add support for signed apt repositories using signed-by rather than apt-key
- Update GNU compiler (`gnu`) runtime library version on Ubuntu 20 and later.

# v22.8.0
- Refreshes default component versions for the LLVM (`llvm`) and 
  NVIDIA HPC SDK (`nvhpc`) building blocks.
- Fixes a package naming bug in the HPC-X (`hpcx`) building block.

# v22.5.0
- Adds support for Ubuntu 22.04.
- Refreshes default component versions for the HPC-X (`hpcx`) and PMI
  (`slurm_pmi2`) building blocks.
- Enhancements to the NVIDIA HPC SDK (`nvhpc`) building block.

# v22.4.0
- Refreshes default component versions for the Arm Allinea Studio
  (`arm_allinea_studio`), NCCL (`nccl`), Nsight Compute (`nsight_compute`),
  Nsight Systems (`nsight_systems`), NVIDIA HPC SDK (`nvhpc`), and PMIX
  (`pmix`) building blocks
- Updates the NCCL (`nccl`) building block for the CUDA Linux repository
  key change
- Enables upstream Arm packages in the LLVM (`llvm`) building block
- Updates how the OpenMPI (`openmpi`) building block supports CUDA
- Adds toolchain parameter to the NVIDIA HPC SDK (`nvhpc`) building block

# v22.2.0
- Changes the NVIDIA HPC SDK (`nvhpc`) building block to install
  from the package repository by default.
- Refreshes default component version for the CMake (`cmake`), 
  LLVM (`llvm`) an NVIDIA HPC SDK (`nvhpc`) building blocks.
- Updates to the example recipes for CentOS 8 EOL.
- Updates the MILC example recipe.

# v21.12.0
- Refreshes default component version for the NVIDIA HPC SDK (`nvhpc`)
  building block.

# v21.10.0
- Refreshes default component version for the Arm Allinea Studio
  (`arm_allinea_studio`) building block.
- Enhancements to the XPMEM (`xpmem`) building block.

# v21.9.0
- Refreshes default component versions for the FFTW (`fftw`) and
  NVIDIA HPC SDK (`nvhpc`) building blocks.
- Fixes and enhancements to the LLVM (`llvm`) building block.
- Updates the MILC example recipe.

# v21.8.0
- Refreshes default component version for the NVSHMEM (`nvshmem`)
  building block
- Adds NVIDIA HPC SDK example recipe

# v21.7.0
- Refreshes default component version for the NVIDIA HPC SDK (`nvhpc`)
  building block.
- Fixes to the HPC-X (`hpcx`) building block documentation.

# v21.6.0
- Adds support for Rocky Linux.
- Refresh default component versions for the Boost (`boost`), HPC-X
  (`hpcx`), and Mellanox OFED (`mlnx_ofed`) building blocks.
- Fixes and enhancements to the Nsight Compute (`nsight_compute`)
  building block.

# v21.5.0
- Adds CPU microarchitecture optimization support via `archspec`.
- Fixes and enhancements to the Nsight Compute (`nsight_compute`),
  NVIDIA HPC SDK (`nvhpc`), and PMI (`slurm_pmi2`) building blocks.

# v21.4.0
- Fixes and enhancements to the gdrcopy (`gdrcopy`), LLVM (`llvm`),
  Mellanox OFED (`mlnx_ofed`), Nsight Compute (`nsight_compute`), Nsight
  Systems (`nsight_systems`), NVIDIA HPC SDK (`nvhpc`), and NVSHMEM
  (`nvshmem`) building blocks.

# v21.3.0
- Updates MPI Bandwidth and OSU Micro-Benchmarks example recipes and
  removes obsolete syntax from several other examples.
- Fixes to the Arm Allinea Studio (`arm_allinea_studio`) and CMake
  (`cmake`) building blocks.
- Detects and reports Singularity recipes that stage files from the
  host in /tmp or /var/tmp.
- Fixes to the documentation of the `shell` primitive.


# v21.2.0
- Refreshes default component versions for the Nsight Systems
  (`nsight_systems`) and NVIDIA HPC SDK (`nvhpc`) building blocks.
- Fixes and enhancements to the PnetCDF (`pnetcdf`) building block.

# v21.1.0

- Fixes and enhancements to the gdrcopy (`gdrcopy`), pip (`pip`), and
  generic (`generic_autotools`, `generic_build`, `generic_cmake`) building
  blocks.

# v20.12.0

- Adds a RDMA Core (`rdma_core`) building block.
- Fixes and enhancements to the gdrcopy (`gdrcopy`) and NVIDIA HPC SDK
  (`nvhpc`) building blocks.
- Add a configuration option to specify the working directory used inside
  the container when building.
- Fix issue with deepcopies of toolchains.

# v20.11.0

- Enhancements to the Nsight Compute (`nsight_compute`), Nsight Systems
  (`nsight_systems`), and NVIDIA HPC SDK (`nvhpc`) building blocks.
- Adds simple conversion of toolchains to environments.

# v20.10.0

- Adds support for Ubuntu 20.04.
- Adds a Nsight Compute (`nsight_compute`) building block.
- Refreshes default component version for the NVIDIA HPC SDK (`nvhpc`).
- Enhancements to the Anaconda (`conda`), CMake (`cmake`), and LLVM (`llvm`).
- Adds an OSU Micro-Benchmarks example recipe, demonstrating how to build a
  container that is portable with respect to the host OFED version.
- Updates the example recipes to use the NVDIA HPC SDK instead of
  the PGI compilers.
- Fixes an install issue with Python 3.4 and later.

# v20.9.0

- Refreshes default component versions for the Arm Allinea Studio
  (`arm_allinea_studio`), Boost (`boost`), CGNS (`cgns`), Charm++ (`charm`),
  CMake (`cmake`), Anaconda (`conda`), gdrcopy (`gdrcopy`), HDF5 (`hdf5`),
  HPC-X (`hpcx`), Intel Parallel Studio runtime (`intel_psxe_runtime`),
  Julia (`julia`), Kokkos (`kokkos`), Mellanox OFED (`mlnx_ofed`),
  "Multi OFED" (`multi_ofed`), MVAPICH2 (`mvapich2`), MVAPICH2-GDR
  (`mvapich2_gdr`), NCCL (`nccl`), NetCDF (`netcdf`), OpenBLAS (`openblas`),
  OpenMPI (`openmpi`), PMIX (`pmix`), PMI (`slurm_pmi2`), and UCX (`ucx`)
  building blocks.
- Enhancements and fixes to the GNU (`gnu`), NVIDIA HPC SDK (`nvhpc`),
  OpenMPI (`openmpi`), pip (`pip`), and PnetCDF (`pnetcdf`) building blocks.
- Updates the PGI (`pgi`) building block to reflect changes in the vendor
  distribution model.

# v20.8.0

- Adds an NVIDIA HPC SDK (`nvhpc`) building block, replacing the previous
  one (`nv_hpc_sdk`).
- Enhancements to the GNU (`gnu`) and LLVM (`llvm`) building blocks.
- Update the hpcbase example recipes to use the NVDIA HPC SDK instead of
  the PGI compilers.

# v20.7.0

- Adds a NCCL (`nccl`) building block.
- Enhancements and fixes to the Boost (`boost`), LLVM (`llvm`), NVSHMEM
  (`nvshmem`), and UCX (`ucx`) building blocks.
- Fix an issue when using the `hpccm.sh` wrapper script
- Internal change to add runtime support to the base building block class.

# v20.6.0

- Adds AMGX (`amgx`), NVIDIA HPC SDK (`nv_hpc_sdk`), and NVSHMEM (`nvshmem`)
  building blocks.
- Enhancements to the Kokkos (`kokkos`), LLVM (`llvm`) and generic
  (`generic_autotools`, `generic_build`, `generic_cmake`) building blocks.
- Adds support for zip file packages.
- Fix to the Jupyter example recipe.

# v20.5.0

- Fixes to the Intel Parallel Studio runtime (`intel_psxe_runtime`),
  Mellanox OFED (`mlnx_ofed`), and "Multi OFED" (`multi_ofed`) building
  blocks.
- Refresh default component version for the HPC-X (`hpcx`) building block.

# v20.4.0
- Adds MAGMA (`magma`) building block
- Refresh default component versions for the Mellanox OFED (`mlnx_ofed`),
  OpenMPI (`openmpi`), and UCX (`ucx`) building blocks
- Adds support for container annotations
- Update many building blocks to internally use the generic building blocks.
- Updates the EasyBuild example recipe.

# v20.3.0

- Adds Nsight Systems (`nsight_systems`) building block.
- Fixes and enhancements to the LLVM (`llvm`), Mellanox OFED (`mlnx_ofed`),
  and generic (`generic_autotools`, `generic_build`, `generic_cmake`)
  building blocks.
- Adds the ability to include recipes in other recipes.
- Adds helper to query the output format in a recipe.
- Updates the GROMACS example recipe.

# v20.2.0

- Refresh default component versions for the Arm Allinea Studio
  (`arm_allinea_studio`), Boost (`boost`), CMake (`cmake`), gdrcopy
  (`gdrcopy`), HDF5(`hdf5`), Intel MPI (`intel_mpi`), Intel Parallel
  Studio runtime (`intel_psxe_runtime`), Julia (`julia`), MKL
  (`mkl`), Mellanox OFED (`mlnx_ofed`), MPICH (`mpich`), MVAPICH2
  (`mvapich2`), MVAPICH2-GDR (`mvapich2-gdr`), NetCDF (`netcdf`),
  OpenBLAS (`openblas`), OpenMPI (`openmpi`), PnetCDF (`pnetcdf`),
  PMI (`slurm_pmi2`), and UCX (`ucx`) building blocks.
- Adds git capabilities to the OpenMPI (`openmpi`) and UCX (`ucx`)
  building blocks.
- Fix issue with versioned GNU compilers on CentOS 8.
- Added support for arbitrary Autotools feature and package flags to
  the `ConfigureMake` template and all derived building blocks.
- Updates the GROMACS example recipe.
- Resolves items flagged by the code scan.

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
