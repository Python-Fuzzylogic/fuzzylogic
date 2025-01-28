from collections import defaultdict

import numpy as np

from .classes import Array
from .functions import R, S, constant, gauss, rectangular, sigmoid, singleton, step, trapezoid, triangular

functions = [step, rectangular]

argument1_functions = [singleton, constant]
argument2_functions = [R, S, gauss]
argument3_functions = [triangular, sigmoid]
argument4_functions = [trapezoid]


def generate_examples() -> dict[str, list[Array]]:
    examples: dict[str, list[Array]] = defaultdict(lambda: [])
    examples["constant"] = [np.ones(16)]
    for x in range(16):
        A = np.zeros(16)
        A[x] = 1
        examples["singleton"].append(A)

    for x in range(1, 16):
        func = R(0, x)
        examples["R"].append(func(np.linspace(0, 1, 16)))  # type: ignore
    return examples
