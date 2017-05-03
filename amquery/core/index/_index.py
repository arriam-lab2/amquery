from typing import List

from amquery.core.distance import PwMatrix
from amquery.core.tree import VpTree, TreeDistance
from amquery.core.kmers_distr import kmerize_samples
from amquery.core.sample_map import SampleMap
from amquery.utils.config import Config
from amquery.utils.benchmarking import measure_time


class Index:
    def __init__(self,
                 config: Config,
                 pwmatrix: PwMatrix,
                 vptree: VpTree):

        self._config = config
        self._pwmatrix = pwmatrix
        self._vptree = vptree

    @measure_time(enabled=True)
    def save(self):
        self.pwmatrix.save()
        self.vptree.save()

    @staticmethod
    @measure_time(enabled=True)
    def load(config: Config):
        pwmatrix = PwMatrix.load(config)
        vptree = VpTree.load(config, pwmatrix.sample_map)
        return Index(config, pwmatrix, vptree)

    @staticmethod
    def build(config: Config, sample_files: List[str]):
        sample_map = SampleMap(config, kmerize_samples(sample_files,
                                                       config.dist.kmer_size))
        pwmatrix = PwMatrix.create(config, sample_map)
        tree_distance = TreeDistance(pwmatrix)
        vptree = VpTree(config).build(tree_distance)

        return Index(config, pwmatrix, vptree)

    def refine(self):
        self._pwmatrix = PwMatrix.create(self.config, self.pwmatrix.sample_map)
        
        tree_distance = TreeDistance(self.pwmatrix)
        self._vptree = VpTree(self.config).build(tree_distance)

    def add(self, sample_files: List[str]):
        sample_map = SampleMap(self.config,
                               kmerize_samples(sample_files,
                                               self.config.dist.kmer_size)
                               )

        self.sample_map.update(sample_map)
        tree_distance = TreeDistance(self.pwmatrix)
        self.vptree.add_samples(sample_map.values(), tree_distance)

    def find(self, sample_file: str, k: int):
        sample_map = SampleMap(self.config,
                               kmerize_samples([sample_file],
                                               self.config.dist.kmer_size)
                               )
        sample = list(sample_map.values())[0]

        tree_distance = TreeDistance(self.pwmatrix)
        values, points = self.vptree.search(sample, k, tree_distance)
        return values, points

    @property
    def config(self) -> Config:
        return self._config

    @property
    def pwmatrix(self) -> PwMatrix:
        return self._pwmatrix

    @property
    def vptree(self) -> VpTree:
        return self._vptree

    @property
    def sample_map(self) -> SampleMap:
        return self.pwmatrix.sample_map
