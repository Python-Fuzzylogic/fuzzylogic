"""Functions to evaluate, infer and defuzzify."""

from math import isinf

from .classes import Domain, Set


def round_partial(value, res):
    """
    Round any value to any arbitrary precision.

    >>> round_partial(0.405, 0.02)
    0.4
    >>> round_partial(0.412, 0.02)
    0.42
    >>> round_partial(1.38, 0.25)
    1.5
    >>> round_partial(1.12, 0.25)
    1.0
    >>> round_partial(9.24, 0.25)
    9.25
    >>> round_partial(7.76, 0.25)
    7.75
    >>> round_partial(987654321, 100)
    987654300
    >>> round_partial(3.14, 0)
    3.14
    """
    # backed up by wolframalpha
    if res == 0 or isinf(res):
        return value
    return round(value / res) * res


def rescale(out_min, out_max, *, in_min=0, in_max=1):
    """Scale from one domain to another.

    Tests only cover scaling from [0,1] (with default in_min, in_max!)
    to R.

    For arbitrary R -> R additional testing is required,
    but it should work in general out of the box.

    Originally used the algo from SO
    (OUT_max - OUT_min)*(x - IN_min) / (IN_max - IN_min) + OUT_min
    but there are too many edge cases thanks to over/underflows.
    Current factorized algo was proposed as equivalent by wolframalpha,
    which seems more stable.
    """
    assert in_min < in_max

    # for easier handling of the formula
    a = out_min
    b = out_max
    c = in_min
    d = in_max
    m = d - c
    n = a * d
    o = b * c

    def f(x):
        return (n - a * x - o + b * x) / m

    return f


def weighted_sum(*, weights: dict, target_d: Domain) -> float:
    """Used for weighted decision trees and such.

    Parametrize with dict of factorname -> weight and domain of results.
    Call with a dict of factorname -> [0, 1]

    There SHOULD be the same number of items (with the same names!)
    of weights and factors, but it doesn't have to be - however
    set(factors.names) <= set(weights.names) - in other words:
    there MUST be at least as many items in weights as factors.
    """
    assert sum(w for w in weights.values()) == 1

    rsc = rescale(target_d._low, target_d._high)

    def f(memberships):
        result = sum(r * weights[n] for n, r in memberships.items())
        return round_partial(rsc(result), target_d._res)

    return f
