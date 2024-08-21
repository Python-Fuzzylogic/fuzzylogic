"""Guesstimate the membership functions and their parameters of a fuzzy logic system.

How this works:
1. We normalize the target array to a very small size, in the range [0, 1].
2. We guess which functions match well based on the normalized array,
    only caring about the shape of the function, not the actual values.
3. We take the best matching functions and start guessing the parameters applying evolutionary algorithms.
4. Using the best matching functions with their parameters, we get some preliminary results.
5. We use the preliminary results to construct an array of the same size as the input array,
    but with the membership function applied. The difference of the two arrays is the new target.
6. Start the process again with the new target. Repeat until there is no difference between the two arrays.
7. The final result is the combination of those functions with their parameters.
"""

import contextlib
import inspect
import sys
from itertools import permutations
from random import choice, randint
from statistics import median
from typing import Callable

import numpy as np

from .functions import R, S, constant, gauss, rectangular, sigmoid, singleton, step, trapezoid, triangular

np.seterr(all="raise")
functions = [step, rectangular]

argument1_functions = [singleton, constant]
argument2_functions = [R, S, gauss]
argument3_functions = [triangular, sigmoid]
argument4_functions = [trapezoid]


def normalize(target: np.ndarray, output_length: int = 16) -> np.ndarray:
    """Normalize and interpolate a numpy array.

    Return an array of output_length and normalized values.
    """
    min_val = np.min(target)
    max_val = np.max(target)
    if min_val == max_val:
        return np.ones(output_length)
    normalized_array = (target - min_val) / (max_val - min_val)
    normalized_array = np.interp(
        np.linspace(0, 1, output_length), np.linspace(0, 1, len(normalized_array)), normalized_array
    )
    return normalized_array


def guess_function(target: np.ndarray) -> Callable:
    normalized = normalize(target)
    # trivial case
    return constant if np.all(normalized == 1) else singleton


def fitness(func: Callable, target: np.ndarray, certainty: int | None = None) -> float:
    """Compute the difference between the array and the function evaluated at the parameters.

    if the error is 0, we have a perfect match: fitness -> 1
    if the error approaches infinity, we have a bad match: fitness -> 0
    """
    test = np.fromiter([func(x) for x in np.arange(*target.shape)], float)
    result = 1 / (np.sum(np.abs((test - target))) + 1)
    return result if certainty is None else round(result, certainty)


def seed_population(func: Callable, target: np.ndarray) -> dict[tuple, float]:
    # create a random population of parameters
    params = [p for p in inspect.signature(func).parameters.values() if p.kind == p.POSITIONAL_OR_KEYWORD]
    seed_population = {}
    seed_numbers = [
        sys.float_info.min,
        sys.float_info.max,
        0,
        1,
        -1,
        0.5,
        -0.5,
        min(target),
        max(target),
        np.argmax(target),
    ]
    # seed population
    for combination in permutations(seed_numbers, len(params)):
        with contextlib.suppress(Exception):
            seed_population[combination] = fitness(func(*combination), target)
    assert seed_population, "Failed to seed population - wtf?"
    return seed_population


def reproduce(parent1: tuple, parent2: tuple) -> tuple:
    child = []
    for p1, p2 in zip(parent1, parent2):
        # mix the parts of the floats by randomness within the range of the parents
        # adding a random jitter should avoid issues when p1 == p2
        a1, a2 = np.frexp(p1)
        b1, b2 = np.frexp(p2)
        a1 += randint(-1, 1)
        a2 += randint(-1, 1)
        b1 += randint(-1, 1)
        b2 += randint(-1, 1)
        child.append(((a1 + b1) / 2) * 2 ** np.random.uniform(a2, b2))
    return tuple(child)


def guess_parameters(
    func: Callable, target: np.ndarray, precision: int | None = None, certainty: int | None = None
) -> tuple:
    """Find the best fitting parameters for a function, targetting an array.

    Args:
        func (Callable): A possibly matching membership function, such as `fuzzylogic.functions.triangular`.
        array (np.ndarray): The target array to fit the function to.

    Returns:
        tuple: The best fitting parameters for the function.
    """

    def best() -> tuple:
        return sorted(population.items(), key=lambda x: x[1])[0][0]

    seed_pop = seed_population(func, target)
    population = seed_pop.copy()
    print(seed_pop)
    # iterate until convergence or max iterations
    pressure = 0
    pop_size = 100
    last_pop = {}
    for generation in range(12):
        # sort the population by fitness
        pop: list[tuple[tuple, float]] = sorted(population.items(), key=lambda x: x[1], reverse=True)[
            :pop_size
        ]
        if not pop:
            population = last_pop
            return best()
        print(f"Best so far:: {func.__name__}(*{pop[0][0]}) with {pop[0][1]:.10f}")
        # maybe the seed population already has a perfect match?
        if pop[0][1] == 1:
            print("Lucky!")
            return best()
        # the next generation
        new_population = {}
        killed = 0
        for parent1 in pop:
            while True:
                with contextlib.suppress(Exception):
                    # select another parent and try to reproduce - try until it works once
                    # at least one viable child is guaranteed (parent1 == parent2)
                    parent2 = choice(pop)
                    child = reproduce(parent1[0], parent2[0])
                    new_population[child] = (fit := fitness(func(*child), target))
                    # check for convergence
                    if fit == 1:
                        print("Lucky!")
                        return child
                    # kill the worst
                    if fit <= pressure:
                        del new_population[child]
                        killed += 1
                        if killed % 1000 == 0:
                            print("xxx")
                        if killed > 10000:
                            break
                    else:
                        if len(new_population) % 1000 == 0:
                            print("...")
                        break
        print(
            f"Generation {generation}: {killed} killed; pop size {len(population)}; pressure {pressure:.10f}"
        )
        if last_pop == new_population:
            break
        last_pop = population
        population = new_population
        # Under Pressure!
        if len(population) == 1:
            print("Only a single survivor!")
            break
        if killed > 1000:
            pop_size += 1000
            pressure **= 0.999
            population |= seed_pop
        else:
            pressure = median([x[1] for x in population.items()])
    return best()


def shave(target: np.ndarray, components: dict[Callable, tuple]) -> np.ndarray:
    """Remove the membership functions from the target array."""
    result = np.zeros_like(target)
    for func, params in components.items():
        f = func(*params)
        result += np.fromiter([f(x) for x in np.arange(*target.shape)], float)
    return target - result
