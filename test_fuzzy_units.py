
from hypothesis import given, strategies as st

from fuzzy import functions as fun


@given(st.floats(allow_nan=False, allow_infinity=False))
def test_noop(x):
    f = fun.noop()
    assert f(x) == x

@given(st.floats(allow_nan=False, allow_infinity=False))
def test_invert(x):
    f = fun.inv()
    assert f(x) == 1 - x
    
    n = fun.noop()
    f = fun.inv(n)
    assert f(x) == 1 - x
    


@given(st.floats(allow_nan=False, allow_infinity=False), 
       st.floats(allow_nan=False, allow_infinity=False))
def test_constant(c, r):
    f = fun.constant(c)
    assert f(r) == c

    
@given(st.floats(min_value=0, max_value=1),
       st.floats(min_value=0, max_value=1),
       st.floats(allow_nan=False))
def test_alpha(lower, upper, x):
    if lower >= upper:
        return
    f = fun.alpha(floor=lower, ceiling=upper)
    if x <= lower:
        assert f(x) == lower
    if x >= upper:
        assert f(x) == upper
    else:
        assert f(x) == x