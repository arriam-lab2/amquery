#!/bin/bash

TREE='data/rep_set.tre'

UU_OUTPUT='out/un_unifrac/'
WU_OUTPUT='out/w_unifrac/'


[ -d $UU_OUTPUT ] || mkdir $UU_OUTPUT
[ -d $WU_OUTPUT ] || mkdir $WU_OUTPUT

if [ "$#" -ne 1 ]; then
    read -r filename
else
    filename=$1
fi

echo "Processing "$filename
beta_diversity.py -i $filename -o $UU_OUTPUT -t $TREE -m unweighted_unifrac
beta_diversity.py -i $filename -o $WU_OUTPUT -t $TREE -m weighted_unifrac
