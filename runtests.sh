#!/bin/bash

COVERAGE=false
COVERAGE_TOOL=coverage
PYTHON=python

while [ "$1" != "" ]; do
    case $1 in
        --coverage )
            COVERAGE=true
            ;;
        --python2 )
            COVERAGE_TOOL=coverage2
            PYTHON=python2
            ;;
        --python3 )
            COVERAGE_TOOL=coverage3
            PYTHON=python3
            ;;
        --verbose )
            VERBOSE="-v"
            ;;
        * )
            ;;
    esac
    shift
done

if ${COVERAGE}; then
  ${COVERAGE_TOOL} run --source=hpccm -m unittest discover -s test ${VERBOSE}
  ${COVERAGE_TOOL} report -m
else
  ${PYTHON} -m unittest discover -s test ${VERBOSE}
fi
