#!/bin/bash

NGPUS=${1:-1}
BASEDIR=$(dirname "$0")
echo $NGPUS
$BASEDIR/run_cont.sh $NGPUS ADH_bench_systems adh_cubic pme_verlet.mdp
