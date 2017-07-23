import os
import json
from amquery.utils.iof import make_sure_exists
from amquery.utils.config import get_samplemap_path, get_sample_dir, get_kmers_dir
from amquery.core.sample import Sample


class SampleMap(dict):
    def __init__(self, *args, **kwargs):
        super(SampleMap, self).__init__(*args, **kwargs)

    @staticmethod
    def load():
        with open(get_samplemap_path()) as json_data:
            hash_list = json.load(json_data)
            return SampleMap({id: Sample.load(os.path.join(get_sample_dir(), id)) for id in hash_list})

    def _save(self):
        make_sure_exists(get_kmers_dir())

        for sample in self.samples:
            sample.save()

        hash_list = [sample.name for sample in self.samples]
        with open(get_samplemap_path(), 'w') as outfile:
            json.dump(hash_list, outfile)

    def save(self):
        self._save()

    @property
    def labels(self):
        return self.keys()

    @property
    def samples(self):
        return self.values()

    @property
    def paths(self):
        return [sample.kmer_index for sample in self.values()]
