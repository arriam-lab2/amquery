#!/usr/bin/env python3

import os
import itertools
import random
import numpy as np
import joblib
import json
import scipy
from scipy import stats
from typing import List

from genetic.individuals import SingleChromosomeIndividual
from genetic.populations import PanmicticPopulation
from genetic.selection import bimodal
from amquery.core.distance import PwMatrix
from amquery.core.sample_map import SampleMap
from amquery.core.sample import Sample
from amquery.utils.config import Config
from amquery.utils.benchmarking import measure_time
from amquery.utils.decorators import hide_field


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
        return self.fitness_function(indiv.genome)

    def _choose(self, names_idx: List[int]):
        names_idx = sorted(names_idx)
        return self.pwmatrix.matrix[np.ix_(names_idx, names_idx)]

    def fitness_function(self, names_idx: List[int]):
        submatrix = self._choose(names_idx)
        singular_values = np.linalg.svd(np.cov(submatrix))[1]
        return scipy.stats.mstats.gmean(singular_values)


def random_chr(names: List[str], k: int):
    return random.sample(range(len(names)), k)


class CoordSystem(dict):

    def __init__(self, config: Config, *args, **kwargs):
        self.config = config
        super(CoordSystem, self).__init__(*args, **kwargs)

    @staticmethod
    @measure_time(enabled=True)
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
        with open(config.coordsys_path) as json_data:
            hash_list = json.load(json_data)
            samples = { hash: Sample.load(config, os.path.join(config.sample_dir, hash)) \
                        for hash in hash_list }
            coord_system = CoordSystem(config, samples)
            coord_system.config = config
            return coord_system

    @hide_field("config")
    def _save(self, config):    
        hash_list = [sample.name for sample in self.values()]
        with open(config.coordsys_path, 'w') as outfile:
            json.dump(hash_list, outfile)

    def save(self):
        self._save(self.config)

if __name__ == "__main__":
    raise RuntimeError()
