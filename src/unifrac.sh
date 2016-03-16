#!/bin/bash

BIOM='data/out_rarefied_otu/*.biom'
TREE='data/rep_set.tre'

UU_OUTPUT='out/un_unifrac/'
WU_OUTPUT='out/w_unifrac/'

[ -d $UU_OUTPUT ] || mkdir $UU_OUTPUT
[ -d $WU_OUTPUT ] || mkdir $WU_OUTPUT

for f in $BIOM; do
    beta_diversity.py -i $f -o $UU_OUTPUT -t $TREE -m unweighted_unifrac
    beta_diversity.py -i $f -o $WU_OUTPUT -t $TREE -m weighted_unifrac
done
