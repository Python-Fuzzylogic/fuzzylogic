from math import isclose
from typing import cast
from unittest import TestCase

import numpy as np
from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st

from fuzzylogic import combinators as combi
from fuzzylogic import functions as fun
from fuzzylogic import hedges, truth
from fuzzylogic import tools as ru
from fuzzylogic.classes import Domain, Set

version = (0, 1, 1, 4)

# Common settings for all tests
common_settings = settings(deadline=None, suppress_health_check=cast(list[HealthCheck], list(HealthCheck)))


class TestFunctions(TestCase):
    @common_settings
    @given(st.floats(allow_nan=False))
    def test_noop(self, x: float) -> None:
        f = fun.noop()
        assert f(x) == x

    @common_settings
    @given(st.floats(allow_nan=False, allow_infinity=False))
    def test_inv(self, x: float) -> None:
        assume(0 <= x <= 1)
        f = fun.inv(fun.noop())
        assert isclose(f(f(x)), x, abs_tol=1e-16)

    @common_settings
    @given(st.floats(allow_nan=False, allow_infinity=False), st.floats(allow_nan=False, allow_infinity=False))
    def test_constant(self, x: float, c: float) -> None:
        f = fun.constant(c)
        assert f(x) == c

    @common_settings
    @given(
        st.floats(allow_nan=False), st.floats(min_value=0, max_value=1), st.floats(min_value=0, max_value=1)
    )
    def test_alpha(self, x: float, lower: float, upper: float) -> None:
        assume(lower < upper)
        f = fun.alpha(floor=lower, ceiling=upper, func=fun.noop())
        if x <= lower:
            assert f(x) == lower
        elif x >= upper:
            assert f(x) == upper
        else:
            assert f(x) == x

    @common_settings
    @given(
        st.floats(allow_nan=False),
        st.floats(min_value=0, max_value=1),
        st.floats(min_value=0, max_value=1),
        st.floats(min_value=0, max_value=1) | st.none(),
        st.floats(min_value=0, max_value=1) | st.none(),
    )
    def test_alpha_2(
        self, x: float, floor: float, ceil: float, floor_clip: float | None, ceil_clip: float | None
    ) -> None:
        assume(floor < ceil)
        if floor_clip is not None and ceil_clip is not None:
            assume(floor_clip < ceil_clip)
        f = fun.alpha(
            floor=floor, ceiling=ceil, func=fun.noop(), floor_clip=floor_clip, ceiling_clip=ceil_clip
        )
        assert 0 <= f(x) <= 1

    @common_settings
    @given(st.floats(allow_nan=False), st.floats(min_value=0, max_value=1))
    def test_normalize(self, x: float, height: float) -> None:
        assume(height > 0)
        f = fun.normalize(height, fun.alpha(ceiling=height, func=fun.R(0, 100)))
        assert 0 <= f(x) <= 1

    @common_settings
    @given(st.floats(min_value=0, max_value=1))
    def test_moderate(self, x: float) -> None:
        f = fun.moderate(fun.noop())
        assert 0 <= f(x) <= 1

    @common_settings
    @given(st.floats(), st.floats(), st.floats(min_value=0, max_value=1), st.floats(min_value=0, max_value=1))
    def test_singleton(self, x: float, c: float, no_m: float, c_m: float) -> None:
        assume(0 <= no_m < c_m <= 1)
        f = fun.singleton(c, no_m=no_m, c_m=c_m)
        assert f(x) == (c_m if x == c else no_m)

    @common_settings
    @given(
        st.floats(allow_nan=False, allow_infinity=False),
        st.floats(allow_nan=False, allow_infinity=False),
        st.floats(allow_nan=False, allow_infinity=False),
    )
    def test_linear(self, x: float, m: float, b: float) -> None:
        f = fun.linear(m, b)
        assert 0 <= f(x) <= 1

    @common_settings
    @given(
        st.floats(allow_nan=False),
        st.floats(allow_nan=False, allow_infinity=False),
        st.floats(allow_nan=False, allow_infinity=False),
        st.floats(min_value=0, max_value=1),
        st.floats(min_value=0, max_value=1),
    )
    def test_bounded_linear(self, x: float, low: float, high: float, c_m: float, no_m: float) -> None:
        assume(low < high)
        assume(c_m > no_m)
        f = fun.bounded_linear(low, high, c_m=c_m, no_m=no_m)
        assert 0 <= f(x) <= 1

    @common_settings
    @given(
        st.floats(allow_nan=False, allow_infinity=False),
        st.floats(allow_nan=False, allow_infinity=False),
        st.floats(allow_nan=False, allow_infinity=False),
    )
    def test_R(self, x: float, low: float, high: float) -> None:
        assume(low < high)
        f = fun.R(low, high)
        assert 0 <= f(x) <= 1

    @common_settings
    @given(
        st.floats(allow_nan=False, allow_infinity=False),
        st.floats(allow_nan=False, allow_infinity=False),
        st.floats(allow_nan=False, allow_infinity=False),
    )
    def test_S(self, x: float, low: float, high: float) -> None:
        assume(low < high)
        f = fun.S(low, high)
        assert 0 <= f(x) <= 1

    @common_settings
    @given(
        st.floats(allow_nan=False),
        st.floats(allow_nan=False, allow_infinity=False),
        st.floats(allow_nan=False, allow_infinity=False),
        st.floats(min_value=0, max_value=1),
        st.floats(min_value=0, max_value=1),
    )
    def test_rectangular(self, x: float, low: float, high: float, c_m: float, no_m: float) -> None:
        assume(low < high)
        f = fun.rectangular(low, high, c_m=c_m, no_m=no_m)
        assert 0 <= f(x) <= 1

    @common_settings
    @given(
        st.floats(allow_nan=False),
        st.floats(allow_nan=False, allow_infinity=False),
        st.floats(allow_nan=False, allow_infinity=False),
        st.floats(allow_nan=False, allow_infinity=False),
        st.floats(min_value=0, max_value=1),
        st.floats(min_value=0, max_value=1),
    )
    def test_triangular(self, x: float, low: float, high: float, c: float, c_m: float, no_m: float) -> None:
        assume(low < c < high)
        assume(no_m < c_m)
        f = fun.triangular(low, high, c=c, c_m=c_m, no_m=no_m)
        assert 0 <= f(x) <= 1

    @common_settings
    @given(
        st.floats(allow_nan=False),
        st.floats(allow_nan=False, allow_infinity=False),
        st.floats(allow_nan=False, allow_infinity=False),
        st.floats(allow_nan=False, allow_infinity=False),
        st.floats(allow_nan=False, allow_infinity=False),
        st.floats(min_value=0, max_value=1),
        st.floats(min_value=0, max_value=1),
    )
    def test_trapezoid(
        self, x: float, low: float, c_low: float, c_high: float, high: float, c_m: float, no_m: float
    ) -> None:
        assume(low < c_low <= c_high < high)
        assume(no_m < c_m)
        f = fun.trapezoid(low, c_low, c_high, high, c_m=c_m, no_m=no_m)
        assert 0 <= f(x) <= 1

    @common_settings
    @given(
        st.floats(allow_nan=False),
        st.floats(min_value=0, max_value=1),
        st.floats(allow_nan=False, allow_infinity=False),
        st.floats(min_value=0, max_value=1),
    )
    def test_sigmoid(self, x: float, L: float, k: float, x0: float) -> None:
        assume(0 < L <= 1)
        f = fun.sigmoid(L, k, x0)
        assert 0 <= f(x) <= 1

    @common_settings
    @given(
        st.floats(allow_nan=False),
        st.floats(allow_nan=False, allow_infinity=False),
        st.floats(allow_nan=False, allow_infinity=False),
    )
    def test_bounded_sigmoid(self, x: float, low: float, high: float) -> None:
        assume(low < high)
        f = fun.bounded_sigmoid(low, high)
        assert 0 <= f(x) <= 1

    @common_settings
    @given(st.floats(allow_nan=False), st.floats(allow_nan=False, allow_infinity=False))
    def test_simple_sigmoid(self, x: float, k: float) -> None:
        f = fun.simple_sigmoid(k)
        assert 0 <= f(x) <= 1

    @common_settings
    @given(
        st.floats(allow_nan=False),
        st.floats(allow_nan=False, allow_infinity=False),
        st.floats(allow_nan=False, allow_infinity=False),
        st.floats(allow_nan=False, allow_infinity=False),
    )
    def test_triangular_sigmoid(self, x: float, low: float, high: float, c: float) -> None:
        assume(low < c < high)
        f = fun.triangular(low, high, c=c)
        assert 0 <= f(x) <= 1

    @common_settings
    @given(
        st.floats(allow_nan=False),
        st.floats(allow_nan=False, allow_infinity=False),
        st.floats(allow_nan=False, allow_infinity=False),
        st.floats(min_value=0, max_value=1),
    )
    def test_gauss(self, x: float, b: float, c: float, c_m: float) -> None:
        assume(b > 0)
        assume(c_m > 0)
        f = fun.gauss(c, b, c_m=c_m)
        assert 0 <= f(x) <= 1

    @common_settings
    @given(
        st.floats(allow_nan=False, min_value=0, allow_infinity=False),
        st.floats(allow_nan=False, min_value=0, allow_infinity=False),
        st.floats(allow_nan=False, min_value=0),
    )
    def test_bounded_exponential(self, k: float, limit: float, x: float) -> None:
        assume(k != 0)
        assume(limit != 0)
        f = fun.bounded_exponential(k, limit)
        assert 0 <= f(x) <= limit


