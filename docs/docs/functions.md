Module fuzzylogic.functions
===========================
General-purpose functions that map R -> [0,1].
 
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

Functions
---------

    
`R(low, high)`
:   Simple alternative for bounded_linear().
    
    THIS FUNCTION ONLY CAN HAVE A POSITIVE SLOPE -
    USE THE S() FUNCTION FOR NEGATIVE SLOPE.

    
`S(low, high)`
:   Simple alternative for bounded_linear.
    
    THIS FUNCTION ONLY CAN HAVE A NEGATIVE SLOPE -
    USE THE R() FUNCTION FOR POSITIVE SLOPE.

    
`alpha(*, floor: float = 0, ceiling: float = 1, func: collections.abc.Callable, floor_clip: Optional[float] = None, ceiling_clip: Optional[float] = None)`
:   Clip a function's values.
    
    This is used to either cut off the upper or lower part of a graph.
    Actually, this is more like a hedge but doesn't make sense for sets.

    
`bounded_exponential(k=0.1, limit=1)`
:   Function that goes through the origin and approaches a limit.
    k determines the steepness. The function defined for [0, +inf).
    Useful for things that can't be below 0 but may not have a limit like temperature
    or time, so values are always defined.
    f(x)=limit-limit/e^(k*x)
    
    Again: This function assumes x >= 0, there are no checks for this assumption!

    
`bounded_linear(low: float, high: float, *, c_m: float = 1, no_m: float = 0, inverse=False)`
:   Variant of the linear function with gradient being determined by bounds.
    
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

    
`bounded_sigmoid(low, high, inverse=False)`
:   Calculate a weight based on the sigmoid function.
    
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

    
`constant(c: float) ‑> collections.abc.Callable`
:   Return always the same value, no matter the input.
    
    Useful for testing.
    >>> f = constant(1)
    >>> f(0)
    1

    
`gauss(c, b, *, c_m=1)`
:   Defined by ae^(-b(x-x0)^2), a gaussian distribution.
    
    Basically a triangular sigmoid function, it comes close to human perception.
    
    vars
    ----
    c_m (a)
        defines the maximum y-value of the graph
    b
        defines the steepness
    c (x0)
        defines the symmetry center/peak of the graph

    
`inv(g: collections.abc.Callable) ‑> collections.abc.Callable`
:   Invert the given function within the unit-interval.
    
    For sets, the ~ operator uses this. It is equivalent to the TRUTH value of FALSE.

    
`linear(m: float = 0, b: float = 0) ‑> <built-in function callable>`
:   A textbook linear function with y-axis section and gradient.
    
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

    
`moderate(func)`
:   Map [0,1] -> [0,1] with bias towards 0.5.
    
    For instance this is needed to dampen extremes.

    
`njit(func)`
:   

    
`noop() ‑> collections.abc.Callable`
:   Do nothing and return the value as is.
    
    Useful for testing.

    
`normalize(height, func)`
:   Map [0,1] to [0,1] so that max(array) == 1.

    
`rectangular(low: float, high: float, *, c_m: float = 1, no_m: float = 0) ‑> <built-in function callable>`
:   Basic rectangular function that returns the core_y for the core else 0.
    
        ______
        |    |
    ____|    |___

    
`sigmoid(L, k, x0)`
:   Special logistic function.
    
    http://en.wikipedia.org/wiki/Logistic_function
    
    f(x) = L / (1 + e^(-k*(x-x0)))
    with
    x0 = x-value of the midpoint
    L = the curve's maximum value
    k = steepness

    
`simple_sigmoid(k=0.229756)`
:   Sigmoid variant with only one parameter (steepness).
    
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

    
`singleton(p, *, no_m=0, c_m=1)`
:   A single spike.
    
    >>> f = singleton(2)
    >>> f(1)
    0
    >>> f(2)
    1

    
`trapezoid(low, c_low, c_high, high, *, c_m=1, no_m=0)`
:   Combination of rectangular and triangular, for convenience.
    
          ____
         /    \
    ____/      \___

    
`triangular(low, high, *, c=None, c_m=1, no_m=0)`
:   Basic triangular norm as combination of two linear functions.
    
         /\
    ____/  \___

    
`triangular_sigmoid(low, high, c=None)`
:   Version of triangular using sigmoids instead of linear.
    
    THIS FUNCTION PEAKS AT 0.9
    
    >>> g = triangular_sigmoid(2, 4)
    >>> g(2)
    0.1
    >>> round(g(3), 2)
    0.9