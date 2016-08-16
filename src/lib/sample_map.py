#!/usr/bin/env python3

from typing import List
import pickle

from .config import Config
from .kmerize import KmerCounter


class SampleMap(dict):
    def __init__(self, config: Config, *args, **kwargs):
        self.config = config
        super(SampleMap, self).__init__(*args, **kwargs)

    def register(self, sample_files: List[str]):
        self.update(KmerCounter.kmerize_samples(self.config, sample_files))
        return self

    @staticmethod
    def load(config: Config):
        try:
            with open(config.sample_map_path, 'rb') as f:
                sample_map = pickle.load(f)
                sample_map.config = config
        except IOError:
            sample_map = SampleMap(config)

        return sample_map

    def save(self, config):
        config = self.config
        del self.config
        pickle.dump(self, open(config.sample_map_path, "wb"))

    @property
    def labels(self):
        return self.keys()

    @property
    def paths(self):
        return self.values()
