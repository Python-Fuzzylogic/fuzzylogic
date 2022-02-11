import io
from itertools import product

import pandas as pd

table = """
            hum.dry             hum.wet
temp.cold   very(motor.slow)    motor.slow
temp.hot    motor.fast          very(motor.fast)
"""

references = globals()

df = pd.read_table(io.StringIO(table), delim_whitespace=True)
D = {}

for x, y in product(range(len(df.index)), range(len(df.columns))):
    D[(eval(df.index[x].strip(), references),
       eval(df.columns[y].strip(), references))] = eval(
        df.iloc[x, y], references
     )
    