class TestHedges(TestCase):
    @common_settings
    @given(st.floats(min_value=0, max_value=1))
    def test_very(self, x: float) -> None:
        s = Set(fun.noop())
        f = hedges.very(s)
        assert 0 <= f(x) <= 1

    @common_settings
    @given(st.floats(min_value=0, max_value=1))
    def test_minus(self, x: float) -> None:
        s = Set(fun.noop())
        f = hedges.minus(s)
        assert 0 <= f(x) <= 1

    @common_settings
    @given(st.floats(min_value=0, max_value=1))
    def test_plus(self, x: float) -> None:
        s = Set(fun.noop())
        f = hedges.plus(s)
        assert 0 <= f(x) <= 1


class TestCombinators(TestCase):
    @common_settings
    @given(st.floats(min_value=0, max_value=1))
    def test_MIN(self, x: float) -> None:
        a = fun.noop()
        b = fun.noop()
        f = combi.MIN(a, b)
        assert 0 <= f(x) <= 1

    @common_settings
    @given(st.floats(min_value=0, max_value=1))
    def test_MAX(self, x: float) -> None:
        a = fun.noop()
        b = fun.noop()
        f = combi.MAX(a, b)
        assert 0 <= f(x) <= 1

    @common_settings
    @given(st.floats(min_value=0, max_value=1))
    def test_product(self, x: float) -> None:
        a = fun.noop()
        b = fun.noop()
        f = combi.product(a, b)
        assert 0 <= f(x) <= 1

    @common_settings
    @given(st.floats(min_value=0, max_value=1))
    def test_bounded_sum(self, x: float) -> None:
        a = fun.noop()
        b = fun.noop()
        f = combi.bounded_sum(a, b)
        assert 0 <= f(x) <= 1

    @common_settings
    @given(st.floats(min_value=0, max_value=1))
    def test_lukasiewicz_AND(self, x: float) -> None:
        a = fun.noop()
        b = fun.noop()
        f = combi.lukasiewicz_AND(a, b)
        assert 0 <= f(x) <= 1

    @common_settings
    @given(st.floats(min_value=0, max_value=1))
    def test_lukasiewicz_OR(self, x: float) -> None:
        a = fun.noop()
        b = fun.noop()
        f = combi.lukasiewicz_OR(a, b)
        assert 0 <= f(x) <= 1

    @common_settings
    @given(st.floats(min_value=0, max_value=1))
    def test_einstein_product(self, x: float) -> None:
        a = fun.noop()
        b = fun.noop()
        f = combi.einstein_product(a, b)
        assert 0 <= f(x) <= 1

    @common_settings
    @given(st.floats(min_value=0, max_value=1))
    def test_einstein_sum(self, x: float) -> None:
        a = fun.noop()
        b = fun.noop()
        f = combi.einstein_sum(a, b)
        assert 0 <= f(x) <= 1

    @common_settings
    @given(st.floats(min_value=0, max_value=1))
    def test_hamacher_product(self, x: float) -> None:
        a = fun.noop()
        b = fun.noop()
        f = combi.hamacher_product(a, b)
        assert 0 <= f(x) <= 1

    @common_settings
    @given(st.floats(min_value=0, max_value=1))
    def test_hamacher_sum(self, x: float) -> None:
        a = fun.noop()
        b = fun.noop()
        f = combi.hamacher_sum(a, b)
        assert 0 <= f(x) <= 1

    @common_settings
    @given(st.floats(min_value=0, max_value=1), st.floats(min_value=0, max_value=1))
    def test_lambda_op(self, x: float, lambda_: float) -> None:
        a = fun.noop()
        b = fun.noop()
        g = combi.lambda_op(lambda_)
        f = g(a, b)
        assert 0 <= f(x) <= 1

    @common_settings
    @given(st.floats(min_value=0, max_value=1), st.floats(min_value=0, max_value=1))
    def test_gamma_op(self, x: float, g: float) -> None:
        a = fun.noop()
        b = fun.noop()
        G = combi.gamma_op(g)
        f = G(a, b)
        assert 0 <= f(x) <= 1

    @common_settings
    @given(st.floats(min_value=0, max_value=1))
    def test_simple_disjoint_sum(self, x: float) -> None:
        a = fun.noop()
        b = fun.noop()
        f = combi.simple_disjoint_sum(a, b)
        assert 0 <= f(x) <= 1


