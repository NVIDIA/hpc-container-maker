#!/bin/bash

NGPUS=$1

# setup data home
MILC_DATA_HOME=/data
mkdir -p $MILC_DATA_HOME
cd $MILC_DATA_HOME

SC15_DATA_HOME=$MILC_DATA_HOME/SC15
mkdir -p $SC15_DATA_HOME
cd $SC15_DATA_HOME

# pull test data if not on disk
BMARK_ARCHIVE=benchmarks.tar
if [ ! -f $BMARK_ARCHIVE ]; then
  # install wget if needed
  which wget || apt-get update \
    && apt-get install --no-install-recommends -y wget

  # pull test data
  wget http://denali.physics.indiana.edu/~sg/SC15_student_cluster_competition/$BMARK_ARCHIVE
fi
tar xf $BMARK_ARCHIVE

# configure run dir and copy over files
RUN_DIR=/sc15_cluster
rm -r $RUN_DIR 2>/dev/null || true
mkdir -p $RUN_DIR

INPUT_FILE=small.bench.in
OUTPUT_FILE=small_bench_$(date +%y-%m-%d_%H-%M)
cp -r $SC15_DATA_HOME/small $RUN_DIR/small
cp -r $SC15_DATA_HOME/ratfunc $RUN_DIR/ratfunc

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

# run benchmark
cd $RUN_DIR/small
echo "Launching with SC15 student cluster competition benchmark. Saving output to $RUN_DIR/$OUTPUT_FILE..."
mpirun --allow-run-as-root -np $NGPUS su3_rhmd_hisq -geom $GEOM $INPUT_FILE ../$OUTPUT_FILE
echo "SC15 student cluster competition benchmark complete, results can be found at $RUN_DIR/$OUTPUT_FILE"
