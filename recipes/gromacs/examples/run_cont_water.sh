#!/bin/bash

NGPUS=${1:-1}
BASEDIR=$(dirname "$0")
$BASEDIR/run_cont.sh $NGPUS water_GMX50_bare water-cut1.0_GMX50_bare/1536 pme.mdp
