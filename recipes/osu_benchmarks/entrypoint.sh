#!/bin/bash
set -e

if [[ "$(find /usr /.singularity.d -name libcuda.so.1 2>/dev/null) " == " " || "$(ls /dev/nvidiactl 2>/dev/null) " == " " ]]; then
  echo
  echo "WARNING: The NVIDIA Driver was not detected.  GPU functionality will not be available."
  if [[ -d /.singularity.d ]]; then
    echo "Use 'singularity run --nv' to start this container; see"
    echo "https://sylabs.io/guides/3.5/user-guide/gpu.html"
  else
    echo "Use 'docker run --gpus all' to start this container; see"
    echo "https://github.com/NVIDIA/nvidia-docker/wiki/Installation-(Native-GPU-Support)"
  fi
  echo
fi

if [ ! -d /dev/infiniband ]; then
  echo "WARNING: No InfiniBand devices detected."
  echo "         Multi-node communication performance may be reduced."
  echo
fi

DETECTED_MOFED=$(cat /sys/module/mlx5_core/version 2>/dev/null || true)
if [ -n "${DETECTED_MOFED}" ]; then
  if [[ ${DETECTED_MOFED} =~ ^5 ]]; then
    # do nothing, use default config
    echo "Detected MOFED ${DETECTED_MOFED}."
  elif [[ ${DETECTED_MOFED} =~ ^4 ]]; then
    case "${DETECTED_MOFED}" in
      4.2*)
	UPDATE_MOFED="4.2-1.5.1.0"
        ;;
      4.3*)
	UPDATE_MOFED="4.3-1.0.1.0"
        ;;
      4.4*)
	UPDATE_MOFED="4.4-1.0.0.0"
        ;;
      4.5*)
	UPDATE_MOFED="4.5-1.0.1.0"
        ;;
      4.6*)
	UPDATE_MOFED="4.6-1.0.1.1"
	;;
      4.7*)
	UPDATE_MOFED="4.7-3.2.9.0"
        ;;
      4.9*)
        UPDATE_MOFED="4.9-0.1.7.0"
        ;;
      *)
        echo "ERROR: Detected MOFED driver ${DETECTED_MOFED}, but this container does not support it."
        echo "       Use of RDMA for multi-node communication will be unreliable."
        sleep 2
	;;
      esac

      if [ -n "${UPDATE_MOFED}" ]; then
        echo "NOTE: Detected MOFED driver ${DETECTED_MOFED}; version automatically updated."
        export PATH=/usr/local/ofed/${UPDATE_MOFED}/usr/bin:$PATH
        export LD_LIBRARY_PATH=/usr/local/ofed/${UPDATE_MOFED}/usr/lib:/usr/local/ofed/${UPDATE_MOFED}/usr/lib/libibverbs:$LD_LIBRARY_PATH
      fi
  else 
    echo "ERROR: Detected MOFED driver ${DETECTED_MOFED}, but this container does not support it."
    echo "       Use of RDMA for multi-node communication will be unreliable."
    sleep 2
  fi
else
  echo "NOTE: MOFED driver for multi-node communication was not detected."
  echo "      Multi-node communication performance may be reduced."
fi

DETECTED_NVPEERMEM=$(cat /sys/module/nv_peer_mem/version 2>/dev/null || true)
if [[ "${DETECTED_MOFED} " != " " && "${DETECTED_NVPEERMEM} " == " " ]]; then
  echo
  echo "NOTE: MOFED driver was detected, but nv_peer_mem driver was not detected."
  echo "      Multi-node communication performance may be reduced."
fi

# set PMIx client configuration to match the server
# enroot already handles this, so only do this under singularity
# https://github.com/NVIDIA/enroot/blob/master/conf/hooks/extra/50-slurm-pmi.sh
if [[ -z "${SLURM_MPI_TYPE-}" || "${SLURM_MPI_TYPE}" == pmix* ]]; then
    if [ -d /.singularity.d ]; then
        echo "Configuring PMIX"

        if [ -n "${PMIX_PTL_MODULE-}" ] && [ -z "${PMIX_MCA_ptl-}" ]; then
            export PMIX_MCA_ptl=${PMIX_PTL_MODULE}
        fi
        if [ -n "${PMIX_SECURITY_MODE-}" ] && [ -z "${PMIX_MCA_psec-}" ]; then
            export PMIX_MCA_psec=${PMIX_SECURITY_MODE}
        fi
        if [ -n "${PMIX_GDS_MODULE-}" ] && [ -z "${PMIX_MCA_gds-}" ]; then
            export PMIX_MCA_gds=${PMIX_GDS_MODULE}
         fi
    fi
fi

echo

if [[ $# -eq 0 ]]; then
  exec "/bin/bash"
else
  exec "$@"
fi
