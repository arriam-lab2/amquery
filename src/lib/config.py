from bunch import Bunch
from typing import Mapping
import json
import os

import lib.iof as iof


class ConfigBase(Bunch):
    def __init__(self, *args, **kwargs):
        super(ConfigBase, self).__init__(*args, **kwargs)
        self.temp = Bunch()
        self.temp.config_path = '.mgns.config'

    def load(self, workon: str):
        self.workon = iof.make_sure_exists(workon)
        if iof.exists(self.temp.config_path):
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
    def get_pwmatrix_path(self):
        return os.path.join(self.workon, self.current_index,
                            "pwmatrix.txt")

    def get_coordsys_path(self):
        raise NotImplementedError()

    def get_vptree_path(self):
        return os.path.join(self.workon, self.current_index,
                            'vptree.p')

    def get_sample_map_path(self):
        return os.path.join(self.workon, self.current_index,
                            'sample_map.p')
