"""
functions.py - General-purpose functions that map R -> [0,1].

These functions work as closures.
The inner function uses the variables of the outer function.

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

The intervals with non-zero m are called 'support', short s_m
The intervals with m == 1 are called 'core', short c_m
The intervals with max(m) are called "height"
The intervals  m != 1 and m != 0 are called 'boundary'.
The intervals with m == 0 are called 'unsupported', short no_m

In a fuzzy set with one and only one m == 1, this element is called 'prototype'.
"""

from __future__ import annotations

from collections.abc import Callable
from math import exp, isinf, isnan, log
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .classes import SingletonSet

type Membership = Callable[[float], float]


try:
    from numba import njit as njit  # ready for prime time?

    raise ImportError

except ImportError:

    def njit(func: Membership) -> Membership:
        return func


LOW_HIGH = "low must be less than high"

#####################
# SPECIAL FUNCTIONS #
#####################


def inv(g: Membership) -> Membership:
    """Invert the given function within the unit-interval.

    For sets, the ~ operator uses this. It is equivalent to the TRUTH value of FALSE.
    """

    def f(x: float) -> float:
        return float(1 - g(x))

    return f


def noop() -> Membership:
    """Do nothing and return the value as is.

    Useful for testing.
    """

    def f(x: float) -> float:
        return x

    return f


def constant(c: float) -> Membership:
    """Return always the same value, no matter the input.

    Useful for testing.
    >>> f = constant(1)
    >>> f(0)
    1
    """

    def f(_: float) -> float:
        return c

    return f


def alpha(
    *,
    floor: float = 0,
    ceiling: float = 1,
    func: Membership,
    floor_clip: float | None = None,
    ceiling_clip: float | None = None,
) -> Membership:
    """Clip a function's values.

    This is used to either cut off the upper or lower part of a graph.
    Actually, this is more like a hedge but doesn't make sense for sets.
    """
    assert floor <= ceiling, breakpoint()
    assert 0 <= floor, breakpoint()
    assert ceiling <= 1, breakpoint()

    floor_clip = floor if floor_clip is None else floor_clip
    ceiling_clip = ceiling if ceiling_clip is None else ceiling_clip

    def f(x: float) -> float:
        m = func(x)
        if m >= ceiling:
            return ceiling_clip
        elif m <= floor:
            return floor_clip
        else:
            return m

    return f


def normalize(height: float, func: Callable[[float], float]) -> Callable[[float], float]:
    """Map [0,1] to [0,1] so that max(array) == 1."""
    assert 0 < height <= 1

    def f(x: float) -> float:
        return func(x) / height

    return f


def moderate(func: Callable[[float], float]) -> Callable[[float], float]:
    """Map [0,1] -> [0,1] with bias towards 0.5.

    For instance this is needed to dampen extremes.
    """

    def f(x: float) -> float:
        return 1 / 2 + 4 * (func(x) - 1 / 2) ** 3

    return f


########################
# MEMBERSHIP FUNCTIONS #
########################


def singleton(c: float, no_m: float = 0, c_m: float = 1) -> SingletonSet:
    """A singleton function.

    This is unusually tricky because the CoG sums up all values and divides by the number of values, which
    may result in 0 due to rounding errors.
    Additionally and more significantly, a singleton well within domain range but not within
    its resolution will never be found and considered. Thus, singletons need special treatment.

    We solve this issue by returning a special subclass (which must be imported here due to circular import),
    which overrides the normal CoG implementation, but still works with the rest of the code.
    """
    from .classes import SingletonSet

    return SingletonSet(c, no_m=no_m, c_m=c_m)


def linear(m: float = 0, b: float = 0) -> Membership:
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

    def f(x: float) -> float:
        y = m * x + b
        if y <= 0:
            return 0
        elif y >= 1:
            return 1
        else:
            return y

    return f


def step(limit: float, /, *, left: float = 0, right: float = 1, at_lmt: float | None = None) -> Membership:
    """A step function.

    Coming from left, the function returns the *left* argument.
    At the limit, it returns *at_lmt* or the average of left and right.
    After the limit, it returns the *right* argument.
    >>> f = step(2)
    >>> f(1)
    0
    >>> f(2)
    0.5
    >>> f(3)
    1
    """
    assert 0 <= left <= 1 and 0 <= right <= 1

    def f(x: float) -> float:
        if x < limit:
            return left
        elif x > limit:
            return right
        else:
            return at_lmt if at_lmt is not None else (left + right) / 2

    return f


