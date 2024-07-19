"""Functions that map arbitrary values to the unit interval.

Quote from 'Fuzzy Logic and Control: Software and Hardware Applications':

"A convex fuzzy set is described by a membership function whose
membership values are strictly monotonically increasing, or whose
membership values are strictly monotonically decreasing, or whose
membership values are strictly monotonically increasing then strictly
monotonically decreasing with increasing values for elements in the universe."

We don't comply (as actually does the book) with that definition as we
use functions that are not *strictly* monotonic.


:Author: Anselm Kiefner
:Version: 3
:Date: 2013-02-15
:Status: superseded
"""

from math import exp, log

from numpy import clip

from .base import FuzzyFunction


class constant(FuzzyFunction):
    """Return a fixed value no matter what input.
    >>> constant(6)(2)
    Traceback (most recent call last):
    ...
    AssertionError: not within the unit interval

    >>> constant(0.7)(9)
    0.7
    """

    def __init__(self, fix):
        assert 0 <= fix <= 1, 'not within the unit interval'
        self.fix = fix

    def __call__(self, x):
        return self.fix


class singleton(FuzzyFunction):
    __slots__ = ['value']

    """A single exact value."""

    def __init__(self, value):
        self.value = value

    def __call__(self, x):
        return 1 if x == self.value else 0


class linearA(FuzzyFunction):
    """A textbook linear function with y-axis section and gradient.
    variables
    --------
    b: float
        y-axis section - function is only *linear* if b == 0
    m: float
        gradient - if m == 0, the function is constant

    >>> linearA(2)(3)
    1
    >>> linearA(-1, 2)(1.5)
    0.5
    """

    def __init__(self, m=0, b=0):
        self.m = m
        self.b = b

    def __call__(self, x):
        return clip(self.m * x + self.b, 0, 1)


class linear(FuzzyFunction):
    """Variant of the linear function with gradient being determined by bounds.

    The bounds determine minimum and maximum value-mappings,
    but also the gradient. As [0, 1] must be the bounds for y-values,
    left and right bounds specify 2 points on the graph, for which the formula
    f(x) = y = (y2 - y1) / (x2 - x1) * (x - x1) + y1 = (y2 - y1) / (x2 - x1) *
                                                                (x - x2) + y2

    (right_y - left_y) / ((right - left) * (x - self.left) + left_y)
    works.

    vars
    ----
    top: float
        the x-value, where f(x) = 1
    bottom: float
        the x-value, where f(x) = 0
    top_y: float
        y-value of the left limit
    bottom_y: float
        y-value of the right limit

    >>> f = linear(1, 10)
    >>> [round(f(x), 2) for x in arange(1, 11)]
    [0.0, 0.11, 0.22, 0.33, 0.44, 0.56, 0.67, 0.78, 0.89, 1.0]

    >>> f = linear(10, 1)
    >>> [round(f(x), 2) for x in arange(1, 11)]
    [1.0, 0.89, 0.78, 0.67, 0.56, 0.44, 0.33, 0.22, 0.11, 0.0]

    >>> f = linear(3, 5)
    >>> [round(f(x), 2) for x in arange(1, 6)]
    [0.0, 0.0, 0.0, 0.5, 1.0]

    >>> f = linear(7, 5)
    >>> [round(f(x), 2) for x in arange(5, 12)]
    [1.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0]
    """

    def __init__(self, bottom, top, top_y=1, bottom_y=0):
        self.top = float(top)
        self.bottom = float(bottom)
        self.top_y = top_y
        self.bottom_y = bottom_y
        self.gradient = (self.top_y - self.bottom_y) / (self.top - self.bottom)

    def __call__(self, x):
        return clip(self.gradient * (x - self.bottom) + self.bottom_y, 0, 1)


class logistic(FuzzyFunction):
    """Derived from the logistic function.

    >>> f = logistic()
    >>> f(0)
    0.01
    >>> round(f(100000), 2)
    0.99
    >>> f(-5)
    0
    """

    def __init__(self, G=0.99, k=1, f_0=0.01):
        self.G = G
        self.k = k
        self.foo = (G / f_0 - 1.)  # precalculated for a little performance

    def __call__(self, x):
        if x < 0:
            return 0
        return self.G * 1 / (1 + exp(-self.k * self.G * x) * self.foo)


class rectangular(FuzzyFunction):
    """Basic rectangular function that returns the core_y for the core else 0.

    graph
    -----
        ______
        |    |
    ____|    |___


    left: float
        minimum x-axis value for the rectangle
    right: float
        maximum x-axis value for the rectangle
    core_y: float
        "height" of the rectangle

    """
    def __init__(self, left, right, core_y=1):
        assert left < right, "Left must be smaller than right."
        self.left = left
        self.right = right
        self.core_y = core_y

    def __call__(self, x):
        return self.core_y if self.left <= x <= self.right else 0


