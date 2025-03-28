from __future__ import annotations

import math

import numpy as np
import pytest
from hypothesis import given
from hypothesis import strategies as st

from fuzzylogic.classes import Domain
from fuzzylogic.functions import singleton

# ---------------------------------------------------------------------------
# Basic Unit Tests
# ---------------------------------------------------------------------------


def test_singleton_membership():
    """Test that a singleton returns 1.0 exactly at its specified location and 0 elsewhere."""
    s = singleton(500)
    # Exact hit yields 1.0
    assert s(500) == 1.0
    # Any other value yields 0.0
    assert s(499.999) == 0.0
    assert s(500.1) == 0.0


def test_singleton_center_of_gravity():
    """Test that the center_of_gravity always returns the singleton’s location."""
    for c in [0, 250, 500, 750, 1000]:
        s = singleton(c)
        assert s.center_of_gravity() == c, f"Expected COG {c}, got {s.center_of_gravity()}"


# ---------------------------------------------------------------------------
# Domain Integration Tests
# ---------------------------------------------------------------------------


def test_singleton_with_domain():
    """
    Test that a SingletonSet assigned to a domain yields the expected membership
    array, containing a spike at the correct position.
    """
    D = Domain("D", 0, 1000)
    s = singleton(500)
    s.domain = D

    arr = s.array()
    points = D.range

    assert 500 in points, "Domain should contain 500 exactly."
    idx = points[500]

    np.testing.assert_almost_equal(arr[idx], 1.0)
    np.testing.assert_almost_equal(arr.sum(), 1.0)


@given(c=st.integers(min_value=0, max_value=1000))
def test_singleton_property_center(c: int):
    """
    Property-based test: For any integer c in [0, 1000], a singleton defined at c
    (and assigned to an appropriately discretized Domain) has a center-of-gravity equal to c.
    """
    D = Domain("D", 0, 1000)
    s = singleton(c)
    s.domain = D
    assert s.center_of_gravity() == c


# ---------------------------------------------------------------------------
# Fuzzy Operation Integration Tests
# ---------------------------------------------------------------------------


def test_singleton_union():
    """
    Test that the fuzzy union (OR) of two disjoint singleton sets creates a fuzzy set
    containing two spikes – one at each singleton location.
    """
    D = Domain("D", 0, 1000)
    s1 = singleton(500)
    s2 = singleton(600)
    s1.domain = D
    s2.domain = D

    union_set = s1 | s2
    union_set.domain = D

    arr = union_set.array()
    points = D.range

    assert 500 in points and 600 in points
    idx_500 = points[500]
    idx_600 = points[600]
    np.testing.assert_almost_equal(arr[idx_500], 1.0)
    np.testing.assert_almost_equal(arr[idx_600], 1.0)

    np.testing.assert_almost_equal(arr.sum(), 2.0)


# ---------------------------------------------------------------------------
# Differential / Regression Testing with Defuzzification
# ---------------------------------------------------------------------------


def test_singleton_defuzzification():
    """
    Test that when a singleton is used in defuzzification (via center_of_gravity),
    the exact spike value is returned regardless of discrete sampling issues.
    """
    s = singleton(500.1)
    assert math.isclose(s.center_of_gravity(), 500.1, rel_tol=1e-9)


# ---------------------------------------------------------------------------
# Performance
# ---------------------------------------------------------------------------


def test_singleton_performance():
    """
    A basic performance test to ensure that evaluating a singleton over a large domain
    remains efficient.
    """
    D = Domain("D", 0, 1000, res=0.0001)  # A large domain
    D.s = singleton(500)
    time_taken = pytest.importorskip("timeit").timeit(lambda: D.s.array(), number=10)
    assert time_taken < 1, "Performance slowed down unexpectedly."


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