class TestDomain(TestCase):
    def test_basics(self) -> None:
        D = Domain("d", 0, 10)
        assert D._name == "d"  # type: ignore
        assert D._low == 0  # type: ignore
        assert D._high == 10  # type: ignore
        assert D._res == 1  # type: ignore
        x = Set(lambda x: 1)
        D.s = x
        assert D.s == x
        assert D._sets == {"s": x}  # type: ignore
        R = D(3)
        assert R == {D.s: 1}
        # repr is hard - need to repr sets first :/
        # D = eval(repr(d))
        # assert d == D


class TestSet(TestCase):
    @common_settings
    @given(
        st.floats(allow_nan=False, allow_infinity=False),
        st.floats(allow_nan=False, allow_infinity=False),
        st.floats(min_value=0.0001, max_value=1),
    )
    def test_eq(self, low: float, high: float, res: float) -> None:
        """This also tests Set.array().
        This test can massively slow down hypothesis with even
        reasonably large/small values.
        """
        assume(low < high)
        # to avoid MemoryError and runs that take forever..
        assume(high - low <= 10)
        D1 = Domain("a", low, high, res=res)
        D1.s1 = fun.bounded_linear(low, high)
        D2 = Domain("b", low, high, res=res)
        D2.s2 = Set(fun.bounded_linear(low, high))
        assert D1.s1 == D2.s2

    def test_normalized(self) -> None:
        D = Domain("d", 0, 10, res=0.1)
        D.s = Set(fun.bounded_linear(3, 12))
        D.x = D.s.normalized()
        D.y = D.x.normalized()
        assert D.x == D.y

    def test_sub_super_set(self) -> None:
        D = Domain("d", 0, 10, res=0.1)
        D.s = Set(fun.bounded_linear(3, 12))
        D.x = D.s.normalized()
        assert D.x >= D.s
        assert D.s <= D.x

    def test_complement(self) -> None:
        D = Domain("d", 0, 10, res=0.1)
        D.s1 = Set(fun.bounded_linear(3, 12))
        D.s2 = ~~D.s1
        assert all(np.isclose(D.s1.array(), D.s2.array()))


