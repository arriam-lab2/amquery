#!/bin/bash

PYTHON=python3
OUTPUT_DIR='out/'
INPUT='data/out_rarefied/*.fna'
#INPUT='data/seqs.fna'

metric=jaccard
#metric=jsd

for k in $(seq 20 5 100); do
#k=50
    out_dir=$OUTPUT_DIR$metric'_'$k
    echo $metric k = $k: $out_dir
    $PYTHON distance.py $INPUT -k $k -d $metric -o $out_dir --quiet
done

