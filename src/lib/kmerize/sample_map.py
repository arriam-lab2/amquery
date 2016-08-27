#!/usr/bin/env python3

import pickle

from lib.config import Config


class SampleMap(dict):
    def __init__(self, config: Config, *args, **kwargs):
        self.config = config
        super(SampleMap, self).__init__(*args, **kwargs)

    @staticmethod
    def load(config: Config):
        with open(config.sample_map_path, 'rb') as f:
            sample_map = pickle.load(f)
            sample_map.config = config
            return sample_map

    def save(self):
        config = self.config
        del self.config
        pickle.dump(self, open(config.sample_map_path, "wb"))
        self.config = config

    @property
    def labels(self):
        return self.keys()

    @property
    def samples(self):
        return self.values()

    @property
    def paths(self):
        return [sample.kmer_index for sample in self.values()]
