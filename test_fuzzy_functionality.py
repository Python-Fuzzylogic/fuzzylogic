
"""
Functional test of the fuzzylogic lib 'fuzzy'.
"""

import unittest

from fuzzy.classes import Domain, Set, Rule
from fuzzy.functions import R, S

class TestSet(unittest.TestCase):
    def setUp(self):
        """
        Lucy tells her robot that it is good to heat when it's cold and not when it's hot."""
        self.temp = Domain('temperature', -100, 100, 1)  # in Celsius
        self.temp.cold = Set(self.temp, S(0, 15))
        self.temp.hot = Set(self.temp, R(10, 20))

    def test_temp(self):
        # we need to define a dictionary-aggregation func here
        pass


if __name__ == '__main__':
    unittest.main()