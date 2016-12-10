from typing import List

from ..utils.config import Config
from .distance import PwMatrix
from .tree import VpTree, TreeDistance, neighbors

from amquery.index.coord_system import CoordSystem
from amquery.index.kmers_distr import kmerize_samples
from amquery.index.sample_map import SampleMap
from amquery.utils.benchmarking import measure_time

import time


class Index:

    def __init__(self,
                 config: Config,
                 coord_system: CoordSystem,
                 pwmatrix: PwMatrix,
                 vptree: VpTree):

        self._config = config
        self._coord_system = coord_system
        self._pwmatrix = pwmatrix
        self._vptree = vptree

    @measure_time(enabled=True)
    def save(self):
        self.coord_system.save()
        self.pwmatrix.save()
        self.vptree.save()

    @staticmethod
    @measure_time(enabled=True)
    def load(config: Config):
        coord_system = CoordSystem.load(config)
        pwmatrix = PwMatrix.load(config)
        vptree = VpTree.load(config)
        return Index(config, coord_system, pwmatrix, vptree)

    @staticmethod
    def build(config: Config, sample_files: List[str]):
        elapsed_time = []
        start = time.time()
        sample_map = SampleMap(config, kmerize_samples(sample_files,
                                                       config.dist.kmer_size))

        elapsed_time.append(time.time() - start)
        start = time.time()

        pwmatrix = PwMatrix.create(config, sample_map)
        elapsed_time.append(time.time() - start)
        start = time.time()

        coord_system = CoordSystem.calculate(config, pwmatrix)
        elapsed_time.append(time.time() - start)
        start = time.time()

        tree_distance = TreeDistance(coord_system, pwmatrix)
        vptree = VpTree.build(config, tree_distance)
        elapsed_time.append(time.time() - start)

        return Index(config, coord_system, pwmatrix, vptree), elapsed_time

    def refine(self):
        self._coord_system = CoordSystem.calculate(self.config,
                                                   self.pwmatrix)
        tree_distance = TreeDistance(self.coord_system, self.pwmatrix)
        self._vptree = VpTree.build(self.config, tree_distance)

    def add(self, sample_files: List[str]):
        elapsed_time = []
        start = time.time()
        sample_map = SampleMap(self.config,
                               kmerize_samples(sample_files,
                                               self.config.dist.kmer_size)
                               )

        self.sample_map.update(sample_map)
        elapsed_time.append(time.time() - start)
        start = time.time()

        tree_distance = TreeDistance(self.coord_system, self.pwmatrix)
        self.vptree.add_samples(sample_map.values(), tree_distance)
        elapsed_time.append(time.time() - start)
        return elapsed_time

    def find(self, sample_file: str, k: int):
        sample_map = SampleMap(self.config,
                               kmerize_samples([sample_file],
                                               self.config.dist.kmer_size)
                               )
        sample = list(sample_map.values())[0]

        tree_distance = TreeDistance(self.coord_system, self.pwmatrix)
        values, points = neighbors(self.vptree, sample, k, tree_distance)
        return values, points

    @property
    def config(self) -> Config:
        return self._config

    @property
    def coord_system(self) -> CoordSystem:
        return self._coord_system

    @property
    def pwmatrix(self) -> PwMatrix:
        return self._pwmatrix

    @property
    def vptree(self) -> VpTree:
        return self._vptree

    @property
    def sample_map(self) -> SampleMap:
        return self.pwmatrix.sample_map
