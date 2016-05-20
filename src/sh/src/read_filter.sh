#!/bin/bash
# Filters reads by length and a proper sample by resulting read count

PYTHON=python3
OUTPUT_DIR="../../out/"
MIN=109
MAX=323
THRESHOLD=5000

if [ "$#" == 1 ]; then
    echo "Filtering" $1"..."
    $PYTHON ../python/read_filter.py -i $1 -o $OUTPUT_DIR --min $MIN --max $MAX --threshold $THRESHOLD
else
    echo "Usage: ./read_filter.sh <input_dir_name>"
    exit
fi
