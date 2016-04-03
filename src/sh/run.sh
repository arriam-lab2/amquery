#!/bin/bash

PYTHON=python3
OUTPUT_DIR='../../out/'
INPUT='../../data/mikkele/100/out_rarefied/*.fna'
#INPUT='data/seqs.fna'

# multiple_rarefactions.py -i otu_table.biom -m 100 -x 100 -s 10 -n 100 -o out_rarefied_100_otu
# ./subsample.py -f ../../data/mikkele/seqs.fna -s ../../data/mikkele/seqs_otus_txt -o ../../data/mikkele/100/ ../../data/mikkele/100/out_rarefied_out/*

#metric=jaccard
#metric=jsd
#metric=bc
metric=gji

#for k in $(seq 20 5 100); do
k=50
    out_dir=$OUTPUT_DIR$metric'_'$k
    echo $metric k = $k: $out_dir
    $PYTHON ../python/distance.py $INPUT -k $k -d $metric -o $out_dir --quiet
#done