class triangular(FuzzyFunction):
    """Basic triangular norm as combination of two linear functions.

    graph
    -----
         /\
    ____/  \___


    vars
    ----
    left
        minimal non-0 x-value
    right
        maximal non-0 x-value
    core
        x-value of the maximal y-value
        if None, the peak is in the middle of left and right
    core_y
        maximal y-value, normally 1

    """
    def __init__(self, left, right, core=None, core_y=1):
        assert left < right, "left must be smaller than right"
        self.left = left
        self.right = right
        self.core = core if core is not None else (left + right) / 2.
        assert left < self.core < right, "core must be between the limits"
        self.core_y = core_y
        # piecewise-linear left side
        self.left_linear = linear(left, self.core, bottom_y=0, top_y=core_y)
        self.right_linear = linear(self.core, right, bottom_y=core_y, top_y=0)

    def __call__(self, x):
        return self.left_linear(x) if x <= self.core else self.right_linear(x)


class trapezoid(FuzzyFunction):
    """Combination of rectangular and triangular, for convenience.

    graph
    -----
          ____
         /    \
    ____/      \___

    vars
    ----

    left
        for x <= left: f(x) == 0
    core_left and core_right
        for core_left <= x <= core_right: f(x) == core_y
    right
        for x >= right: f(x) == 0
    """

    def __init__(self, left, core_left, core_right, right, height=1,
                 inverse=False):
        assert left < core_left <= core_right < right, "Overlapping params."
        assert height >= 0, 'Core must not be negative'
        self.height = height
        self.left = left
        self.core_left = core_left
        self.core_right = core_right
        self.right = right
        self.inverse = inverse

    def __call__(self, x):
        if x < self.left:
            return 0 if not self.inverse else 1
        elif x < self.core_left:
            return (linear(self.left, self.core_left, right_y=self.height)
                    if not self.inverse else
                    linear(self.left, self.core_left, right_y=self.height,
                    inverse=True))
        elif x < self.core_right:
            return self.height if not self.inverse else self.inverse(
                self.height)
        elif x < self.right:
            return (linear(self.core_right, self.right, left_y=self.height,
                    right_y=0)
                    if not self.inverse else
                    linear(self.core_right, self.right, left_y=self.height,
                    inverse=True))
        else:
            return 0 if not self.inverse else 1


class sigmoid(FuzzyFunction):
    """Calculates a weight based on the sigmoid function.

    We specify the lower limit where f(x) = 0.1 and the
    upper with f(x) = 0.9 and calculate the steepness and elasticity
    based on these. We don't need the general logistic function as we
    operate on [0,1].

    vars
    ----
    left:float
        minimum x-value with f(x) = left_y (normally 0.1)
    right:float
        maximum x-value with f(x) = right_y (normally 0.9)
    left_y: float
        minimal y-value of the function
    right_y: float
        maximal y-value of the function

    >>> f = sigmoid(0, 1)
    >>> f(0)
    0.1
    >>> round(f(100000), 2)
    1.0
    >>> f(-100000)
    0.0

    TODO: make actual use of left_y, right_y

    """

    def __init__(self, left, right, left_y=0.1, right_y=0.9):
        assert left < right, "left must be smaller than right"
        self.k = -(4. * log(3)) / (left - right)
        self.o = 9 * exp(left * self.k)

    def __call__(self, x):
        try:
            return 1. / (1. + exp(-self.k * x) * self.o)
        except OverflowError:
            return 0.0


class sigmoidB(FuzzyFunction):
    """A sigmoid variant with only one parameter.

    There's a catch: the curve starts high and grows low.


    >>> f = sigmoidB()

    >>> f(-1000)
    1.0
    >>> f(0)
    0.5
    >>> f(1000)
    0.0
    >>> round(f(-20), 2)
    0.99
    >>> round(f(20), 2)
    0.01
    """
    def __init__(self, k=0.229756):
        self.k = k

    def __call__(self, x):
        if x < -20:
            return 1.0
        if x > 20:
            return 0.0

        return 1 / (1 + exp(x * self.k))


class triangular_sigmoid(FuzzyFunction):
    def __init__(self, left, right, left_y=0, right_y=0, core=None, core_y=1):
        assert left < right, "left must be smaller than right"
        if core is not None:
            assert left < core < right, "core must be between the limits"
        self.core = core if core is not None else (left + right) / 2.
        self.core_y = core_y
        self.left_sigmoid = sigmoid(left, self.core, left_y, core_y)
        self.right_sigmoid = sigmoid(self.core, right, core_y, right_y)

    def __call__(self, x):
        if x < self.core:
            return self.left_sigmoid(x)
        elif self.core < x:
            return self.right_sigmoid(x)
        else:
            return self.core_y


class gaussianA(FuzzyFunction):
    """Defined by ae^(-b(x-x0)^2), a gaussian distribution.
    Basically a triangular sigmoid function, it comes close to human perception.

    vars
    ----
    a
        defines the maximum y-value of the graph
    b
        defines the steepness
    x0
        defines the symmetry center of the graph
    """

    def __init__(self, b, x0, a=1):
        self.a = a
        self.b = b
        self.x0 = x0

    def __call__(self, x):
        return self.a * exp(-self.b * (x - self.x0)**2)


class gaussian(FuzzyFunction):
    """Variant of the gaussian function that takes similar parameters as the others.

    left
        lower x-value for which f(x) == peak/10. (thus usually 0.1)
    right
        upper x-value for which f(x) == peak/10.
    peak
        maximum y-value of the graph
    """
    def __init__(self, left, right, peak=1):
        self.left = left
        self.right = right
        self.peak = peak


if __name__ == "__main__":
    import doctest
    doctest.testmod()
