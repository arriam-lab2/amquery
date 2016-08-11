#!/usr/bin/env python3

import os
import numpy as np
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

    pwmatrix_file = os.path.join(config.workon, config.current_index,
                                 'pwmatrix.txt')

    if not iof.exists(pwmatrix_file):
        open(pwmatrix_file, 'a').close()

    pwmatrix = PwMatrix.load(config, pwmatrix_file)

    sample_map = SampleMap.kmerize(config, input_files)
    pwmatrix.add(sample_map)
    pwmatrix.save()

    return pwmatrix
