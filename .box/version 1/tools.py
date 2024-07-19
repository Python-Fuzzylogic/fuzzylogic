
import numpy as np


def normalize(lst):
    high = max(lst)
    return [value/float(high) for value in lst]

def center_of_gravity(A):
    """
    >>> from fuzzification import singleton
    >>> r = np.arange(0, 10, 1)
    >>> f = singleton(3)
    >>> A = [f(x) for x in r]
    >>> center_of_gravity(A)
    3.0
    >>> from fuzzification import rectangular
    >>> f = rectangular(2,4)
    >>> A = [f(x) for x in r]
    >>> center_of_gravity(A)
    3.0
    >>> from fuzzification import linear
    >>> f = linear(0,1)
    >>> A = [f(x) for x in r]
    >>> center_of_gravity(A)
    5.0
    """
    return (1. / np.sum(A)) * sum(a*x for a,x in enumerate(A))

if __name__ == "__main__":
    import doctest
    doctest.testmod()

    import cProfile
    from timeit import Timer

    from .fuzzification import constant

    def test1():
        r = np.arange(0,100,1)
        f = constant(1)
        A = [f(x) for x in r]
        center_of_gravity(A)

    f = constant(1)
    r = np.arange(0, 100, 1)
    A = np.array([f(x) for x in r])

    def test2():
        center_of_gravity(A)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
