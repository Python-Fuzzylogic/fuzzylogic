import numpy as np

from fuzzylogic.classes import Domain, Rule, rule_from_table
from fuzzylogic.functions import R, S, trapezoid

temp = Domain("Temperatur", -30, 100, res=0.0001)  # ,res=0.1)
temp.kalt = S(-10, 30)
temp.heiß = R(30, 70)
temp.mittel = ~temp.heiß & ~temp.kalt


tan = Domain("tandelta", 0, 1.3, res=0.0001)  # ,res=0.1)
tan.klein = S(0.1, 0.5)
tan.groß = R(0.5, 0.9)
tan.mittel = ~tan.groß & ~tan.klein

gef = Domain("Gefahrenbewertung", -0.5, 1.5, res=0.0001)  # ,res=0.1)
gef.klein = trapezoid(-0.5, 0, 0, 0.5)
gef.groß = trapezoid(0.5, 1, 1, 1.5)
gef.mittel = trapezoid(0, 0.5, 0.5, 1)

R1 = Rule({(temp.kalt, tan.klein): gef.klein})
R2 = Rule({(temp.mittel, tan.klein): gef.klein})
R3 = Rule({(temp.heiß, tan.klein): gef.klein})
R4 = Rule({(temp.kalt, tan.mittel): gef.klein})
R5 = Rule({(temp.mittel, tan.mittel): gef.mittel})
R6 = Rule({(temp.heiß, tan.mittel): gef.groß})
R7 = Rule({(temp.kalt, tan.groß): gef.mittel})
R8 = Rule({(temp.mittel, tan.groß): gef.groß})
R9 = Rule({(temp.heiß, tan.groß): gef.groß})


rules = R1 | R2 | R3 | R4 | R5 | R6 | R7 | R8 | R9

table = """
            tan.klein	tan.mittel	tan.groß
temp.kalt	gef.klein	gef.klein	gef.mittel
temp.mittel	gef.klein	gef.mittel	gef.groß
temp.heiß	gef.klein	gef.groß	gef.groß
"""


table_rules = rule_from_table(table, globals())

assert table_rules == rules

value = {temp: 20, tan: 0.55}
result = rules(value)
assert isinstance(result, float)
assert np.isclose(result, 0.45, atol=0.0001)

"""
For the input {temp: 20, tan: 0.55}:
* temp: 20 activates:
    temp.mittel (membership = 0.75)
    temp.kalt (membership = 0.25)

* tan: 0.55 activates:
    tan.mittel (membership = 0.875)
    tan.groß (membership = 0.125)

This triggers four rules:

* R4: (temp.kalt, tan.mittel) → gef.klein (firing strength = min(0.25, 0.875) = 0.25)
* R5: (temp.mittel, tan.mittel) → gef.mittel (firing strength = 0.75)
* R7: (temp.kalt, tan.groß) → gef.mittel (firing strength = min(0.25, 0.125) = 0.125)
* R8: (temp.mittel, tan.groß) → gef.groß (firing strength = 0.125)


|------------------|------------------|------------------|
| Rule              | Consequent       | Weight           | Consequent CoG   |
|------------------|------------------|------------------|
|R4|gef.klein|	0.25|	0.0 (midpoint of [-0.5, 0.5])
|R5|gef.mittel|	0.75|	0.5 (midpoint of [0, 1])
|R7|gef.mittel|	0.125|	0.5
|R8|gef.groß|	0.125|	1.0 (midpoint of [0.5, 1.5])

COG = (0.25 * 0.0 + 0.75 * 0.5 + 0.125 * 0.5 + 0.125 * 1.0) / (0.25 + 0.75 + 0.125 + 0.125)
    = 0.5625/1.25
    = 0.45
"""
