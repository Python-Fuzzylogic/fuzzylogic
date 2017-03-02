
"""
-----------
COMBINATORS
-----------
Linguistic terms (membership functions of two different FuzzySets of the same domain) 
are combined.

a and b are functions.

Since these combinators are used directly in the Set class to implement logic operations, 
the most obvious use of this module is when subclassing Set to make use of specific combinators
for special circumstances.
"""


def MIN(a, b):
    """Classic AND variant."""
    def f(x):
        return min(a(x), b(x))
    return f


def MAX(a, b):
    """Classic OR variant."""
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

def lukasiewicz_AND(a, b):
    """AND variant."""
    def f(x):
        return min(1, a(x) + b(x))
    return f

def lukasiewicz_OR(a, b):
    """OR variant."""
    def f(x):
        return max(0, a(x) + b(x) - 1)
    return f

def einstein_product(a, b):
    """AND variant."""
    def f(x):
        a_x, b_x = a(x), b(x)
        return (a_x * b_x) / (2 - (a_x + b_x - a_x * b_x))
    return f

def einstein_sum(a, b):
    """OR variant."""
    def f(x):
        a_x, b_x = a(x), b(x)
        return (a_x + b_x) / (1 + a_x * b_x)
    return f

def hamacher_product(a, b):
    """AND variant.
    (xy) / (x + y - xy) for x, y != 0
    0 otherwise
    """
    def f(z):
        x, y = a(z), b(z)
        return (x * y) / (x + y - x * y) if x != 0 and y != 0 else 0
    return f

def hamacher_sum(a, b):
    """OR variant.
    (x + y - 2xy) / (1 - xy) for x,y != 1
    1 otherwise
    """
    def f(z):
        x, y = a(z), b(z)
        return (x + y - 2 * x * y) / (1 - x * y) if x != 1 or y != 1 else 1
    return f


def lambda_op(l):
    """A 'compensatoric' operator, combining AND with OR by a weighing factor l.
    
    This complicates matters a little, since all combinators promise to just take 
    2 functions as arguments, so we parametrize this with l.
    """
    assert (0 <= l <= 1)
        
    def e(a, b):
        def f(x):
            a_x, b_x = a(x), b(x)
            return l * (a_x * b_x) + (1 - l) * (a_x + b_x - a_x * b_x)
        return f
    return e


def gamma_op(g):
    """A 'compensatoric' operator, combining AND with OR by a weighing factor g.
    g (gamma-factor)
        0 < g < 1 (g == 0 -> AND; g == 1 -> OR)
        
    Same problem as with lambda_op, since all combinators promise to just take 
    2 functions as arguments, so we parametrize this with g.
    """
    assert (0 <= g <= 1)
    
    def e(a, b):
        def f(z):
            x, y = a(z), b(z)
            return (x * y) ** (1 - g) * ((1 - x) * (1 - y)) ** g
        return f
    return e