
from hypothesis import given, strategies as st

from fuzzy import functions as fun

@given(st.floats(min_value=0, max_value=1), 
       st.floats(min_value=0, max_value=1))
def test_constant(c, r):
    f = fun.constant(c)
    assert f(r) == c