#!/bin/bash


if [ "$#" == 0 ]; then
    echo "Usage: ./run_read_filters.sh <DIRECTORIES>"
    exit
else
    NUM_THREADS=4
    chmod +x src/read_filter.sh
    parallel --no-notice --ungroup -j $NUM_THREADS src/read_filter.sh ::: "$@"

fi
