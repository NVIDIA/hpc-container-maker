#!/bin/bash

COVERAGE=false
COVERAGE_TOOL=coverage
PYTHON=python
TEST=""

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
        --test=?*)
            TEST=${1#*=}
            ;;
        * )
            ;;
    esac
    shift
done

if ${COVERAGE}; then
    ${COVERAGE_TOOL} run --source=hpccm -m unittest discover -s test ${VERBOSE}
    ${COVERAGE_TOOL} report -m
elif [ -n "${TEST}" ]; then
    echo "Test: ${TEST}"
    ${PYTHON} -m unittest discover ${VERBOSE} -s test -p "*${TEST}*.py"
else
    ${PYTHON} -m unittest discover -s test ${VERBOSE}
fi
