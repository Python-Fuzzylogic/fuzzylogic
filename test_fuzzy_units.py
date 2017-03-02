
from hypothesis import given, strategies as st, assume
from math import isclose
from unittest import TestCase

from fuzzy.classes import Domain, Set, Rule
from fuzzy import functions as fun
from fuzzy import hedges

class Test_Functions(TestCase):
    @given(st.floats(allow_nan=False))
    def test_noop(self, x):
        f = fun.noop()
        assert f(x) == x

    @given(st.floats(allow_nan=False, allow_infinity=False))
    def test_inv(self, x):
        assume(0 <= x <= 1)
        f = fun.inv(fun.noop())
        assert isclose(f(f(x)), x, abs_tol=1e-16)

    @given(st.floats(allow_nan=False, allow_infinity=False), 
           st.floats(allow_nan=False, allow_infinity=False))
    def test_constant(self, x, c):
        f = fun.constant(c)
        assert f(x) == c


    @given(st.floats(allow_nan=False),
            st.floats(min_value=0, max_value=1),
            st.floats(min_value=0, max_value=1),
           )
    def test_alpha(self, x, lower, upper):
        assume(lower < upper)
        f = fun.alpha(lower, upper, fun.noop())
        if x <= lower:
            assert f(x) == lower
        elif x >= upper:
            assert f(x) == upper
        else:
            assert f(x) == x

    @given(st.floats(),
           st.floats(),
           st.floats(min_value=0, max_value=1),
           st.floats(min_value=0, max_value=1))
    def test_singleton(self, x, c, no_m, c_m):
        assume(0 <= no_m < c_m <= 1)
        f = fun.singleton(c, no_m=no_m, c_m=c_m)
        assert f(x) == (c_m if x == c else no_m)
    
    
    @given(st.floats(allow_nan=False, allow_infinity=False),
          st.floats(allow_nan=False, allow_infinity=False),
          st.floats(allow_nan=False, allow_infinity=False))
    def test_linear(self, x, m, b):
        f = fun.linear(m, b)
        assert (0 <= f(x) <= 1)
        
    @given(st.floats(allow_nan=False),
      st.floats(allow_nan=False, allow_infinity=False),
      st.floats(allow_nan=False, allow_infinity=False),
      st.floats(min_value=0, max_value=1),
      st.floats(min_value=0, max_value=1))
    def test_bounded_linear(self, x, low, high, c_m, no_m):
        assume(low < high)
        assume(c_m > no_m)
        f = fun.bounded_linear(low, high, c_m=c_m, no_m=no_m)
        assert (0 <= f(x) <= 1)

    @given(st.floats(allow_nan=False),
            st.floats(allow_nan=False, allow_infinity=False),
            st.floats(allow_nan=False, allow_infinity=False))
    def test_R(self, x, low, high):
        assume(low < high)
        f = fun.R(low, high)
        assert (0 <= f(x) <= 1)
        
    @given(st.floats(allow_nan=False),
        st.floats(allow_nan=False, allow_infinity=False),
        st.floats(allow_nan=False, allow_infinity=False))
    def test_S(self, x, low, high):
        assume(low < high)
        f = fun.S(low, high)
        assert (0 <= f(x) <= 1)
        
    @given(st.floats(allow_nan=False),
      st.floats(allow_nan=False, allow_infinity=False),
      st.floats(allow_nan=False, allow_infinity=False),
      st.floats(min_value=0, max_value=1),
      st.floats(min_value=0, max_value=1))
    def test_rectangular(self, x, low, high, c_m, no_m):
        assume(low < high)
        f = fun.rectangular(low, high, c_m=c_m, no_m=no_m)
        assert (0 <= f(x) <= 1)
        
    @given(st.floats(allow_nan=False),
      st.floats(allow_nan=False, allow_infinity=False),
      st.floats(allow_nan=False, allow_infinity=False),
      st.floats(allow_nan=False, allow_infinity=False),
      st.floats(min_value=0, max_value=1),
      st.floats(min_value=0, max_value=1))
    def test_triangular(self, x, low, high, c, c_m, no_m):
        assume(low < c < high)
        assume(no_m < c_m)
        f = fun.triangular(low, high, c=c, c_m=c_m, no_m=no_m)
        assert (0 <= f(x) <= 1)
        
    @given(st.floats(allow_nan=False),
      st.floats(allow_nan=False, allow_infinity=False),
      st.floats(allow_nan=False, allow_infinity=False),
      st.floats(allow_nan=False, allow_infinity=False),
      st.floats(allow_nan=False, allow_infinity=False),
      st.floats(min_value=0, max_value=1),
      st.floats(min_value=0, max_value=1))
    def test_trapezoid(self, x, low, c_low, c_high, high, c_m, no_m):
        assume(low < c_low <= c_high < high)
        assume(no_m < c_m)
        f = fun.trapezoid(low, c_low, c_high, high, c_m=c_m, no_m=no_m)
        assert (0 <= f(x) <= 1)
        
    @given(st.floats(allow_nan=False),
      st.floats(min_value=0, max_value=1),
      st.floats(allow_nan=False, allow_infinity=False),
      st.floats(min_value=0, max_value=1))
    def test_sigmoid(self, x, L, k, x0):
        assume(0 < L <= 1)
        f = fun.sigmoid(L, k, x0)
        assert (0 <= f(x) <= 1)

    @given(st.floats(allow_nan=False),
      st.floats(allow_nan=False, allow_infinity=False),
      st.floats(allow_nan=False, allow_infinity=False))
    def test_bounded_sigmoid(self, x, low, high):
        assume(low < high)
        f = fun.bounded_sigmoid(low, high)
        assert (0 <= f(x) <= 1)
    
    @given(st.floats(allow_nan=False),
      st.floats(allow_nan=False, allow_infinity=False))
    def test_simple_sigmoid(self, x, k):
        f = fun.simple_sigmoid(k)
        assert (0 <= f(x) <= 1)
        
    @given(st.floats(allow_nan=False),
      st.floats(allow_nan=False, allow_infinity=False),
      st.floats(allow_nan=False, allow_infinity=False),
      st.floats(allow_nan=False, allow_infinity=False))
    def test_triangular_sigmoid(self, x, low, high, c):
        assume(low < c < high)
        f = fun.triangular(low, high, c=c)
        assert (0 <= f(x) <= 1)
    
    @given(st.floats(allow_nan=False),
      st.floats(allow_nan=False, allow_infinity=False),
      st.floats(allow_nan=False, allow_infinity=False),
      st.floats(min_value=0, max_value=1))
    def test_gauss(self, x, b, c, c_m):
        assume(0 < c_m <= 1)
        assume(0 < b)
        f = fun.gauss(c, b, c_m=c_m)
        assert (0 <= f(x) <= 1)

class Test_Hedges(TestCase):
    @given(st.floats(allow_nan=False))
    def test_very(self, x):
        assume(0 <= x <= 1)
        s = Set(fun.noop())
        h = hedges.very(s)
        assert (0 <= h(x) <= 1)

    @given(st.floats(allow_nan=False))
    def test_minus(self, x):
        assume(0 <= x <= 1)
        s = Set(fun.noop())
        h = hedges.minus(s)
        assert (0 <= h(x) <= 1)
        
    @given(st.floats(allow_nan=False))
    def test_plus(self, x):
        assume(0 <= x <= 1)
        s = Set(fun.noop())
        h = hedges.plus(s)
        assert (0 <= h(x) <= 1)