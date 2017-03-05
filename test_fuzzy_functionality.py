
"""
Functional test of the fuzzylogic lib 'fuzzy'.
"""

from unittest import TestCase, skip

from fuzzy.classes import Domain, Set
from fuzzy.rules import scale
from fuzzy.functions import R, S, bounded_linear

class TestTop(TestCase):
    def setUp(self):
        """Lucy tells her robot that it is good to heat when it's cold and not when it's hot."""
        self.temp = Domain('temperature', -100, 100)  # in Celsius
        self.temp.cold = Set(S(0, 15))
        self.temp.hot = Set(R(10, 30))
        self.temp.warm = ~self.temp.cold & ~self.temp.hot

    def test_temp(self):
        assert(self.temp(6) == {'cold': 0.6, 'hot': 0, 'warm': 0.4})

class Test_Meal(TestCase):
    def setUp(self):
        """Tom is surveying restaurants. 
        He doesn't need fancy logic but rather uses a simple approach with weights.
        He went into a small, dirty bar that served some delicious drink and food.
        """
        self.R = Domain("rating", 1, 10, res=0.1)
        self.R.norm = Set(bounded_linear(1, 10))
        self.weights = weights = {"beverage": 0.3, 
                                  "atmosphere": 0.2, 
                                   "arrangement":0.2,
                                   "taste": 0.3}
        self.ratings = {"beverage": self.R.MIN(7),
                       "atmosphere": self.R.MIN(3),
                       "arrangement": self.R.MIN(2),
                       "taste": self.R.MIN(9)}
    
if __name__ == '__main__':
    unittest.main()