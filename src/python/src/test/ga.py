from ..lib.ga import *

print("ga test: ", end="")


def engine(_):
    return random.randint(0, 50)


def fitness(x):
    return abs(200 - sum(n ** 10 for n in x.chromosome) ** 0.5)


ancestors = [Individual(0.1, engine, 10) for _ in range(2)]
#
population = Population(ancestors, 50, fitness, mode="minimize")
for generation_legends in population.evolve(10, 25, 10):
    # print(*[fitness for fitness, indiv in generation_legends])
    pass

print("passed")

