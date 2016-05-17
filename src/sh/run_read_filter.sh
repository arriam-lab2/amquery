#!/bin/bash

directories=(
"~/storage/metagen/AlnusCheckerboard"
"~/storage/metagen/Extracellular_DNA_in_soil"
"~/storage/metagen/FL_Spatial_Study_Complete"
"~/storage/metagen/hungate_qSIP"
"~/storage/metagen/Influence_of_soil_properties_on_microbial_diversity_in_aged_PAHs_soil"
"~/storage/metagen/IPY_Thule_Metagenomics"
"~/storage/metagen/IPY_Toolik_Metagenomics"
)

NUM_THREADS=4
chmod +x read_filter.sh
parallel --no-notice --ungroup -j $NUM_THREADS ./read_filter.sh ::: "${directories[@]}"
#parallel -j $NUM_THREADS ./read_filter.sh ::: "${directories[@]}"
