#! /usr/bin/env python

from collections import Sequence
import itertools
import random
import time
import numpy as np
import abc


class abstractstatic(staticmethod):
    __slots__ = ()

    def __init__(self, function):
        super(abstractstatic, self).__init__(function)
        function.__isabstractmethod__ = True
    __isabstractmethod__ = True


class Individual(object):
    __metaclass__ = abc.ABCMeta

    def __hash__(self):
        return hash(self._chromosome)

    def __lt__(self, other):
        return tuple(self.chromosome) < tuple(other.chromosome)

    def __eq__(self, other):
        """
        :type other: Individual
        :rtype: bool
        """
        if not isinstance(other, Individual):
            raise TypeError
        return self.chromosome == other.chromosome

    def __ne__(self, other):
        """
        :type other: Individual
        :rtype: bool
        """
        return not self == other

    @property
    def engine(self):
        return self._engine

    @property
    def chromosome(self):
        return self._chromosome

    @abstractstatic
    def _mutate(mutation_rate, chromosome, engine):
        """
        :type mutation_rate: float
        :param mutation_rate: the probability of mutation per gene
        :type chromosome: Sequence
        :param chromosome: a sequence of genes (features)
        :rtype: list
        :return: a mutated chromosome
        """

    @abstractstatic
    def _crossover(chr1, chr2):
        """
        :param chr1: a chromosome type object
        :param chr2: a chromosome type object
        :rtype: list
        :return: the result of crossover between chr1 and chr2
        """

    def replicate_chr(self):
        return self._mutate(self._mutation_rate,
                            self._chromosome, self._engine)

    @abc.abstractmethod
    def mate(self, other):
        """
        :return: the result of mating with other Individual object
        of the same type
        """


class IndividualImpl(Individual):
    """
    :type _l: int
    :type _engine: Sequence[Callable]
    :type _mutation_rate: float
    :type _chromosome: tuple
    """

    def __init__(self, mutation_rate, engine, l=None, starting_chr=None):
        # TODO add docs about starting_chromosome
        """
        :type mutation_rate: float
        :param mutation_rate: the binomial mutation success rate for each gene
        :type engine: Union[Sequence[Callable[Optional]], Callable[Optional]]
        :param engine: an engine is used to mutate individual's features.
                       It can be:
                       - A single callable object that takes one argument
                         (current value of a feature) and returns an new value.
                         It must handle `None` inputs if `starting_chromosome`
                         is `None`
                       - A sequence of such callable object, one per each
                         feature
                       Note: when `starting_chr` is `None` the first time
                       `engine` is used its callables get `None` as input,
                       which means they should return some starting value; this
                       detail may not be important for your implementation, (e.g.
                       if you don't have any special rules for starting values
                       and mutated values), but make sure the your callables
                       handle `None` inputs if you don't `starting_chr`
        :type l: Optional[int]
        :param l: the number of features, defaults to `None`. Can't be == 0.
                  - If `l` is set to `None`, it's true value is inferred from
                    `len(engine)`, hence a `ValueError` will be raised if
                    `engine` is not a sequence;
                  - If `l` is not `None` and `engine` is a sequence such that
                    `len(engines) != l`, a `ValueError` will be raised.
        :type starting_chr: Sequence
        :param starting_chr:
        """
        if l and isinstance(engine, Sequence) and len(engine) != l:
            raise ValueError("len(engine) != l, while l is not None")
        elif l is None and not isinstance(engine, Sequence):
            raise ValueError("`l` is not specified, while `engine` is not a "
                             "sequence, hence `l` cannot be be inferred")

        self._l = l if l else len(engine)
        self._engine = (engine if isinstance(engine, Sequence) else
                        [engine] * self._l)
        self._mutation_rate = mutation_rate

        if starting_chr and self._l != len(starting_chr):
            raise ValueError(
                "`starting_chr`'s length doesn't match the number "
                "of features specified by `l` (or inferred from "
                "`len(engine)`)")
        # chromosome is a sequence of genes (features)
        self._chromosome = (tuple(starting_chr) if starting_chr else
                            tuple(gen(None) for gen in self._engine))

    @staticmethod
    def _mutate(mutation_rate, chromosome, engine):
        """
        :type mutation_rate: float
        :param mutation_rate: the probability of mutation per gene
        :type chromosome: Sequence
        :param chromosome: a sequence of genes (features)
        :rtype: list
        :return: a mutated chromosome
        """
        mutation_mask = np.random.binomial(1, mutation_rate, len(chromosome))
        return [generator(val) if mutate else val for val, mutate, generator in
                list(zip(chromosome, mutation_mask, engine))]

    @staticmethod
    def _crossover(chr1, chr2):
        """
        :rtype: list
        """
        if len(chr1) != len(chr2):
            raise ValueError("Incompatible species can't mate")
        choice_mask = np.random.binomial(1, 0.5, len(chr1))
        return [gene1 if choice else gene2 for gene1, gene2, choice in
                list(zip(chr1, chr2, choice_mask))]

    def mate(self, other):
        offspring_chr = self._crossover(self.replicate_chr(),
                                        other.replicate_chr())

        return IndividualImpl(mutation_rate=self._mutation_rate,
                              engine=self._engine, l=self._l,
                              starting_chr=offspring_chr)


