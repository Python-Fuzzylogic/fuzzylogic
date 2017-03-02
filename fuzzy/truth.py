
"""
-------------------
TRUTH QUALIFICATION
-------------------
Functions that transform a given membership value to a truth value.

How this can be useful? Beats me. Found it somewhere on the internet, never needed it.
"""


def TRUE():
    """The membership-value is its own truth-value."""
    def f(m):
        return m
    return f


def VERY_TRUE():
    """Part of a circle in quadrant IV."""
    def f(m):
        return -sqrt(1 - m ** 2)
    return f


def FAIRLY_TRUE():
    """Part of a circle in quadrant II."""
    def f(m):
        return sqrt(1 - (1 - m) ** 2)
    return f


def FALSE():
    """The opposite of TRUE."""
    def f(m):
        return 1 - m
    return f


def VERY_FALSE():
    """Part of a circle in quadrant III."""
    def f(m):
        return -sqrt(1 - (1 - m) ** 2)
    return f


def FAIRLY_FALSE():
    """Part of a circle in quadrant I."""
    def f(m):
        return sqrt(1 - m ** 2)
    return f