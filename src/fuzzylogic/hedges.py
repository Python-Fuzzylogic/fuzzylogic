
"""
Lingual hedges modify curves of membership values.

These work with sets only. It's more trouble than it is worth making
these work with pure functions, so meta-functionality was removed.
"""

from .classes import Set

def very(g):
    """Sharpen memberships so that only the values close 1 stay at the top."""
    def s_f(g):
        def f(x):
            return g(x) ** 2
        return f
    return Set(s_f(g.func))


def plus(g):
    """Sharpen memberships like 'very' but not as strongly."""
    def s_f(g):
        def f(x):
            return g(x) ** 1.25
        return f
    return Set(s_f(g.func))
    

def minus(g):
    """Increase membership support so that more values hit the top."""
    def s_f(g):
        def f(x):
            return g(x) ** 0.75
        return f 
    return Set(s_f(g.func))