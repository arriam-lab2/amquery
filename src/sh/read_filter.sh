#!/bin/bash

PYTHON=python2

OUTPUT_DIR="../../out/"
MIN=109
MAX=323

echo $1

if [ "$#" == 1 ]; then
    echo "Filtering" $1"..."
    PYTHON ../python/read_filter.py -i $1 -o $OUTPUT_DIR --min $MIN --max $MAX
else
    echo "Usage: ./read_filter.sh <input_dir_name>"
    exit
fi
