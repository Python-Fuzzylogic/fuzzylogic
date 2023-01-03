import sys
from pathlib import Path

src = str((Path(__file__).parent / "../src").resolve())
sys.path.insert(0, src)

import numpy as np
from fuzzylogic.classes import Domain, Rule
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

from fuzzylogic.classes import rule_from_table

table_rules = rule_from_table(table, globals())

assert table_rules == rules

value = {temp: 20, tan: 0.55}
result = rules(value)
assert isinstance(result, float)
assert np.isclose(result, 0.45, atol=0.0001)
