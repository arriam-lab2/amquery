#!/bin/bash


if [ "$#" == 0 ]; then
    echo "Usage: ./run_read_filters.sh <DIRECTORIES>"
    exit
else
    NUM_THREADS=4
    PYTHON=python3
    SCRIPT=../python/read_filter.py
    MIN=109
    MAX=323
    THRESHOLD=500
    #CUT=208
    CUT=0
    OUTPUT=../../out/

    parallel --no-notice --ungroup -j $NUM_THREADS $PYTHON $SCRIPT \
    {1} --min {2} --max {3} --threshold {4} --cut {5} -o {6} \
    ::: "$@" ::: $MIN ::: $MAX ::: $THRESHOLD ::: $CUT ::: $OUTPUT

fi
