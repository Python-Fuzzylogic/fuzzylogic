
"""
--------------------
FUZZY FUNCTIONS
--------------------
Collection of general-purpose functions that map a value X onto the
unit-interval [0,1]. These functions work as closures. The inner function uses
the variables of the outer function.

These functions work in two steps: prime and call.
In the first step the function is constructed, initialized and
constants pre-evaluated. In the second step the actual value
is passed into the function, using the arguments of the first step.

Definitions
-----------
These functions are used to determine the *membership* of a value x in a fuzzy-
set. Thus, the 'height' is the variable 'm' in general.
In a normal set there is at least one m with m == 1. This is the default.
In a non-normal set, the global maximum and minimum is skewed.
The following definitions are for normal sets.

The intervals with non-zero m are called 'support'.
The intervals with m == 1 are called 'core'.
The intervals  m != 1 and m != 0 are called 'boundary'.
The intervals with m == 0 are called 'unsupported'.

In a fuzzy set with one and only one m == 1, this element is called 'prototype'.
"""


from math import exp, log, sqrt

#####################
# SPECIAL FUNCTIONS #
#####################

def inv(g):
    """Invert the given function within the unit-interval.
    For sets, the ~ operator uses this. It is equivalent to the TRUTH value of FALSE.
    """
    def f(x):
        return 1 - g(x)
    return f


def noop():
    """Do nothing and return the value as is.
    Useful for testing.
    """
    def f(x):
        return x
    return f

def constant(c):
    """Always return the same value, no matter the input.
    Useful for testing.
    >>> f = constant(1)
    >>> f(0)
    1
    """

    def f(x):
        return c
    return f


def alpha(floor, ceiling, func):
    """Function to clip a function.
    This is used to either cut off the upper or lower part of a graph.
    Actually, this is more like a hedge but doesn't make sense for sets.
    """
    assert floor <= ceiling
    assert 0 <= floor
    assert 1 >= ceiling
    
    def f(x):
        if func(x) >= ceiling:
            return ceiling
        elif func(x) <= floor:
            return floor
        else: 
            return func(x)
    return f

########################
# MEMBERSHIP FUNCTIONS #
########################

def singleton(p, non_p_m=0, p_m=1):
    """A single spike.
    vars:
        p (prototype) - single value with
        p_m (prototype membership value)
        non_p_m - value of all values but p
    >>> f = singleton(2)
    >>> f(1)
    0
    >>> f(2)
    1
    """

    assert 0 <= p_m <= 1
    assert 0 <= non_p_m <= 1

    def f(x):
        return p_m if x == p else non_p_m

    return f


def linear(m:float=0, b:float=0) -> callable:
    """A textbook linear function with y-axis section and gradient.
    f(x) = m*x + b
    BUT CLIPPED.

    >>> f = linear(1, -1)
    >>> f(-2)   # should be -3 but clipped
    0
    >>> f(0)    # should be -1 but clipped
    0
    >>> f(1)
    0
    >>> f(1.5)
    0.5
    >>> f(2)
    1
    >>> f(3)    # should be 2 but clipped
    1
    """
    def f(x) -> float:
        y = m * x + b
        if y <= 0:
            return 0
        elif y >= 1:
            return 1
        else:
            return y
    return f


def bounded_linear(low_bound, high_bound, core_m=1, unsupported_m=0):
    """Variant of the linear function with gradient being determined by bounds.

    THIS FUNCTION ONLY CAN HAVE A POSITIVE SLOPE -
    USE inv() IF IT NEEDS TO BE NEGATIVE

    The bounds determine minimum and maximum value-mappings,
    but also the gradient. As [0, 1] must be the bounds for y-values,
    left and right bounds specify 2 points on the graph, for which the formula
    f(x) = y = (y2 - y1) / (x2 - x1) * (x - x1) + y1 = (y2 - y1) / (x2 - x1) *
                                                                (x - x2) + y2

    (right_y - left_y) / ((right - left) * (x - self.left) + left_y)
    works.

    vars
    ----
    high_bound: float
        the x-value, where f(x) = core_m
    low_bound: float
        the x-value, where f(x) = unsupported_m
    core_m: float
        membership-value of the maximum
    unsupported_m: float
        membership-value of the minimum

    >>> f = bounded_linear(2, 3)
    >>> f(1)
    0.0
    >>> f(2)
    0.0
    >>> f(2.5)
    0.5
    >>> f(3)
    1.0
    >>> f(4)
    1.0
    """
    if high_bound <= low_bound:
        raise ValueError('high must not be less than low.')

    gradient = (core_m - unsupported_m) / (high_bound - low_bound)

    def f(x):
        m = gradient * (x - low_bound) + unsupported_m
        if m < 0:
            return 0.
        if m > 1:
            return 1.
        return m
    return f


def R(left, right):
    """Simple alternative for bounded_linear().
    THIS FUNCTION ONLY CAN HAVE A POSITIVE SLOPE -
    USE THE S() FUNCTION FOR NEGATIVE SLOPE.
    """

    if left >= right:
        raise ValueError("left must be less than right.")

    def f(x):
        if x < left:
            return 0
        if left <= x <= right:
            return (x - left) / (right - left)
        if x > right:
            return 1
    return f


def S(left, right):
    """Simple alternative for inv(bounded_linear()
    THIS FUNCTION ONLY CAN HAVE A NEGATIVE SLOPE -
    USE THE R() FUNCTION FOR POSITIVE SLOPE.
    """
    if left >= right:
        raise ValueError("left must be less than right.")

    def f(x):
        if x < left:
            return 1
        if left <= x <= right:
            return (right - x) / (right - left)
        if right < x:
            return 0
    return f


