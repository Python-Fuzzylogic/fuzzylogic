
"""
Functional test of the fuzzylogic lib 'fuzzy'.
"""

from unittest import TestCase, skip

from fuzzy.classes import Domain, Set
from fuzzy.rules import rescale, weighted_sum
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

class Test_Weighted(TestCase):
    def setUp(self):
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
        self.R = Domain("rating", 1, 10, res=0.1)
        self.R.norm = Set(bounded_linear(1, 10))
        self.weights = {"beverage": 0.3, 
                        "atmosphere": 0.2, 
                        "looks":0.2,
                        "taste": 0.3}
        self.w_func = weighted_sum(weights=self.weights, target=self.R)      
    
    def test_rating(self):
        ratings = {"beverage": self.R.min(9),
                   "atmosphere": self.R.min(5),
                   "looks": self.R.min(4),
                    "taste": self.R.min(8)}
        assert (self.w_func(ratings) == 6.9)
    
if __name__ == '__main__':
    unittest.main()