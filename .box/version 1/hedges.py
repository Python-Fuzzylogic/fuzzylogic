"""
Lingual hedges modify curves describing truthvalues.
"""


def very(fit):
    return fit ** 2


def plus(fit):
    return fit ** 1.25


def minus(fit):
    return fit ** 0.75


def highly(fit):
    return minus(very(very(fit)))


if __name__ == "__main__":
    import doctest
    doctest.testmod()
