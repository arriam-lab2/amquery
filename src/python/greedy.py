import numpy as np
from iof import read_distance_matrix
from partial_corr import partial_corr
from itertools import combinations
import click


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


class DummyIndividual():
    def __init__(self, chromosome):
        self.chromosome = list(chromosome)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(self.chromosome)


class CsSearch:
    def __init__(self, dmatrix, names):
        self.dmatrix = dmatrix
        self.names = names

    def run(self, fitness, k):
        n = len(self.dmatrix)
        bases = list(DummyIndividual(x)
                     for x in combinations(np.arange(n), 3))
        f = [fitness(x) for x in bases]
        argmin = np.argmin(f)
        base = bases[argmin]

        for i in range(4, k + 1):
            outer = list(set(np.arange(n)) - set(base.chromosome))

            new_bases = [DummyIndividual(base.chromosome + [j])
                         for j in outer]
            f = [fitness(x) for x in new_bases]
            argmin = np.nanargmin(f)
            base = new_bases[argmin]
            print(i, "-th best solution: ", np.nanmin(f), " ", base, sep="")

        return base


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--distance_matrix', '-f', type=click.Path(exists=True),
              required=True)
@click.option('--cs_size', '-k', type=int, help='Coord system size',
              required=True)
def run(distance_matrix, cs_size):
    names, dmatrix = read_distance_matrix(distance_matrix)
    dmatrix = np.matrix(dmatrix)
    search = CsSearch(dmatrix, names)
    fitness = Fitness(dmatrix, names)
    search.run(fitness, cs_size)

if __name__ == "__main__":
    run()
