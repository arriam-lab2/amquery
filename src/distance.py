#!/usr/bin/env python3

import os
import numpy as np
import pickle
from bunch import Bunch
from typing import List, Callable, Mapping

from lib import iof
from lib.dist import SampleMap
from lib.pwcomp import PwMatrix
from lib.config import Config


def add(config: Config, input_files: List[str]):
    sample_map = SampleMap.load(config)
    sample_map.update(SampleMap.kmerize(config, input_files))
    sample_map.save()


def append(config: Config, input_files: List[str]):
    raise NotImplementedError("")
