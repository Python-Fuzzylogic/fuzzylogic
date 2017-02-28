
"""
Functional test of the fuzzylogic lib 'fuzzy'.
"""

import unittest

from fuzzy.classes import Domain, Set, Rule
from fuzzy.functions import S, R, trapezoid

@unittest.skip("skipping for now..")
class SimpleTest(unittest.TestCase):
    def setUp(self):
        """
        Lucy tells her robot that it is good when it's hot during the day
        and to heat when it's cold more so during the day."""
        self.temp = Domain('temperature', -100, 100, 1)  # in Celsius
        self.temp.cold = Set(R(0, 15))
        self.temp.hot = Set(S(10, 20))

        self.daytime = Domain('time_of_day', 0, 24)  # in 24-hours
        self.daytime.day = Set(trapezoid(5, 7, 21, 23))
        self.daytime.night = ~self.daytime.day

        self.heater = Domain('heater', 0, 3)  # off, a bit, medium, full
        self.heater.power(S(0, 3))

        self.rule = Rule(min, ["temperature.hot", 'daytime.day'],
                         self.heater.power)

    def test_temp(self):
        # we need to define a dictionary-aggregation func here
        self.assertEqual(0, self.rule(-12))
        self.assertEqual(0, self.rule(50))
        self.assertEqual(1, self.rule(20))


if __name__ == '__main__':
    unittest.main()