#!/usr/bin/env python3

import itertools
import random
import click
import numpy as np
from typing import Sequence, Callable, Any, Tuple, List

from genetic.individuals import BaseIndividual
from genetic.populations import PanmicticPopulation
from genetic.selection import bimodal

from lib.pwcomp import PwMatrix
from lib.config import Config


class Engine:
    def __init__(self, names):
        self.names = np.array(list(names))

    def __call__(self, val=None, chromosome=None):
        elem = random.choice(self.names)
        idx = np.where(self.names == elem)[0][0]

        result = val if chromosome and idx in chromosome else idx
        print(result)
        return result


class CoordSystemIndividual(BaseIndividual):
    def __init__(self, engine: Engine, mutrate: float, l=None,
                 starting=None):

        self._engine = (engine if isinstance(engine, Sequence) else
                        [engine] * l)

        self._l = l if l else len(engine)

        if starting and (not isinstance(starting, Sequence) or
                         self._l != len(starting)):
            raise ValueError("`starting` length doesn't match the number "
                             "of features specified by `l` (or inferred from "
                             "`len(engine)`)")

        # chromosome is a sequence of genes (features)
        self._genome = (tuple(starting) if starting else
                        tuple(gen(None) for gen in self._engine))

        self._mutrate = mutrate


    def __eq__(self, other):
        return self.genome == other.genome

    def __ne__(self, other):
        return not self == other

    @property
    def engine(self) -> Sequence[Callable]:
        return self._engine

    @property
    def genome(self) -> Tuple[Any]:
        return self._genome

    @property
    def mutrate(self) -> float:
        return self._mutrate

    def replicate(self) -> List[Any]:
        mutation_mask = np.random.binomial(1, self.mutrate, len(self.genome))
        return [gen(val) if mutate else val for (val, mutate, gen) in
                list(zip(self.genome, mutation_mask, self.engine))]

    def mate(self, other, *args, **kwargs):
        offspring_genome = _crossover(self.replicate(), other.replicate())

        return type(self)(engine=self._engine, mutrate=self.mutrate,
                          l=self._l, starting=offspring_genome)


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

    def __init__(self, dmatrix, names):
        self.dmatrix = dmatrix
        self.names = names

    def __call__(self, indiv):
        return self._total_partcorr(indiv.genome)

    def _choose(self, names_idx):
        outer_idx = list(set(np.arange(len(self.names))) - set(names_idx))
        dmx = np.delete(self.dmatrix, outer_idx, axis=1)
        dmx = np.delete(dmx, names_idx, axis=0)
        return dmx

    def _total_partcorr(self, names_idx):
        dmx = self._choose(names_idx)
        corrs = np.corrcoef(dmx)
        sums = np.apply_along_axis(sum, 1, corrs)
        total_pc = np.apply_along_axis(sum, 0, sums)
        return float(total_pc)


def random_chr(names, k):
    return random.sample(range(len(names)), k)


class CoordSystem(list):
    @staticmethod
    def load(config: Config):
        raise NotImplementedError()

    @staticmethod
    def calculate(config: Config):
        coord_system_size = config.genetic.coord_system_size
        generations = config.genetic.generations
        mutation_rate = config.genetic.mutation_rate
        population_size = config.genetic.population_size
        select_rate = config.genetic.select_rate
        random_select_rate = config.genetic.random_select_rate
        legend_size = config.genetic.legend_size

        pwmatrix = PwMatrix.load(config)

        engine = Engine(pwmatrix.labels)
        fitness = Fitness(pwmatrix.matrix, pwmatrix.labels)
        ancestors = [CoordSystemIndividual(engine, mutation_rate,
                                           coord_system_size,
                                           random_chr(pwmatrix.labels,
                                                      coord_system_size))
                     ] * 2


        selection = bimodal(fittest_fraction=select_rate,
                            other_random_survival=random_select_rate)

        population = PanmicticPopulation(ancestors, population_size, fitness,
                                         selection, legend_size)

        legends = list(population.evolve(generations))

        eps = 1e-20
        last = None
        locality_count = 0
        n = 1
        for legend in legends:
            best = legend[np.argmin([fitness for fitness, indiv in legend])]

            if not config.quiet:
                print("\rRound", n, "of", generations,
                      "best solution:", best[0], end="")
            n += 1

            if last and abs(best[0] - last) < eps:
                locality_count += 1

            if locality_count > idle_threshold:
                break

            last = best[0]

        #print()
        #print(best[1].genome)

        self = [pwmatrix.labels[i] for i in best[1].genome]


    @staticmethod
    def load(config: Config):
        pass

    def save(self):
        with open(self.__filename, "w") as f:
            f.write('\n'.join(x for x in self))


if __name__ == "__main__":
    raise RuntimeError()
