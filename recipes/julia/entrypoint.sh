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
              Pkg.add([PackageSpec(name="CUDAnative", rev="v2.3.0"),
                       PackageSpec(name="CuArrays", rev="v1.2.1"),
                       PackageSpec(name="CUDAdrv", rev="v3.1.0"),
                       PackageSpec(name="GPUArrays", rev="v1.0.1")]);'
  else
    # Docker
    if [ $(id -u) -eq 0 ]; then
      # root
      echo "Re-building Julia CUDA driver package ..."
      julia -e 'using Pkg; Pkg.add(PackageSpec(name="CUDAdrv", rev="v3.1.0"));'
    else
      # non-root
      export JULIA_DEPOT_PATH=/tmp/.julia-ngc
      echo "Installing Julia CUDA packages ..."
      julia -e 'using Pkg;
                Pkg.add([PackageSpec(name="CUDAnative", rev="v2.3.0"),
                         PackageSpec(name="CuArrays", rev="v1.2.1"),
                         PackageSpec(name="CUDAdrv", rev="v3.1.0"),
                         PackageSpec(name="GPUArrays", rev="v1.0.1")]);'
    fi
  fi
fi

echo

if [[ $# -eq 0 ]]; then
  exec "/bin/bash"
else
  exec "$@"
fi
