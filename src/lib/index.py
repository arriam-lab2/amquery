from typing import List

from .config import Config
from .distance import PwMatrix
from .tree.vptree import VpTree
from .coord_system import CoordSystem
from lib.kmerize.kmer_index import PrimaryKmerIndex
from lib.kmerize.sample import Sample
from lib.kmerize.sample_map import SampleMap


def _register(config: Config,
              sample_files: List[str],
              kmer_index: PrimaryKmerIndex) -> SampleMap:

    sample_map = {}
    for sample_file in sample_files:
        sample = Sample(sample_file)
        kmer_index.register(sample)
        sample_map[sample_file] = sample

    return SampleMap(config, sample_map)


def _unify(sample_map: SampleMap,
           kmer_index: PrimaryKmerIndex) -> SampleMap:

    for sample in sample_map.values():
        kmer_index.extend_sample_distribution(sample)

    return sample_map


class Index:
    def __init__(self,
                 config: Config,
                 kmer_index: PrimaryKmerIndex,
                 coord_system: CoordSystem,
                 vptree: VpTree):

        self._config = config
        self._kmer_index = kmer_index
        self._coord_system = coord_system
        self._vptree = vptree

    def save(self):
        self.kmer_index.save()
        self.coord_system.save()
        self.vptree.save()

    @staticmethod
    def load(config: Config):
        coord_sys = CoordSystem.load(config)
        vptree = VpTree.load(config)
        kmer_index = PrimaryKmerIndex.load(config)
        return Index(config, kmer_index, coord_sys, vptree)

    @staticmethod
    def build(config: Config, sample_files: List[str]):
        kmer_index = PrimaryKmerIndex(config)
        sample_map = _register(config, sample_files, kmer_index)
        sample_map = _unify(sample_map, kmer_index)

        pwmatrix = PwMatrix.create(config, sample_map)
        coord_system = CoordSystem.calculate(config, pwmatrix)
        vptree = VpTree.build(config, coord_system, pwmatrix)

        return Index(config, kmer_index, coord_system, vptree)

    def refine(self):
        pwmatrix = PwMatrix.load(self.config)
        self._coord_system = CoordSystem.calculate(self.config,
                                                   pwmatrix)
        self._vptree = VpTree.build(self.config,
                                    self.coord_system,
                                    self.pwmatrix)

    def add(self, sample_files: List[str]):
        sample_map = _register(self.config,
                               sample_files,
                               self.kmer_index)
        new_samples = sample_map.values()

        self.vptree.sample_map.update(sample_map)
        sample_map = _unify(self.vptree.sample_map, self.kmer_index)

        self.vptree.add_samples(new_samples)

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

    @property
    def kmer_index(self) -> PrimaryKmerIndex:
        return self._kmer_index
