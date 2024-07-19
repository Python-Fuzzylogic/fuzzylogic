
"""
Defuzzyfication is the process of mapping a set in the unit interval gained from
fuzzyfication and inference back to a value with a physical unit.

There are multiple ways of achieving this with more or less precision, ambiguities and
required processing power.

All of these functions take a 2-dimensional argument of the form [arange(x), y_values]
with y_values in the unit interval.
to allow easy plotting and use of numpy functions.
All functions return a single unit interval that can be directly mapped to a control value.
"""

import numpy as np


def maximum(fuzzyset):
    """Calculates the (generalized) maximum of a fuzzyset.

    This is needed for defuzzification.

    First we determine a suitable step within the range, then we go from
    left to right until we hit a maximum. Then we go from right to left,
    until we find a maximum. As we can be sure that the function is
    triangular, the maximum must be at the same height, however,
    we might need to calculate the average of an eventual "saddle".
    """
    L = fuzzyset.lower
    U = fuzzyset.upper
    func = fuzzyset.func
    step = (U - L) / 100.

    values = [func(x) for x in np.nrange(L, U, step)]
    m = max(values)
    # We get the lower maximum
    lower_max_i = values.index(m)
    lower_max = L + lower_max_i*step

    # We get the upper maximum
    values.reverse()
    upper_max_i = values.index(m)
    upper_max = U - upper_max_i * i

    return (upper_max - lower_max) / 2.

def center_of_gravity(fuzzyset):
    pass
