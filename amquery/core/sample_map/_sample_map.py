#!/usr/bin/env python3

import os
import json

from amquery.utils.iof import make_sure_exists
from amquery.utils.decorators import hide_field
from amquery.core.sample import Sample


class SampleMap(dict):
    def __init__(self, config, *args, **kwargs):
        self.config = config
        super(SampleMap, self).__init__(*args, **kwargs)

    @staticmethod
    def load(config):
        with open(config.sample_map_path) as json_data:
            hash_list = json.load(json_data)
            samples = { hash: Sample.load(config, os.path.join(config.sample_dir, hash)) \
                        for hash in hash_list }

            sample_map = SampleMap(config, samples)
            sample_map.config = config
            return sample_map

    @hide_field("config")
    def _save(self, config):
        make_sure_exists(config.sample_dir)
        make_sure_exists(config.kmer_index_dir)

        for sample in self.samples:
            sample.save(config)

        hash_list = [sample.name for sample in self.samples]
        with open(config.sample_map_path, 'w') as outfile:
            json.dump(hash_list, outfile)

    def save(self):
        self._save(self.config)

    @property
    def labels(self):
        return self.keys()

    @property
    def samples(self):
        return self.values()

    @property
    def paths(self):
        return [sample.kmer_index for sample in self.values()]
