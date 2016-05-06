#!/usr/bin/env python3

import click
from iof import read_distance_matrix
import numpy as np
import random
from partial_corr import partial_corr
import genetic_algorithm as ga
from collections import Sequence


class CoordSystem(ga.Individual):
    """
    :type _l: int
    :type _engine: Sequence[Callable]
    :type _mutation_rate: float
    :type _chromosome: tuple
    """

    def __init__(self, mutation_rate, engine, l=None,
                 starting_chr=None):
        if l and isinstance(engine, Sequence) and len(engine) != l:
            raise ValueError("len(engine) != l, while l is not None")
        elif l is None and not isinstance(engine, Sequence):
            raise ValueError("`l` is not specified, while `engine` is not a "
                             "sequence, hence `l` cannot be be inferred")

        self._l = l if l else len(engine)
        self._engine = (engine if isinstance(engine, Sequence) else
                        [engine] * self._l)
        self._mutation_rate = mutation_rate

        if (starting_chr is not None) and (self._l != len(starting_chr)):
            raise ValueError(
                "`starting_chr`'s length doesn't match the number "
                "of features specified by `l` (or inferred from "
                "`len(engine)`)")
        # chromosome is a sequence of genes (features)
        self._chromosome = starting_chr if starting_chr is not None \
            else np.array([gen(None) for gen in self._engine])

    @staticmethod
    def _mutate(mutation_rate, chromosome, engine):
        """
        :ty pe mutation_rate: float
        :param mutation_rate: the probability of mutation per gene
        :type chromosome: Sequence
        :param chromosome: a sequence of genes (features)
        :rtype: list
        :return: a mutated chromosome
        """
        mutation_mask = np.random.binomial(1, mutation_rate, len(chromosome))
        return [generator(val, chromosome) if mutate else val for val, mutate, generator in
                zip(chromosome, mutation_mask, engine)]

    @staticmethod
    def _crossover(chr1, chr2):
        """
        :rtype: list
        """
        if len(chr1) != len(chr2):
            raise ValueError("Incompatible species can't mate")
        joined = np.union1d(chr1, chr2)
        return tuple(joined[random.sample(range(len(joined)), len(chr1))])

    def mate(self, other):
        offspring_chr = self._crossover(self.replicate_chr(),
                                        other.replicate_chr())
        return CoordSystem(mutation_rate=self._mutation_rate,
                           engine=self._engine, l=self._l,
                           starting_chr=offspring_chr)


class Engine:

    def __init__(self, names):
        self.names = np.array(names)

    def __call__(self, val=None, chromosome=None):
        pool = self.names
        elem = random.choice(pool)
        idx = np.where(self.names == elem)[0][0]
        return val if chromosome and idx in chromosome else idx


class Fitness:

    def __init__(self, dmatrix, names):
        self.dmatrix = dmatrix
        self.names = names

    def __call__(self, indiv):
        return self._total_partcorr(indiv.chromosome)

    def _choose(self, names_idx):
        outer_idx = list(set(np.arange(len(self.names))) - set(names_idx))
        dmx = np.delete(self.dmatrix, outer_idx, axis=1)
        dmx = np.delete(dmx, names_idx, axis=0)
        return dmx

    def _total_partcorr(self, names_idx):
        dmx = self._choose(names_idx)
        corrs = partial_corr(dmx)
        sums = np.apply_along_axis(sum, 1, corrs)
        total_pc = np.apply_along_axis(sum, 0, sums)
        return float(total_pc)


def random_chr(names, k):
    return random.sample(range(len(names)), k)


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--distance_matrix', '-f', type=click.Path(exists=True),
              required=True)
@click.option('--cs_size', '-k', type=int, help='Coord system size',
              required=True)
@click.option('--generations', '-n', type=int, help='Number of generations',
              default=1000)
@click.option('--mutation_rate', '-m', type=float, help='Mutation rate',
              default=0.1)
@click.option('--population_size', '-p', type=int, help='Population size',
              default=100)
@click.option('--select_size', '-s', type=int,
              help='Number of best individuals to select on each generation',
              default=25)
@click.option('--random_select_size', '-r', type=int,
              help='Number of random individuals to select on each generation',
              default=10)
def run(distance_matrix, cs_size, generations, mutation_rate, population_size,
        select_size, random_select_size):
    names, dmatrix = read_distance_matrix(distance_matrix)
    dmatrix = np.matrix(dmatrix)

    engine = Engine(names)
    fitness = Fitness(dmatrix, names)
    ancestors = [CoordSystem(mutation_rate, engine, cs_size,
                             random_chr(names, cs_size)) for _ in range(2)]

    population = ga.Population(ancestors, population_size, fitness,
                               mode="minimize")

    legends = population.evolve(generations,
                                select_size,
                                random_select_size)
    for legend in legends:
        print(*[fitness for fitness, indiv in legend])


if __name__ == "__main__":
    run()