def rectangular(left, right, core_m=1, unsupported_m=0):
    """Basic rectangular function that returns the core_y for the core else 0.

    graph
    -----
        ______
        |    |
    ____|    |___


    left: float
        min(x) with f(x) = core_m
    right: float
        max(x) with f(x) = core_m
    core_m: float
        "height" of the rectangle
    """

    if left > right:
        raise ValueError('left must not be greater than right.')

    def f(x):
        if x < left:
            return unsupported_m
        if left <= x <= right:
            return core_m
        if right < x:
            return unsupported_m

    return f


def triangular(left, right, p=None, p_m=1, unsupported_m=0):
    """Basic triangular norm as combination of two linear functions.

    graph
    -----
         /\
    ____/  \___


    vars
    ----
    left
        minimum supported x-value
    right
        maximum supported x-value
    p (as in 'peak' or 'prototype')
        x-value with the maximum m-value
        if None, p is in the middle of left and right
    p_m
        maximum membership-value, normal 1
    """
    if left > right:
        raise ValueError('left must not be greater than right.')
    p = p if p is not None else (left + right) / 2.
    if not(left <= p <= right):
        raise ValueError('p must be between left and right.')
    left_slope = bounded_linear(left, p, unsupported_m=0, core_m=p_m)
    right_slope = inv(bounded_linear(p, right, unsupported_m=0, core_m=p_m))

    def f(x):
        return left_slope(x) if x <= p else right_slope(x)

    return f


def trapezoid(left, c_left, c_right, right, c_m=1, unsupported_m=0):
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
        for core_left <= x <= core_right: f(x) == core_m
    right
        for x >= right: f(x) == 0
    """

    if not(left < c_left <= c_right < right):
        raise ValueError('NOT left < c_left <= c_right < right')

    if not(0 <= c_m <= 1):
        raise ValueError('c_m invalid.')

    if not(0 <= unsupported_m <= 1):
        raise ValueError('unsupported_m invalid.')

    left_slope = bounded_linear(left, c_left, c_m, unsupported_m)
    # right slope is negative - the meaning of c_m and unsupported_m are
    # reversed
    right_slope = inv(bounded_linear(c_right, right, c_m, unsupported_m))

    def f(x):
        # not touching the base
        if x < left or right < x:
            return unsupported_m
        if x < c_left:
            return left_slope(x)
        if x > c_right:
            return right_slope(x)
        # we're on the top
        return c_m

    return f


def sigmoid(L, k, x0):
    """Special logistic function.

    http://en.wikipedia.org/wiki/Logistic_function

    f(x) = L / (1 + e^(-k*(x-x0)))
    with
    x0 = x-value of the midpoint
    L = the curve's maximum value
    k = steepness
    """
    if not (0 <= L <= 1):
        raise ValueError('L invalid.')

    def f(x):
        return L / (1 + exp(-k*(x - x0)))

    return f


def bounded_sigmoid(low, high):
    """
    Calculates a weight based on the sigmoid function.

    We specify the lower limit where f(x) = 0.1 and the
    upper with f(x) = 0.9 and calculate the steepness and elasticity
    based on these. We don't need the general logistic function as we
    operate on [0,1].


    USE inv() IF IT NEEDS TO BE NEGATIVE

    vars
    ----
    low: x-value with f(x) = 0.1
    for x < low: m -> 0
    high: x-value with f(x) = 0.9
    for x > high: m -> 1

    >>> f = bounded_sigmoid(0, 1)
    >>> f(0)
    0.1
    >>> round(f(1), 2)
    0.9
    >>> round(f(100000), 2)
    1.0
    >>> round(f(-100000), 2)
    0.0
    """
    assert low < high, 'high must not be less than low'
    
    k = -(4. * log(3)) / (low - high)
    o = 9 * exp(low * k)

    def f(x):
        try:
            return 1. / (1. + exp(x * -k) * o)
        except OverflowError:
            return 0.0

    return f


def simple_sigmoid(k=0.229756):
    """Sigmoid variant with only one parameter (steepness).

    The midpoint is 0.

    The slope is positive for positive k and negative k.

    f(x) is within [0,1] for any real k and x.


    >>> f = simple_sigmoid()

    >>> round(f(-1000), 2)
    0.0
    >>> f(0)
    0.5
    >>> round(f(1000), 2)
    1.0
    >>> round(f(-20), 2)
    0.01
    >>> round(f(20), 2)
    0.99
    """
    def f(x):
        return 1 / (1 + exp(x * -k))

    return f


def triangular_sigmoid(left, right, p=None):
    """Version of triangular using sigmoids instead of linear.
    THIS FUNCTION PEAKS AT 0.9

    >>> g = triangular_sigmoid(2, 4)
    >>> g(2)
    0.1
    >>> round(g(3), 2)
    0.9
    """

    if left > right:
        raise ValueError('left must not be less than right.')
    p = p if p is not None else (left + right) / 2.
    if not(left <= p <= right):
        raise ValueError('NOT left <= p <= right')

    left_slope = bounded_sigmoid(left, p)
    right_slope = inv(bounded_sigmoid(p, right))

    def f(x):
        if x <= p:
            return left_slope(x)
        else:
            return right_slope(x)

    return f


def gauss(b, p, p_m=1):
    """Defined by ae^(-b(x-x0)^2), a gaussian distribution.
    Basically a triangular sigmoid function, it comes close to human perception.

    vars
    ----
    p_m (a)
        defines the maximum y-value of the graph
    b
        defines the steepness
    p (x0)
        defines the symmetry center of the graph
    """

    def f(x):
        return p_m * exp(-b * (x - p)**2)
    return f


if __name__ == "__main__":
    import doctest
    doctest.testmod()