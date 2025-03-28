"""
Functional tests of the fuzzylogic library.
"""

import unittest

from numpy import array_equal
from pytest import fixture

from fuzzylogic.classes import Domain, Set
from fuzzylogic.functions import R, S, bounded_linear
from fuzzylogic.tools import weighted_sum


@fixture
def temp() -> Domain:
    d = Domain("temperature", -100, 100, res=0.1)  # in Celsius
    d.cold = S(0, 15)  # sic
    d.hot = Set(R(10, 30))  # sic
    d.warm = ~d.cold & ~d.hot
    return d


@fixture
def simple() -> Domain:
    d = Domain("simple", 0, 10)
    d.low = S(0, 1)
    d.high = R(8, 10)
    return d


def test_array(simple: Domain) -> None:
    assert array_equal(simple.low.array(), [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    assert array_equal(simple.high.array(), [0, 0, 0, 0, 0, 0, 0, 0, 0, 0.5, 1.0])
    assert len(simple.low.array()) == 11  # unlike arrays and lists, upper boundary is INCLUDED


def test_value(temp: Domain) -> None:
    assert temp(6) == {temp.cold: 0.6, temp.hot: 0, temp.warm: 0.4}


def test_rating() -> None:
    """Tom is surveying restaurants.
    He doesn't need fancy logic but rather uses a simple approach
    with weights.
    He went into a small, dirty bar that served some
    really good drink and food that wasn't nicely arranged but still
    yummmy. He rates the different factors on a scale from 1 to 10,
    uses a bounded_linear function to normalize over [0,1] and
    passes both the weights (how much each aspect should weigh in total)
    and the domain as parameters into weighted_sum.
    However, he can't just use Domain(value) because that would return
    a dict of memberships, instead he uses Domain.min(value) which
    returns the minimum of all memberships no matter how many sets
    there are. He creates a dict of membership values corresponding to
    the weights and passes that into the parametrized weighted_sum func
    as argument to get the final rating for this restaurant.
    """
    R = Domain("rating", 1, 10, res=0.1)
    R.norm = bounded_linear(1, 10)
    weights = {"beverage": 0.3, "atmosphere": 0.2, "looks": 0.2, "taste": 0.3}
    w_func = weighted_sum(weights=weights, target_d=R)

    ratings: dict[str, float] = {
        "beverage": R.min(9),
        "atmosphere": R.min(5),
        "looks": R.min(4),
        "taste": R.min(8),
    }
    assert w_func(ratings) == 6.9


if __name__ == "__main__":
    unittest.main()
