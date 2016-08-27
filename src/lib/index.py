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
        print("Registering", sample_file)
        sample = Sample(sample_file)
        kmer_index.register(sample)
        sample_map[sample_file] = sample

    return SampleMap(config, sample_map)


class Index:
    def __init__(self,
                 config: Config,
                 coord_system: CoordSystem,
                 vptree: VpTree,
                 kmer_index: PrimaryKmerIndex):

        self._config = config
        self._coord_system = coord_system
        self._vptree = vptree
        self._kmer_index = kmer_index

    @staticmethod
    def load(config: Config):
        coord_sys = CoordSystem.load(config)
        vptree = VpTree.load(config)
        return Index(config, coord_sys, vptree)

    @staticmethod
    def build(config: Config, sample_files: List[str]):
        kmer_index = PrimaryKmerIndex(config)
        sample_map = _register(config, sample_files, kmer_index)

        pwmatrix = PwMatrix.create(config, sample_map)
        pwmatrix.save()

        coord_system = CoordSystem.calculate(config, pwmatrix)
        coord_system.save()

        vptree = VpTree.build(config, coord_system, pwmatrix)
        vptree.save()

        return Index(config, coord_system, vptree, kmer_index)

    def refine(self):
        pwmatrix = PwMatrix.load(self.config)
        self._coord_system = CoordSystem.calculate(self.config,
                                                   pwmatrix)
        self.coord_system.save()

        self._vptree = VpTree.build(self.config,
                                    self.coord_system,
                                    self.pwmatrix)
        self.vptree.save()

    def add(self, sample_files: List[str]):
        sample_map = _register(self.config,
                               sample_files,
                               self.kmer_index)
        self.vptree.add_samples(sample_map)
        self.vptree.save()

    @property
    def coord_system(self) -> CoordSystem:
        return self._coord_system

    @property
    def vptree(self) -> VpTree:
        return self._vptree

    @property
    def config(self) -> Config:
        return self._config
