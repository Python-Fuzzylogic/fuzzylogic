
from math import isinf
from fuzzy.classes import Domain, Set

def round_partial(value, res):
    """
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

def scale(OUT_min, OUT_max, *, IN_min=0, IN_max=1):
    """Scale from one domain to another.
    
    Works best for [0,1] -> R. 
    
    For R -> R additional testing is required, 
    but it should work in general out of the box.
    
    Originally used the naive algo from SO
    (OUT_max - OUT_min)*(x - IN_min) / (IN_max - IN_min) + OUT_min
    but there are too many edge cases thanks to over/underflows.
    Current factorized algo was proposed as equivalent by wolframalpha, 
    which seems more stable.
    """
    assert IN_min < IN_max
        
    def f(x):
        if x == IN_min:
            return OUT_min
        elif x == IN_max:
            return OUT_max
        return (OUT_min * IN_min - OUT_min * x - 
         2 * OUT_max *  IN_min + OUT_max * IN_max + IN_max * x) / (
            IN_max - IN_min)
        
    return f


def weighted_sum(*, weights:dict, target:Domain) -> float:
    """Ordinarily used for weighted decision trees and such.
    Parametrize with dict of factorname -> weight and domain of results.
    Call with a dict of factorname -> [0, 1]
    
    There SHOULD be the same number of items (with the same names!)
    of weights and factors, but it doesn't have to be - however
    set(factors.names) <= set(weights.names) - in other words:
    there MUST be at least as many items in weights as factors.
    """
    assert sum(w for w in weights.values()) == 1
    S = scale(target.low, target.high)
    
    def f(factors):
        RES = sum(r * weights[n] for n, r in factors.items())
        return S(round_partial(RES, target.res))
    return f