def bounded_linear(
    low: float, high: float, *, c_m: float = 1, no_m: float = 0, inverse: bool = False
) -> Membership:
    """Variant of the linear function with gradient being determined by bounds.

    The bounds determine minimum and maximum value-mappings,
    but also the gradient. As [0, 1] must be the bounds for y-values,
    left and right bounds specify 2 points on the graph, for which the formula
    f(x) = y = (y2 - y1) / (x2 - x1) * (x - x1) + y1 = (y2 - y1) / (x2 - x1) *
                                                                (x - x2) + y2

    (right_y - left_y) / ((right - left) * (x - self.left) + left_y)
    works.

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
    assert low < high, LOW_HIGH
    assert c_m > no_m, "core_m must be greater than unsupported_m"

    if inverse:
        c_m, no_m = no_m, c_m

    gradient = (c_m - no_m) / (high - low)

    # special cases found by hypothesis

    def g_0(_: Any) -> float:
        return (c_m + no_m) / 2

    if gradient == 0:
        return g_0

    def g_inf(x: float) -> float:
        asymptode = (high + low) / 2
        if x < asymptode:
            return no_m
        elif x > asymptode:
            return c_m
        else:
            return (c_m + no_m) / 2

    if isinf(gradient):
        return g_inf

    def f(x: float) -> float:
        y = gradient * (x - low) + no_m
        if y < 0:
            return 0.0
        return 1.0 if y > 1 else y

    return f


def R(low: float, high: float) -> Membership:
    """Simple alternative for bounded_linear().

    THIS FUNCTION ONLY CAN HAVE A POSITIVE SLOPE -
    USE THE S() FUNCTION FOR NEGATIVE SLOPE.
    """
    assert low < high, f"{low} < {high} is not true."

    def f(x: float) -> float:
        if x < low or isinf(high - low):
            return 0
        elif low <= x <= high:
            return (x - low) / (high - low)
        else:
            return 1

    return f


def S(low: float, high: float) -> Membership:
    """Simple alternative for bounded_linear.

    THIS FUNCTION ONLY CAN HAVE A NEGATIVE SLOPE -
    USE THE R() FUNCTION FOR POSITIVE SLOPE.
    """
    assert low < high, f"{low} must be less than {high}."

    def f(x: float) -> float:
        if x <= low:
            return 1
        elif low < x < high:
            # factorized to avoid nan
            return high / (high - low) - x / (high - low)
        else:
            return 0

    return f


def rectangular(low: float, high: float, *, c_m: float = 1, no_m: float = 0) -> Membership:
    """Basic rectangular function that returns the core_y for the core else 0.

        ______
        |    |
    ____|    |___
    """
    assert low < high, f"{low}, {high}"

    def f(x: float) -> float:
        return no_m if x < low or high < x else c_m

    return f


def triangular(
    low: float, high: float, *, c: float | None = None, c_m: float = 1, no_m: float = 0
) -> Membership:
    r"""Basic triangular norm as combination of two linear functions.

         /\
    ____/  \___

    """
    assert low < high, "low must be less than high."
    assert no_m < c_m

    c = c if c is not None else (low + high) / 2.0
    assert low < c < high, "peak must be inbetween"

    left_slope = bounded_linear(low, c, no_m=0, c_m=c_m)
    right_slope = inv(bounded_linear(c, high, no_m=0, c_m=c_m))

    def f(x: float) -> float:
        return left_slope(x) if x <= c else right_slope(x)

    return f


def trapezoid(
    low: float, c_low: float, c_high: float, high: float, *, c_m: float = 1, no_m: float = 0
) -> Membership:
    r"""Combination of rectangular and triangular, for convenience.

          ____
         /    \
    ____/      \___

    """
    assert low < c_low <= c_high < high
    assert 0 <= no_m < c_m <= 1

    left_slope = bounded_linear(low, c_low, c_m=c_m, no_m=no_m)
    right_slope = bounded_linear(c_high, high, c_m=c_m, no_m=no_m, inverse=True)

    def f(x: float) -> float:
        if x < low or high < x:
            return no_m
        elif x < c_low:
            return left_slope(x)
        elif x > c_high:
            return right_slope(x)
        else:
            return c_m

    return f


def sigmoid(L: float, k: float, x0: float = 0) -> Membership:
    """Special logistic function.

    http://en.wikipedia.org/wiki/Logistic_function

    f(x) = L / (1 + e^(-k*(x-x0)))
    with
    x0 = x-value of the midpoint
    L = the curve's maximum value
    k = steepness
    """
    # need to be really careful here, otherwise we end up in nanland
    assert 0 < L <= 1, "L invalid."

    def f(x: float) -> float:
        if isnan(k * x):
            # e^(0*inf) == 1
            o = 1.0
        else:
            try:
                o = exp(-k * (x - x0))
            except OverflowError:
                o = float("inf")
        return L / (1 + o)

    return f


def bounded_sigmoid(low: float, high: float, inverse: bool = False) -> Membership:
    """
    Calculate a weight based on the sigmoid function.

    Specify the lower limit where f(x) = 0.1 and the
    upper with f(x) = 0.9 and calculate the steepness and elasticity
    based on these. We don't need the general logistic function as we
    operate on [0,1].

    core idea:
    f(x) = 1. / (1. + exp(x * (4. * log(3)) / (low - high)) *
                9 * exp(low * -(4. * log(3)) / (low - high)))

    How I got this? IIRC I was playing around with linear equations and
    boundary conditions of sigmoid funcs on wolframalpha..

    previously factored to:
    k = -(4. * log(3)) / (low - high)
    o = 9 * exp(low * k)
    return 1 / (1 + exp(-k * x) * o)

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
    assert low < high, LOW_HIGH

    if inverse:
        low, high = high, low

    k = (4.0 * log(3)) / (low - high)
    try:
        # if high - low underflows to 0..
        if isinf(k):
            p = 0.0
        # just in case k -> 0 and low -> inf
        elif isnan(-k * low):
            p = 1.0
        else:
            p = exp(-k * low)
    except OverflowError:
        p = float("inf")

    def f(x: float) -> float:
        try:
            # e^(0*inf) = 1 for both -inf and +inf
            q = 1.0 if (isinf(k) and x == 0) or (k == 0 and isinf(x)) else exp(x * k)
        except OverflowError:
            q = float("inf")

        # e^(inf)*e^(-inf) == 1
        r = p * q
        if isnan(r):
            r = 1
        return 1 / (1 + 9 * r)

    return f


