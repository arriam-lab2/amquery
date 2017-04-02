#!/usr/bin/env python3

import joblib

from amquery.utils.config import Config


class SampleMap(dict):

    def __init__(self, config: Config, *args, **kwargs):
        self.config = config
        super(SampleMap, self).__init__(*args, **kwargs)

    @staticmethod
    def load(config: Config):
        sample_map = joblib.load(config.sample_map_path)
        sample_map.config = config
        return sample_map

    def save(self):
        config = self.config
        del self.config
        joblib.dump(self, config.sample_map_path)
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
