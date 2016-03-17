#!/bin/bash

BIOM='../../data/mikkele/100/out_rarefied_otu/*.biom'
NUM_THREADS=4

chmod +x unifrac.sh
ls $BIOM | parallel --will-cite -j $NUM_THREADS ./unifrac.sh