def bounded_exponential(k: float = 0.1, limit: float = 1) -> Membership:
    """Function that goes through the origin and approaches a limit.
    k determines the steepness. The function defined for [0, +inf).
    Useful for things that can't be below 0 but may not have a limit like temperature
    or time, so values are always defined.
    f(x)=limit-limit/e^(k*x)

    Again: This function assumes x >= 0, there are no checks for this assumption!
    """
    assert limit > 0
    assert k > 0

    def f(x: float) -> float:
        try:
            return limit - limit / exp(k * x)
        except OverflowError:
            return limit

    return f


def simple_sigmoid(k: float = 0.229756) -> Membership:
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

    def f(x: float) -> float:
        if isinf(x) and k == 0:
            return 1 / 2
        try:
            return 1 / (1 + exp(x * -k))
        except OverflowError:
            return 0.0

    return f


def triangular_sigmoid(low: float, high: float, c: float | None = None) -> Membership:
    """Version of triangular using sigmoids instead of linear.

    THIS FUNCTION PEAKS AT 0.9

    >>> g = triangular_sigmoid(2, 4)
    >>> g(2)
    0.1
    >>> round(g(3), 2)
    0.9
    """
    assert low < high, LOW_HIGH
    c = c if c is not None else (low + high) / 2.0
    assert low < c < high, "c must be inbetween"

    left_slope = bounded_sigmoid(low, c)
    right_slope = inv(bounded_sigmoid(c, high))

    def f(x: float) -> float:
        return left_slope(x) if x <= c else right_slope(x)

    return f


def gauss(c: float, b: float, *, c_m: float = 1) -> Membership:
    """Defined by ae^(-b(x-x0)^2), a gaussian distribution.

    Basically a triangular sigmoid function, it comes close to human perception.

    vars
    ----
    c_m (a)
        defines the maximum y-value of the graph
    b
        defines the steepness
    c (x0)
        defines the symmetry center/peak of the graph
    """
    assert 0 < c_m <= 1
    assert 0 < b, "b must be greater than 0"

    def f(x: float) -> float:
        try:
            o = (x - c) ** 2
        except OverflowError:
            return 0
        return c_m * exp(-b * o)

    return f


if __name__ == "__main__":
    import doctest

    doctest.testmod()
