#!/bin/bash

PYTHON=python3
#OUTPUT_DIR='../../out/'
#INPUT='../../data/mikkele/100/out_rarefied/*.fna'
#INPUT='../../data/mikkele/100/out_rarefied/seqs.fna'

# multiple_rarefactions.py -i otu_table.biom -m 100 -x 100 -s 10 -n 100 -o out_rarefied_100_otu
# ./subsample.py -f ../../data/mikkele/seqs.fna -s ../../data/mikkele/seqs_otus_txt -o ../../data/mikkele/100/ ../../data/mikkele/100/out_rarefied_out/*

#metric=jaccard
#metric=jsd
#metric=bc
#metric=gji


if [ "$#" == 4 ]; then
    echo "Processing" $1"..."

    INPUT=$1
    OUTPUT_DIR=$2
    metric=$3
    k=$4
    out_dir=$OUTPUT_DIR$metric'_'$k

    echo $metric k = $k: $out_dir
    $PYTHON ../python/distance.py $INPUT -k $k -d $metric -o $out_dir --quiet
else
    echo "Usage: ./run_distance.sh <fasta> <output_dir> <metric> <kmer-size>"
    exit
fi
