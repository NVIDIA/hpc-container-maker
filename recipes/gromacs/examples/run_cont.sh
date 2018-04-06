#!/bin/bash

NGPUS=$1
DATASET=$2
DATA_DIR=$3
GROMPP_FILE=$4
NSTEPS=10000

# setup data home
GROMACS_DATA_HOME=/data
mkdir -p $GROMACS_DATA_HOME
cd $GROMACS_DATA_HOME

# pull test data if not on disk
if [ ! -f ${DATASET}.tar.gz ]; then
  # install wget if needed
  $(which wget) || apt-get update \
    && apt-get install --no-install-recommends -y wget

  # pull test data
  wget ftp://ftp.gromacs.org/pub/benchmarks/${DATASET}.tar.gz
fi

tar xvf ${DATASET}.tar.gz

# prepare test data if needed
if [ ! -f pme_verlet.mdp ]; then
  cd $DATA_DIR
  gmx grompp -f $GROMPP_FILE
fi

LASTCORE=$(lscpu | grep On-line | cut -f3 -d"-")
THREADSPER=$(lscpu | grep Thread | cut -f2 -d":")
OMP_NUM_THREADS=$(( ( ((LASTCORE+1)/NGPUS) / THREADSPER) ))
if [ "${OMP_NUM_THREADS}" -gt "${OMP_MAX_THREADS}" ] ; then
    OMP_NUM_THREADS="${OMP_MAX_THREADS}"
fi
export OMP_NUM_THREADS="${GMX_NTHREADS:-$OMP_NUM_THREADS}"

# setup work dir
WORK_DIR=/tmp/gmx
mkdir -p $WORK_DIR
cd $WORK_DIR

gmx mdrun \
  -nb gpu \
  -ntmpi ${NGPUS} \
  -pin on \
  -resethway \
  -v \
  -noconfout \
  -nsteps ${NSTEPS} \
  -s $GROMACS_DATA_HOME/$DATA_DIR/topol.tpr \
  -ntomp $OMP_NUM_THREADS
