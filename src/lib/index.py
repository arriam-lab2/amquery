from typing import List

from .config import Config
from .sample_map import SampleMap
from .distance import PwMatrix
from .vptree import VpTree
from .coord_system import CoordSystem

class Index:
    def __init__(self,
                 config: Config,
                 sample_map: SampleMap,
                 pwmatrix: PwMatrix,
                 coord_system: CoordSystem,
                 vptree: VpTree):

        self._config = config
        self._sample_map = sample_map
        self._pwmatrix = pwmatrix
        self._coord_system = coord_system
        self._vptree = vptree

    @staticmethod
    def load(config: Config):
        sample_map = SampleMap.load(config)
        pwmatrix = PwMatrix.load(config, sample_map)
        coord_sys = CoordSystem.load(config)
        return Index(config, sample_map, pwmatrix, coord_sys)

    @staticmethod
    def build(config: Config, input_files: List[str]):
        sample_map = SampleMap.load(config).register(input_files)
        #sample_map.save()

        pwmatrix = PwMatrix.calculate(config, sample_map)
        pwmatrix.save()
        #pwmatrix = PwMatrix.load(config, sample_map)

        coord_system = CoordSystem.calculate(config, pwmatrix)
        coord_system.save()
        #coord_system = CoordSystem.load(config)
        #print(coord_system)

        vptree = VpTree.build(config, coord_system, pwmatrix)

        return Index(config, sample_map, pwmatrix, coord_system, vptree)

    @staticmethod
    def _add_samples(config: Config, input_files: List[str]) -> SampleMap:
        sample_map = SampleMap.load(config)
        sample_map.update(SampleMap.kmerize(config, input_files))
        sample_map.save()
        return sample_map

    @property
    def sample_map(self) -> SampleMap:
        return self._sample_map

    @property
    def pwmatrix(self) -> PwMatrix:
        return self._pwmatrix

    @property
    def coord_system(self) -> CoordSystem:
        return self._coord_system

    @property
    def vptree(self) -> VpTree:
        return self._vptree
