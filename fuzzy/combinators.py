
"""
-----------
COMBINATORS
-----------
Linguistic terms (membership functions of two different FuzzySets) 
are combined with these functions to implement rules.

a and b are functions.
"""


def MIN(a, b):
    """Simple AND of two functions a and b."""
    def f(x):
        return min(a(x), b(x))
    return f


def MAX(a, b):
    """Simple OR of two functions a and x."""
    def f(x):
        return max(a(x), b(x))
    return f


def product(a, b):
    """AND variant."""
    def f(x):
        return a(x) * b(x)
    return f


def bounded_sum(a, b):
    """OR variant."""
    def f(x):
        a_x, b_x = a(x), b(x)
        return a_x + b_x - a_x * b_x
    return f


def lukasiewicz_OR(a, b):
    """OR variant."""
    def f(x):
        return max(0, a(x) + b(x) - 1)
    return f


def lukasiewicz_AND(a, b):
    """AND variant."""
    def f(x):
        return min(1, a(x) + b(x))
    return f


def einstein_sum(a, b):
    """OR variant."""
    def f(x):
        a_x, b_x = a(x), b(x)
        return (a_x + b_x) / (1 + a_x * b_x)
    return f


def einstein_product(a, b):
    """AND variant."""
    def f(x):
        a_x, b_x = a(x), b(x)
        return (a_x * b_x) / (2 - (a_x + b_x - a_x * b_x))
    return f


def hamacher_sum(a, b):
    """OR variant."""
    def f(x):
        a_x, b_x = a(x), b(x)
        return (a_x + b_x - 2 * a_x * b_x) / (1 - a_x * b_x)
    return f


def hamacher_product(a, b):
    """AND variant."""
    def f(x):
        a_x, b_x = a(x), b(x)
        return (a_x * b_x) / (a_x + b_x - a_x * b_x)


def lambda_op(a, b, l):
    """A 'compensatoric' operator, combining AND with OR by a weighing factor l.
    """
    def f(x):
        a_x, b_x = a(x), b(x)
        return l * (a_x * b_x) + (1 - l) * (a_x + b_x - a_x * b_x)
    return f


def gamma_op(a, b, g):
    """A 'compensatoric' operator, combining AND with OR by a weighing factor g.
    g (gamma-factor)
        0 < g < 1 (g == 0 -> AND; g == 1 -> OR)
    """
    if not(0 <= g <= 1):
        raise ValueError

    def f(x):
        a_x, b_x = a(x), b(x)
        return (a_x * b_x) ** (1 - g) * ((1 - a_x) * (1 - b_x)) ** g

    return f