class TestRules(TestCase):
    @common_settings
    @given(
        st.floats(min_value=0, max_value=1),
        st.floats(allow_infinity=False, allow_nan=False),
        st.floats(allow_infinity=False, allow_nan=False),
        st.floats(min_value=0, max_value=1),
        st.floats(min_value=0, max_value=1),
    )
    def test_rescale(self, x: float, out_min: float, out_max: float, in_min: float, in_max: float) -> None:
        assume(in_min < in_max)
        assume(in_min <= x <= in_max)
        assume(out_min < out_max)
        f = ru.rescale(out_min, out_max)
        assert out_min <= f(x) <= out_max

    @given(st.floats(allow_nan=False), st.floats(allow_nan=False))
    def round_partial(self, x: float, res: float) -> None:
        assert isclose(x, ru.round_partial(x, res))


class TestTruth(TestCase):
    @common_settings
    @given(st.floats(min_value=0, max_value=1))
    def test_true_and_false(self, m: float) -> None:
        assert truth.true(m) + truth.false(m) == 1

    @common_settings
    @given(st.floats(min_value=0, max_value=1))
    def test_very_false_and_fairly_true(self, m: float) -> None:
        assert truth.very_false(m) + truth.fairly_true(m) == 0

    @common_settings
    @given(st.floats(min_value=0, max_value=1))
    def test_fairly_false_and_very_true(self, m: float) -> None:
        assert truth.fairly_false(m) + truth.very_true(m) == 0
