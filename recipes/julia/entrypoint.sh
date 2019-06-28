#!/bin/bash

set -e

if [[ "$(find /usr /.singularity.d -name libcuda.so.1 2>/dev/null) " == " " || "$(ls /dev/nvidiactl) " == " " ]]; then
  echo
  echo "WARNING: The NVIDIA Driver was not detected.  GPU functionality will not be available."
else
  # Enable GPU support
  if [ -d /.singularity.d ]; then
    # Singularity
    echo "Installing Julia CUDA packages (one-time) ..."
    julia -e 'using Pkg;
              Pkg.add([PackageSpec(name="CUDAnative", rev="v2.1.3"),
                       PackageSpec(name="CuArrays"),
                       PackageSpec(name="CUDAdrv"),
                       PackageSpec(name="GPUArrays")]);'
  else
    # Docker
    if [ $(id -u) -eq 0 ]; then
      # root
      echo "Re-building Julia CUDA driver package ..."
      julia -e 'using Pkg; Pkg.add("CUDAdrv"); Pkg.build("CuArrays")'
    else
      # non-root
      export JULIA_DEPOT_PATH=/tmp/.julia-ngc
      echo "Installing Julia CUDA packages ..."
      julia -e 'using Pkg;
                Pkg.add([PackageSpec(name="CUDAnative", rev="v2.1.3"),
                         PackageSpec(name="CuArrays"),
                         PackageSpec(name="CUDAdrv"),
                         PackageSpec(name="GPUArrays")]);'
    fi
  fi
fi

echo

if [[ $# -eq 0 ]]; then
  exec "/bin/bash"
else
  exec "$@"
fi
