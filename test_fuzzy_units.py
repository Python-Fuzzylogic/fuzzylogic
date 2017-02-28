
from hypothesis import given, strategies as st, assume
from math import isclose

from fuzzy import functions as fun
    
@given(st.floats(allow_nan=False, allow_infinity=False))
def test_noop(x):
    f = fun.noop()
    assert f(x) == x

@given(st.floats(allow_nan=False, allow_infinity=False))
def test_inv(x):
    assume(0 <= x <= 1)
    f = fun.inv(fun.noop())
    assert isclose(f(f(x)), x, abs_tol=1e-16)
    
@given(st.floats(allow_nan=False, allow_infinity=False), 
       st.floats(allow_nan=False, allow_infinity=False))
def test_constant(c, r):
    f = fun.constant(c)
    assert f(r) == c

    
@given(st.floats(min_value=0, max_value=1),
       st.floats(min_value=0, max_value=1),
       st.floats(allow_nan=False))
def test_alpha(lower, upper, x):
    assume(lower < upper)
    f = fun.alpha(lower, upper, fun.noop())
    if x <= lower:
        assert f(x) == lower
    elif x >= upper:
        assert f(x) == upper
    else:
        assert f(x) == x