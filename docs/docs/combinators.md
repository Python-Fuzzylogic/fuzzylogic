Module fuzzylogic.combinators
=============================
Combine two linguistic terms.

a and b are functions of two sets of the same domain.

Since these combinators are used directly in the Set class to implement logic operations, 
the most obvious use of this module is when subclassing Set to make use of specific combinators
for special circumstances.

Most functions also SHOULD support an arbitrary  number of arguments so they can be used in
other contexts than just fuzzy sets. HOWEVER, mind that the primary set of arguments always are functors and
there is always only one secondary argument - the value to be evaluated.

## Example

    def bounded_sum(*guncs):
        funcs = list(guncs)

        def op(x, y):
            return x + y - x * y

        def F(z):
            return reduce(op, (f(z) for f in funcs))

        return F

This function is initialized with any number of membership functions ("guncs")
which are then turned into a fixed list and numba.njit-ed in the future.

> f = bounded_sum(R(0, 10), R(5, 15), S(0, 10))

would return the inner F function and prepare everything for operation in an initialization phase.
Now ready for operational phase, when called with a value like `f(5)`, 
the inner function applies all specified functions to this value
and combines these membership-values via the inner op function, reducing it all to a single value in [0,1].

Functions
---------

    
`MAX(*guncs)`
:   Classic OR variant.

    
`MIN(*guncs) ‑> collections.abc.Callable`
:   Classic AND variant.

    
`bounded_sum(*guncs)`
:   OR variant.

    
`einstein_product(*guncs)`
:   AND variant.

    
`einstein_sum(*guncs)`
:   OR variant.

    
`gamma_op(g)`
:   Combine AND with OR by a weighing factor g.
    
    This is called a 'compensatoric' operator.
    
    g (gamma-factor)
        0 < g < 1 (g == 0 -> AND; g == 1 -> OR)
    
    Same problem as with lambda_op, since all combinators only take functions as arguments, so we parametrize this with g in a pre-init step.

    
`hamacher_product(*guncs)`
:   AND variant.
    
    (xy) / (x + y - xy) for x, y != 0
    0 otherwise

    
`hamacher_sum(*guncs)`
:   OR variant.
    
    (x + y - 2xy) / (1 - xy) for x,y != 1
    1 otherwise

    
`lambda_op(l)`
:   A 'compensatoric' operator, combining AND with OR by a weighing factor l.
    
    This complicates matters a little, since all normal combinators only take functions as parameters so we parametrize this with l in a pre-init step.

    
`lukasiewicz_AND(*guncs)`
:   AND variant.

    
`lukasiewicz_OR(*guncs)`
:   OR variant.

    
`njit(func)`
:   

    
`product(*guncs)`
:   AND variant.

    
`simple_disjoint_sum(*guncs)`
:   Simple fuzzy XOR operation.
    Someone fancy a math proof?
    
    Basic idea:
    (A AND ~B) OR (~A AND B)
    
    >>> xor = simple_disjoint_sum(noop(), noop())
    >>> xor(0)
    0
    >>> xor(1)
    0
    >>> xor(0.5)
    0.5
    >>> xor(0.3) == round(xor(0.7), 2)
    True
    
    Attempt for expansion without proof:
    x = 0.5
    y = 1
    (x and ~y) or (~x and b)
    
    max(min(0.5, 0), min(0.5, 1)) == 0.5
    
    ----
    
    x = 0
    y = 0.5
    z = 1
    
    (A AND ~B AND ~C) OR (B AND ~A AND ~C) OR (C AND ~B AND ~A)
    max(min(0,0.5,0), min(0.5,1,0), min(1,0.5,1)) == 0.5