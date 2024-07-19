"""These functions operate on a FuzzySet at a time to modify its shape.


sources
-------

http://kik.informatik.fh-dortmund.de/abschlussarbeiten/fuzzyControl/operatoren.html
"""


def shift_to_middle(x):
    """This function maps [0,1] -> [0,1] with bias towards 0.5.

    For instance this is needed to dampen extremes.
    """
    return 1/2 + 4 * (x - 1/2)**3

def inverse(x):
    return 1-x

def concentration(x):
    """Used to reduce the amount of values the set includes and to dampen the
    membership of many values.
    """
    return x**2

def contrast_intensification(x):
    """Increases the membership of values that already strongly belong to the set
    and dampens the rest.
    """

    if x < 0.5:
        return 2 * x**2
    else:
        return 1 - 2(1 - x**2)

def dilatation(x):
    """Expands the set with more values and already included values are enhanced."""
    return x ** 1./2.

def multiplication(x, n):
    """Set is multiplied with a constant factor, which changes all membership values."""
    return x * n

def negation(x):
    return 1 - x
