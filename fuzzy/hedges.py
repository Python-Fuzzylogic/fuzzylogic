
"""
------
HEDGES
------
Lingual hedges modify curves describing truthvalues.
These work with sets only. It's more trouble than it is worth making
these work with pure functions, so meta-functionality was removed.
"""

from fuzzy.classes import Set

def very(g):
    def s_f(g):
        def f(x):
            return g(x) ** 2
        return f
    return Set(s_f(g.func))


def plus(g):
    def s_f(g):
        def f(x):
            return g(x) ** 1.25
        return f
    return Set(s_f(g.func))
    

def minus(g):
    def s_f(g):
        def f(x):
            return g(x) ** 0.75
        return f 
    return Set(s_f(g.func))