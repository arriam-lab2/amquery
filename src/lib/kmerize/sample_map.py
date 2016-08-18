#!/usr/bin/env python3

from typing import List, Mapping
import pickle

from lib.config import Config
from lib.kmerize.kmer_counter import KmerCounter
from lib.kmerize.sample import Sample


class SampleMap(dict):
    def __init__(self, config: Config, *args, **kwargs):
        self.config = config
        super(SampleMap, self).__init__(*args, **kwargs)

    @staticmethod
    def create(config: Config, sample_files: List[str]):
        sample_map = SampleMap(config)
        sample_map.add_samples(sample_files)
        return sample_map

    def add_samples(self, sample_files: List[str]) -> Mapping:
        new_samples = KmerCounter.kmerize_samples(self.config, sample_files)
        self.update(new_samples)
        return new_samples


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
