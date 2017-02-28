
"""
------
HEDGES
------
Lingual hedges modify curves describing truthvalues.
These work with sets only. Meta-functionality is deprecated.
"""

from fuzzy.classes import Set
from warnings import warn

def very(g):
    def f(x):
        return g(x) ** 2

    def s_f(g):
        def f(x):
            return g(x) ** 2
        return f

    if isinstance(g, Set):
        return Set(g.domain, s_f(g.func))
    warn("deprecated", DeprecationWarning)
    return f


def plus(g):
    def f(x):
        return g(x) ** 1.25
    
    def s_f(g):
        def f(x):
            return g(x) ** 1.25
        return f
    
    if isinstance(g, Set):
        return Set(g.domain, s_f(g.func))
    warn("deprecated", DeprecationWarning)
    return f
    

def minus(g):
    def f(x):
        return g(x) ** 0.75
    
    def s_f(g):
        def f(x):
            return g(x) ** 0.75
        return f
    
    if isinstance(g, Set):
        return Set(g.domain, s_f(g.func))
    warn("deprecated", DeprecationWarning)
    return f