
def scale(x, *, IN_min=0, IN_max=1, OUT_min, OUT_max):
    return (OUT_max - OUT_min)*(x - IN_min) / (IN_max - IN_min) + OUT_min