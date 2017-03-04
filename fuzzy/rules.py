
from math import isinf

def scale(OUT_min, OUT_max, *, IN_min=0, IN_max=1):
    """Scale from one domain to another.
    
    Works best for [0,1] -> R. For R -> R additional testing is required.
    """
    assert IN_min < IN_max
    # this is not arbitrary. lim x -> inf x*0+x -> inf
    if isinf(OUT_max - OUT_min):
        return lambda x: OUT_max
    
    def f(x):
        return (OUT_max - OUT_min)*(x - IN_min) / (IN_max - IN_min) + OUT_min
    return f