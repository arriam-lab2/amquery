from typing import List

from .config import Config
from .distance import PwMatrix
from .tree.vptree import VpTree
from .tree.search import neighbors
from .coord_system import CoordSystem
from lib.kmerize.kmer_index import kmerize_samples
from lib.kmerize.sample_map import SampleMap
from lib.benchmarking import measure_time


class Index:
    def __init__(self,
                 config: Config,
                 coord_system: CoordSystem,
                 vptree: VpTree):

        self._config = config
        self._coord_system = coord_system
        self._vptree = vptree

    @measure_time(enabled=True)
    def save(self):
        self.coord_system.save()
        self.vptree.save()

    @staticmethod
    @measure_time(enabled=True)
    def load(config: Config):
        coord_sys = CoordSystem.load(config)
        vptree = VpTree.load(config)
        return Index(config, coord_sys, vptree)

    @staticmethod
    def build(config: Config, sample_files: List[str]):
        sample_map = SampleMap(config, kmerize_samples(sample_files,
                                                       config.dist.kmer_size))
        pwmatrix = PwMatrix.create(config, sample_map)
        coord_system = CoordSystem.calculate(config, pwmatrix)
        vptree = VpTree.build(config, coord_system, pwmatrix)

        return Index(config, coord_system, vptree)

    def refine(self):
        pwmatrix = PwMatrix.load(self.config)
        self._coord_system = CoordSystem.calculate(self.config,
                                                   pwmatrix)
        self._vptree = VpTree.build(self.config,
                                    self.coord_system,
                                    pwmatrix)

    def add(self, sample_files: List[str]):
        sample_map = SampleMap(self.config,
                               kmerize_samples(sample_files,
                                               self.config.dist.kmer_size)
                               )

        self.sample_map.update(sample_map)
        self.vptree.add_samples(sample_map.values())

    def find(self, sample_file: str, k: int):
        sample_map = SampleMap(self.config,
                               kmerize_samples([sample_file],
                                               self.config.dist.kmer_size)
                               )
        sample = list(sample_map.values())[0]

        values, points = neighbors(self.vptree, sample, k)
        return values, points

    @property
    def coord_system(self) -> CoordSystem:
        return self._coord_system

    @property
    def vptree(self) -> VpTree:
        return self._vptree

    @property
    def sample_map(self) -> SampleMap:
        return self.vptree.sample_map

    @property
    def config(self) -> Config:
        return self._config
