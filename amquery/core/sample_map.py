import os
import json

from amquery.core.sample import Sample
from amquery.utils.iof import make_sure_exists
from amquery.utils.config import get_kmers_dir, get_samplemap_path, get_sample_dir


class SampleMap(dict):
    def __init__(self, *args, **kwargs):
        super(SampleMap, self).__init__(*args, **kwargs)

    @staticmethod
    def load(database_config):
        database_name = database_config["name"]
        with open(get_samplemap_path(database_name)) as json_data:
            hash_list = json.load(json_data)
            return SampleMap({id: Sample.load(os.path.join(get_sample_dir(database_name), id)) for id in hash_list})

    def save(self, database_name):
        make_sure_exists(get_kmers_dir(database_name))
    
        for sample in self.samples:
            sample.save()

        hash_list = [sample.name for sample in self.samples]
        with open(get_samplemap_path(database_name), 'w') as outfile:
            json.dump(hash_list, outfile)


    @property
    def labels(self):
        return self.keys()

    @property
    def samples(self):
        return self.values()

    @property
    def paths(self):
        return [sample.kmer_index for sample in self.values()]
