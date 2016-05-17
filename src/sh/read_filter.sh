#!/bin/bash

OUTPUT_DIR="../../out/"
MIN=109
MAX=323

if [ "$#" == 1 ] && [ -d "$1" ]; then
    echo "Filtering" $1"..."
    python3 ../python/read_filter.py -i $1 -o $OUTPUT_DIR --min $MIN --max $MAX
else
    echo "Usage: ./read_filter.sh <input_dir_name>"
    exit
fi
