#!/bin/bash

NGPUS=$1

# setup data home
MILC_DATA_HOME=/data
mkdir -p $MILC_DATA_HOME
cd $MILC_DATA_HOME

# pull test data if not on disk
CHKLAT=36x36x36x72.chklat
if [ ! -f $CHKLAT ]; then
  # install wget if needed
  which wget || apt-get update \
    && apt-get install --no-install-recommends -y wget

  # pull test data
  wget http://portal.nersc.gov/project/m888/apex/MILC_lattices/$CHKLAT
fi

if [ ! -f MILC_160413.tgz ]; then
  # install wget if needed
  which wget || apt-get update \
    && apt-get install --no-install-recommends -y wget

  wget http://portal.nersc.gov/project/m888/apex/MILC_160413.tgz
fi
tar xf MILC_160413.tgz

# configure run dir and copy over files
RUN_DIR=/apex
rm -r $RUN_DIR 2>/dev/null || true
mkdir -p $RUN_DIR

INPUT_FILE=input
OUTPUT_FILE=apex_result_$(date +%y-%m-%d_%H-%M)
cp /workspace/examples/inputs/$INPUT_FILE $RUN_DIR
cp $MILC_DATA_HOME/MILC-apex/benchmarks/rationals_m001m05m5.test1 $RUN_DIR
cp $MILC_DATA_HOME/$CHKLAT $RUN_DIR

case $NGPUS in
  1)
    GEOM="1 1 1 1"
    ;;
  2)
    GEOM="1 1 1 2"
    ;;
  4)
    GEOM="1 1 1 4"
    ;;
  8)
    GEOM="1 1 2 4"
    ;;
esac

# run APEX
cd $RUN_DIR
echo "Launching with APEX workload. Saving output to $RUN_DIR/$OUTPUT_FILE..."
mpirun --allow-run-as-root -np $NGPUS su3_rhmd_hisq -geom $GEOM $INPUT_FILE $OUTPUT_FILE
echo "APEX workload complete, results can be found at $RUN_DIR/$OUTPUT_FILE"
