from bunch import Bunch
from typing import Mapping
import json
import os

from ..iof import exists, make_sure_exists


class ConfigBase(Bunch):

    def __init__(self, *args, **kwargs):
        super(ConfigBase, self).__init__(*args, **kwargs)
        self.temp = Bunch()
        self.temp.config_path = '.amq.config'

    def load(self, workon: str):
        self.workon = make_sure_exists(workon)
        if exists(self.temp.config_path):
            with open(self.temp.config_path) as data_file:
                loaded_dict = json.load(data_file)
                self.update(loaded_dict)

    def save(self):
        config_path = self.temp.config_path
        del self.temp

        with open(config_path, "w") as f:
            print("", json.dumps(self), file=f)

    def update(self, dictionary: Mapping):
        for k, v in dictionary.items():
            if type(v) == dict:
                self[k] = Bunch()
                self[k].update(v)
            else:
                self[k] = v


class Config(ConfigBase):

    @property
    def index_path(self):
        return os.path.join(self.workon, self.current_index)

    @property
    def primary_kmer_index_path(self):
        return os.path.join(self.index_path, "primary_index.p")

    @property
    def pwmatrix_path(self):
        return os.path.join(self.index_path, "pwmatrix.txt")

    @property
    def coordsys_path(self):
        return os.path.join(self.index_path, "coord_system.p")

    @property
    def vptree_path(self):
        return os.path.join(self.index_path, "vptree.p")

    @property
    def sample_map_path(self):
        return os.path.join(self.index_path, "sample_map.p")

    @property
    def kmers_dir(self):
        return os.path.join(self.index_path,
                            "kmers." + str(self.dist.kmer_size))
