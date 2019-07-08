
"""
Functions that transform a given membership value to a truth value.

How this can be useful? Beats me. Found it somewhere on the internet, 
never needed it.
"""
from math import sqrt


def true(m):
    """The membership-value is its own truth-value."""
    return m

def false(m):
    """The opposite of TRUE."""
    return 1 - m

def fairly_false(m):
    """Part of a circle in quadrant I."""
    return sqrt(1 - m ** 2)

def fairly_true(m):
    """Part of a circle in quadrant II."""
    return sqrt(1 - (1 - m) ** 2)

def very_false(m):
    """Part of a circle in quadrant III."""
    return -sqrt(1 - (1 - m) ** 2)

def very_true(m):
    """Part of a circle in quadrant IV."""
    return -sqrt(1 - m ** 2)