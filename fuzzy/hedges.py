"""
------
HEDGES
------
Lingual hedges modify curves describing truthvalues.
These are special since they work with functions AND sets.
"""

from fuzzy.classes import Set

def very(g):
    def f(x):
        return g(x) ** 2

    def s_f(g):
        def f(x):
            return g(x) ** 2
        return f

    if isinstance(g, Set):
        return Set(g.domain, s_f(g.func))
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
    return f