class Population(object):
    """
    :type _evaluated_ancestors: list[(object, Individual)]
    :type _legends: list[(object, Individual)]
    """
    modes = ("maximize", "minimize")

    def __init__(self, ancestors, size, fitness_function, mode="maximize",
                 n_legends=10):
        """
        :type ancestors: Sequence[Individual]
        :param ancestors: a bunch of individuals to begin with
        :type size: int
        :param size: population size
        :type fitness_function: (Individual) -> object
        :param fitness_function: a callable that requires one argument - an
                                 instance of Individual - and returns an
                                 instance of a class that supports comparison
                                 operators, i.e. can be used to evaluate and
                                 compare fitness of different Individuals.
        :type n_legends: int
        :param n_legends: the number of the best individuals to remember
        :return:
        """
        if mode not in Population.modes:
            raise ValueError('`mode` must be `"maximize"` or `"minimize"`')

        if not isinstance(ancestors, Sequence) or not ancestors:
            raise ValueError("`ancestors` must be a nonempty sequence")

        if len(ancestors) < 2:
            raise ValueError("At least 2 ancestors are required to start a"
                             "population")

        if not all(isinstance(indiv, Individual) for indiv in ancestors):
            raise ValueError("`ancestors` can only contain instances of"
                             "`Individual`")
        if not isinstance(n_legends, int):
            raise ValueError("`n_legends` must be a non-negative integer")

        self._maximize = mode == "maximize"
        self._ancestors = list(ancestors)
        self._size = size
        self._n_legends = n_legends
        self._legends = []

        try:
            if fitness_function(ancestors[0]) is None:
                raise ValueError(
                    "`fitness_function` mustn't return `NoneType` "
                    "values")
        except (TypeError, AttributeError):
            raise ValueError("`fitness_function` must be a callable object,"
                             "that a single argument of type `Individual`")
        self._fitness_func = fitness_function
        self._evaluated_ancestors = list(zip(map(self._fitness_func, ancestors),
                                        ancestors))

    @property
    def legends(self):
        """
        :rtype: list[(object, Individual)]
        """
        return self._legends

    def _repopulate(self, evaluated_ancestors):
        """
        Mate ancestors to restore population size
        :type evaluated_ancestors: list[(object, Individual)]
        :rtype: list[(object, Individual)]
        """
        # generate all possible pairs of individuals and mate enough random
        # pairs to reach the desired population size
        individuals = [indiv for fitness, indiv in evaluated_ancestors]
        all_pairs = tuple(itertools.combinations(individuals, r=2))
        mating_pairs = (random.choice(all_pairs)
                        for _ in range(self._size - len(evaluated_ancestors)))
        offsprings = [indiv1.mate(indiv2) for indiv1, indiv2 in mating_pairs]
        # evaluate offsprings and merge the result with `evaluated_ancestors`
        offspring_fitness = map(self._fitness_func, offsprings)
        return list(zip(offspring_fitness, offsprings)) + evaluated_ancestors

    def _select(self, evaluated_population, n_fittest, n_random_unfit):
        """
        :type evaluated_population: list[(object, Individual)]
        :param evaluated_population:
        :type n_fittest: int
        :param n_fittest:
        :type n_random_unfit: int
        :param n_random_unfit:
        :rtype: list[object, Individual)]
        """
        # pick the most fittest and random lesser fit individuals
        ranked_pop = sorted(evaluated_population, reverse=self._maximize)
        fittest_survivors = ranked_pop[:n_fittest]
        random_unfit_survivors = random.sample(ranked_pop[n_fittest:],
                                               n_random_unfit)
        return fittest_survivors + random_unfit_survivors

    @staticmethod
    def _filter_duplicates_by_id(objects):
        """
        Filter duplicated references from a sequence. Utilises object ids.
        :type objects: Sequence[object]
        :rtype: list[object]
        """
        return {id(obj): obj for obj in objects}.values()

    def _update_legends(self, contenders):
        """
        :type contenders: list[(object, Individual)]
        :rtype: None
        """
        # merge `contenders` with `self._legends`, sort again and strip to
        # `self._n_legends`
        # note: since `contenders` can contain some evaluated individuals from
        #       `legends` (if they managed to survive through the generations)
        #       we need to remove obvious duplicates by checking object ids
        self._legends = sorted(
            self._filter_duplicates_by_id(contenders + self._legends),
            reverse=self._maximize)[:self._n_legends]

    def _run_generation(self, evaluated_ancestors, n_fittest, n_unfit):
        """
        Repopulate the population, apply selection, update the list of legends
        and return the survivors
        :type evaluated_ancestors: list[(object, Individual)]
        :param n_fittest:
        :param n_unfit:
        :rtype: list[(object, Individual)]
        """
        # repopulate, apply selection and update the hall of fame (legends)
        population = self._repopulate(evaluated_ancestors)
        selected_individuals = self._select(population, n_fittest, n_unfit)
        # note: since the list returned by `self._select` starts with the
        # fittest individuals we can pick contenders for the hall of fame
        # by slicing the first `self._n_legends` of `selected_individuals`
        self._update_legends(selected_individuals[:self._n_legends])
        return selected_individuals

    def _run_generation_parallel(self, evaluated_ancestors, n_fittest, n_unfit,
                                 n_jobs):
        # TODO
        # import pathos.multiprocessing as mp
        raise NotImplemented

    def evolve(self, n_gen, n_fittest, n_random_unfit):
        """
        :type n_gen: int
        :param n_gen: the number of generations
        :type n_fittest: int
        :param n_fittest: the number of the most fittest individuals to pick
                          for the next generation
        :type n_random_unfit: int
        :param n_random_unfit: the number of lesser fit individuals to pick at
                               random
        """
        if n_fittest < 0 or not isinstance(n_fittest, int):
            raise ValueError("`n_fittest` must be a nonzero integer")

        if n_random_unfit < 0 or not isinstance(n_random_unfit, int):
            raise ValueError("`n_unfit` must be a nonzero integer")

        if n_fittest + n_random_unfit > self._size:
            raise ValueError("Population size is too small to fit "
                             "`n_fittest` + `n_unfit`")
        current_generation = self._evaluated_ancestors
        for _ in range(n_gen):
            current_generation = self._run_generation(current_generation,
                                                      n_fittest,
                                                      n_random_unfit)
            yield self._legends


def test():
    engine = lambda x: random.randint(0, 50)
    ancestors = [IndividualImpl(0.1, engine, 75) for _ in range(2)]

    fitness_func = lambda indiv: abs(200 - sum(indiv.chromosome))
    population = Population(ancestors, 100, fitness_func, mode="minimize")
    start = time.time()
    for generation_legends in population.evolve(1000, 25, 10):
        print(*[fitness for fitness, indiv in generation_legends])
    print(time.time() - start)


if __name__ == "__main__":
    test()
