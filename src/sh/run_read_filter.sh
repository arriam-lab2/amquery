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

NUM_THREADS=4
chmod +x src/read_filter.sh
parallel --no-notice --ungroup -j $NUM_THREADS src/read_filter.sh ::: "${directories[@]}"
