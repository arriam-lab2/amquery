from lib.ga import *

print("ga test: ", end="")


def engine(_):
    return random.randint(0, 50)


def fitness(x):
    return abs(200 - sum(x.chromosome))


pop_size = 500
ancestors = [Individual(0.1, engine, 50) for _ in range(pop_size)]
population = Population(ancestors, pop_size, fitness, mode="minimize")
for generation_legends in population.evolve(100, 100, 50):
    # print(*[fitness for fitness, indiv in generation_legends])
    pass

print("passed")
