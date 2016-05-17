#!/bin/bash

directories=(
"../../data/AlnusCheckerboard"
"../../data/Extracellular_DNA_in_soil"
"../../data/FL_Spatial_Study_Complete"
"../../data/hungate_qSIP"
"../../data/Influence_of_soil_properties_on_microbial_diversity_in_aged_PAHs_soil"
"../../data/IPY_Thule_Metagenomics"
"../../data/IPY_Toolik_Metagenomics"
)

PYTHON=python2
NUM_THREADS=2
chmod +x read_filter.sh
#parallel --ungroup --will-cite -j$NUM_THREADS ./read_filter.sh ::: "${directories[@]}"
parallel --no-notice --ungroup -j $NUM_THREADS read_filter.sh ::: "${directories[@]}"
