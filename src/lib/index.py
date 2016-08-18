from typing import List

from .config import Config
from .distance import PwMatrix
from .tree.vptree import VpTree
from .coord_system import CoordSystem


class Index:
    def __init__(self,
                 config: Config,
                 pwmatrix: PwMatrix,
                 coord_system: CoordSystem,
                 vptree: VpTree):

        self._config = config
        self._pwmatrix = pwmatrix
        self._coord_system = coord_system
        self._vptree = vptree

    @staticmethod
    def load(config: Config):
        pwmatrix = PwMatrix.load(config)
        coord_sys = CoordSystem.load(config)
        vptree = VpTree.load(config)
        return Index(config, pwmatrix, coord_sys, vptree)

    @staticmethod
    def build(config: Config, input_files: List[str]):
        pwmatrix = PwMatrix.create(config, input_files)
        pwmatrix.save()

        coord_system = CoordSystem.calculate(config, pwmatrix)
        coord_system.save()

        vptree = VpTree.build(config, coord_system, pwmatrix)
        vptree.save()

        return Index(config, pwmatrix, coord_system, vptree)


    def refine(self):
        self._coord_system = CoordSystem.calculate(self.config,
                                                   self.pwmatrix)
        self.coord_system.save()

        self._vptree = VpTree.build(self.config,
                                    self.coord_system,
                                    self.pwmatrix)
        self.vptree.save()


    def add(self, input_files: List[str]):
        self.pwmatrix.add(input_files)
        self.pwmatrix.save()

        self.vptree.add(input_files)
        self.vptree.save()


    @property
    def pwmatrix(self) -> PwMatrix:
        return self._pwmatrix

    @property
    def coord_system(self) -> CoordSystem:
        return self._coord_system

    @property
    def vptree(self) -> VpTree:
        return self._vptree

    @property
    def config(self) -> Config:
        return self._config
