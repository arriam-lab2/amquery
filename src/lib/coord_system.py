#!/usr/bin/env python3

import itertools
import random
import numpy as np
import pickle
from typing import List

from genetic.individuals import SingleChromosomeIndividual
from genetic.populations import PanmicticPopulation
from genetic.selection import bimodal

from lib.distance import PwMatrix
from lib.config import Config
from lib.kmerize.sample_map import SampleMap


class Engine:
    def __init__(self, names):
        self.names = np.array(list(names))

    def __call__(self, val=None, chromosome=None):
        elem = random.choice(self.names)
        idx = np.where(self.names == elem)[0][0]
        return val if chromosome and idx in chromosome else idx


def _crossover(chr1, chr2):
    """
    :rtype: list
    """
    if len(chr1) != len(chr2):
        raise ValueError("Incompatible species can't mate")
    unique = list(set(itertools.chain(chr1, chr2)))
    # note: it's a bit faster to use `unique = set(chr1);
    #       unique.update(chr2)`, though not as functionally pure.

    return tuple(random.sample(unique, len(chr1)))


class Fitness:
    def __init__(self, pwmatrix: PwMatrix):
        self.pwmatrix = pwmatrix

    def __call__(self, indiv: SingleChromosomeIndividual):
        return self._total_corr(indiv.genome)

    def _choose(self, names_idx: List[int]):
        names_idx = sorted(names_idx)
        return self.pwmatrix.matrix[np.ix_(names_idx, names_idx)]

    def _total_corr(self, names_idx: List[int]):
        dmx = self._choose(names_idx)
        corrs = np.corrcoef(dmx)
        sums = np.apply_along_axis(sum, 1, corrs)
        total_pc = np.apply_along_axis(sum, 0, sums)
        return -1. * float(total_pc)


def random_chr(names: List[str], k: int):
    return random.sample(range(len(names)), k)


class CoordSystem(dict):
    def __init__(self, config: Config, *args, **kwargs):
        self.config = config
        super(CoordSystem, self).__init__(*args, **kwargs)

    @staticmethod
    def calculate(config: Config, pwmatrix: PwMatrix = None):
        coord_system_size = config.genetic.coord_system_size
        generations = config.genetic.generations
        mutation_rate = config.genetic.mutation_rate
        population_size = config.genetic.population_size
        select_rate = config.genetic.select_rate
        random_select_rate = config.genetic.random_select_rate
        legend_size = config.genetic.legend_size

        if not pwmatrix:
            pwmatrix = PwMatrix.load(config)

        engine = Engine(pwmatrix.labels)
        fitness = Fitness(pwmatrix)
        ancestors = [SingleChromosomeIndividual(engine, mutation_rate,
                                                coord_system_size,
                                                random_chr(pwmatrix.labels,
                                                           coord_system_size))
                     ] * 2

        selection = bimodal(fittest_fraction=select_rate,
                            other_random_survival=random_select_rate)

        population = PanmicticPopulation(ancestors, population_size, fitness,
                                         selection, legend_size)

        average_fitness = list(population.evolve(generations))
        best_solution = np.argmin([legend[0] for legend in population.legends])
        labels_idx = population.legends[best_solution][1].genome

        labels_array = np.array(list(pwmatrix.labels))
        basis_labels = list(labels_array[np.ix_(list(labels_idx))])
        basis_map = dict((k, pwmatrix.sample_map[k]) for k in basis_labels)
        basis = SampleMap(config, basis_map)
        return CoordSystem(config, basis)

    @staticmethod
    def load(config: Config):
        with open(config.coordsys_path, 'rb') as f:
            coord_system = pickle.load(f)
            coord_system.config = config
            return coord_system

    def save(self):
        config = self.config
        del self.config
        pickle.dump(self, open(config.coordsys_path, "wb"))
        self.config = config


if __name__ == "__main__":
    raise RuntimeError()
