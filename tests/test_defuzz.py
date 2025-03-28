from __future__ import annotations

import math
import timeit

import numpy as np
import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from fuzzylogic.defuzz import (
    _get_max_points,
    bisector,
    cog,
    lom,
    mom,
    som,
)
from fuzzylogic.functions import Membership

# ---------------------------------------------------------------------------
# Core Testing Infrastructure
# ---------------------------------------------------------------------------


class DummyDomain:
    """Mock domain for testing fuzzy operations"""

    def __init__(self, low: float, high: float, n_points: int = 101):
        assert low < high, "Invalid domain bounds"
        self._low = low
        self._high = high
        self._n_points = n_points

    @property
    def range(self) -> list[float]:
        return np.linspace(self._low, self._high, self._n_points).tolist()


class DummySet:
    """Mock fuzzy set with configurable properties"""

    def __init__(self, cog_value: float, membership_func: Membership | None = None):
        self._cog = cog_value
        self.membership_func = membership_func or (lambda x: 1.0)
        self.domain = None

    def center_of_gravity(self) -> float:
        return self._cog

    def __call__(self, x: float) -> float:
        return self.membership_func(x)


# ---------------------------------------------------------------------------
# Property-Based Tests
# ---------------------------------------------------------------------------


@given(
    cogs=st.lists(st.floats(min_value=-1e3, max_value=1e3), min_size=1, max_size=10),
    weights=st.lists(st.floats(min_value=0.1, max_value=1e3), min_size=1, max_size=10),
    domain=st.tuples(st.floats(min_value=-1e3), st.floats(min_value=-1e3)).filter(lambda x: x[0] < x[1]),
)
def test_cog_weighted_average_property(cogs: list[float], weights: list[float], domain: tuple[float, float]):
    """Verify COG is proper weighted average of centroids"""
    assume(len(cogs) == len(weights))
    low, high = domain
    domain_obj = DummyDomain(low, high)

    sets = [DummySet(cog) for cog in cogs]
    for s in sets:
        s.domain = domain_obj

    target_weights = list(zip(sets, weights))
    result = cog(target_weights)

    total_weight = sum(weights)
    expected = sum(c * w for c, w in zip(cogs, weights)) / total_weight
    assert math.isclose(result, expected, rel_tol=1e-5, abs_tol=1e-5)


@given(
    peak=st.floats(allow_nan=False, allow_infinity=False),
    width=st.floats(min_value=0.1, max_value=100),
    domain=st.tuples(st.floats(), st.floats()).filter(lambda x: x[0] < x[1]),
)
def test_bisector_triangular_property(peak: float, width: float, domain: tuple[float, float]):
    """Test bisector with generated triangular functions"""
    low, high = domain
    a = peak - width / 2
    b = peak
    c = peak + width / 2
    assume(low <= a < c <= high)

    domain_obj = DummyDomain(low, high)
    points = domain_obj.range
    step = (high - low) / (len(points) - 1)

    from fuzzylogic import functions

    f = functions.triangular(a, c, c=b)

    result = bisector(f, points, step)
    assert math.isclose(result, peak, rel_tol=0.01), f"Expected {peak}, got {result}"


# ---------------------------------------------------------------------------
# Edge Cases
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("dtype, tol", [(np.float32, 1e-6), (np.float64, 1e-12), (np.longdouble, 1e-15)])
def test_cog_precision(dtype, tol):
    """Test numerical precision across data types"""
    domain = DummyDomain(0, 1, 1001)
    exact_val = dtype(0.5)
    fuzzy_set = DummySet(float(exact_val))
    fuzzy_set.domain = domain

    result = cog([(fuzzy_set, 1.0)])
    assert abs(result - exact_val) < tol


# ---------------------------------------------------------------------------
# Performance
# ---------------------------------------------------------------------------


def test_cog_linear_scaling():
    """Verify O(n) time complexity"""
    sizes = [100, 1000, 10000]
    times = []

    # sourcery skip: no-loop-in-tests
    for _ in sizes:
        sets = [DummySet(0.5) for _ in range(10)]
        weights = [(s, 1.0) for s in sets]

        t = timeit.timeit(lambda: cog(weights), number=10)
        times.append(t)

    # Check linear correlation
    log_sizes = np.log(sizes)
    log_times = np.log(times)
    corr = np.corrcoef(log_sizes, log_times)[0, 1]
    assert corr > 0.95, f"Unexpected complexity (corr={corr:.2f})"


# ---------------------------------------------------------------------------
# Core Functionality
# ---------------------------------------------------------------------------


def test_mom_constant_membership():
    """Test MOM with uniform maximum"""
    domain = DummyDomain(0, 10)
    points = domain.range
    result = mom(lambda _: 1.0, points)
    expected = (0 + 10) / 2
    assert math.isclose(result, expected)


def test_som_lom_plateau():
    """Test SOM/LOM with plateaued maximum"""
    domain = DummyDomain(0, 10)
    points = domain.range
    agg_mf = lambda x: 1.0 if 3 <= x <= 7 else 0.0

    assert math.isclose(som(agg_mf, points), 3.0)
    assert math.isclose(lom(agg_mf, points), 7.0)


def test_get_max_points():
    """Test maximum point detection"""
    points = [0, 1, 2, 3, 4]
    agg_mf = lambda x: 1.0 if x == 2 else 0.5
    assert _get_max_points(agg_mf, points) == [2]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--hypothesis-show-statistics"])
