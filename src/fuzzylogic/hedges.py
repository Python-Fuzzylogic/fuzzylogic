
"""
Lingual hedges modify curves of membership values.

These should work with Sets and functions.
"""

from .classes import Set

def very(g):
    """Sharpen memberships so that only the values close 1 stay at the top."""
    if isinstance(g, Set):
        def s_f(g):
            def f(x):
                return g(x) ** 2
            return f
        return Set(s_f(g.func))
    else:
        def f(x):
            return g(x) ** 2
        return f


def plus(g):
    """Sharpen memberships like 'very' but not as strongly."""
    if isinstance(g, Set):
        def s_f(g):
            def f(x):
                return g(x) ** 1.25
            return f
        return Set(s_f(g.func))
    else:
        def f(x):
            return g(x) ** 1.25
        return f
    

def minus(g):
    """Increase membership support so that more values hit the top."""
    if isinstance(g, Set):
        def s_f(g):
            def f(x):
                return g(x) ** 0.75
            return f 
        return Set(s_f(g.func))
    else:
        def f(x):
            return g(x) ** 0.75
        return f