#!/usr/bin/env python3

import os
import numpy as np
import pickle
from bunch import Bunch
from typing import List, Callable, Mapping

from lib import iof
from lib.dist import SampleMap, LoadApply
from lib.pwcomp import PwMatrix, PairwiseDistance
from lib.config import Config


def add(config: Config, input_files: List[str]):
    kmer_size = config.dist.kmer_size
    kmer_output_dir = iof.make_sure_exists(
        os.path.join(config.workon, config.current_index,
                     "kmers." + str(kmer_size))
    )

    #pwmatrix_file = os.path.join(config.workon, config.current_index,
    #                             'pwmatrix.txt')

    #if not iof.exists(pwmatrix_file):
    #    open(pwmatrix_file, 'a').close()

    #pwmatrix = PwMatrix.load(config, pwmatrix_file)
    
    sample_map = SampleMap()
    with open(config.get_sample_map_path(), 'rb') as f:
        sample_map = pickle.load(f)
        
    sample_map.update(SampleMap.kmerize(config, input_files))
    print(sample_map.mapping)
    pickle.dump(sample_map, open(config.get_sample_map_path(), "wb"))
    
    #pwmatrix.recalc(sample_map)
    #pwmatrix.save()
    #return pwmatrix


def append(config: Config, input_files: List[str]):
    pass
