
"""
Fuzzy Logic for Python 3.

Usage:
1) Define a Domain and specify the measurable range & resolution.
2) Define some fuzzysets ("adjectives") as attributes that describe ranges within
the domain using Set().
3) You can combine fuzzysets using fuzzy logic operators (~, &, |, +, *) to
define derived fuzzysets.
4) Now suppose you have a value x. Call the fuzzyset(x) directly to produce a
membership value or
call the domain with it to get a dictionary of memberships.
5) To really put these to work, you will want to map membership values of one or
more domains onto another domain, producing "real world" values again that can
be used to control things. This is called inference (combining domains) and
defuzzification (turning membership values back into measurables).
"""

import matplotlib.pyplot as plt
from numpy import arange

from functions import inv
from combinators import MAX, MIN, product, bounded_sum



class Domain:
    """
    A domain is a 'measurable' dimension of 'real' values like temperature.

    There must be a lower and upper limit and a resolution (the size of steps)
    specified.

    Fuzzysets are defined within one such domain and are only meaningful
    while considered within their domain ('apples and bananas').
    To operate with sets across domains, there needs to be a mapping.

    The sets are accessed as attributes of the domain like
    >>> temp = Domain('temperature', 0, 100)
    >>> temp.hot = Set(temp, lambda x: 0)     # functions.constant
    >>> temp.hot(5)
    0

    DO NOT call a derived set without assignment first as it WILL
    confuse the recursion and seriously mess up.
    >>> not_hot = ~temp.hot
    >>> not_hot(2)
    1

    You MUST NOT add arbitrary attributes to an *instance* of Domain - you can
    however subclass or modify the class itself, which affects its instances:
    >>> d = Domain('d', 0, 100)
    >>> Domain.x = 78
    >>> d.x
    78

    Use the Domain by calling it with the value in question. This returns a
    dictionary with the degrees of membership per set. You MAY override __call__
    in a subclass to enable concurrent evaluation for performance improvement.
    >>> temp.cold = ~temp.hot
    
    # >>> result = temp(3)
    # >>> {'temperature.hot': 0, 'temperature.cold': 1} == result
    # True
    """
    _sets = set()

    def __init__(self, name, low, high, res=1):
        if high < low:
            raise AttributeError("higher bound must not be less than lower.")
        self.name = name
        self.high = high
        self.low = low
        self.res = res

    
    def __call__(self, x):
        return NotImplemented
    # self._sets isn't properly defined
        set_memberships = {}
        for setname, s in self._sets.items():
            set_memberships["{0}.{1}".format(self.name, setname)] = s(x)
        return set_memberships

    def __str__(self):
        return "Domain(%s)" % self.name

    def __getattr__(self, name):
        if name in self._sets:
            return self._sets[name]
        else:
            raise AttributeError("not a set and not an attribute")

"""
    def __setattr__(self, name, value):
        # it's a domain attr
        if name in ['name', 'low', 'high', 'res', '_sets']:
            object.__setattr__(self, name, value)
        # we've got a fuzzyset within this domain and the value is a func
        else:
            if not isinstance(value, Set):
                raise ValueError("only a fuzzy.Set may be assigned.")
            self._sets[name] = value
            value.domain = self
"""

class Set:
    """
    A fuzzyset defines a 'region' within a domain.
    The associated membership function defines 'how much' a given value is
    inside this region - how 'true' the value is.
    A set is identified by the name and attribute of its domain,
    therefor there is no need for an extra identifier.

    Sets and functions MUST NOT be mixed because functions don't have
    the methods of the sets needed for the logic.

    The combination operations SHOULD only be applied with sets of the same
    domain as ranges may not overlap and thus give unexpected results,
    however it is possible to reuse the set under different names because
    it is simply a function that may mean different things under different
    domains, yet have the same graph (like 'cold' could use the same function
    as 'dry' or 'close' if the ranges are the same.)

    Sets that are returned from one of the operations are 'derived sets' or
    'Superfuzzysets' according to Zadeh.
    """
    def __init__(self, domain:Domain, func:callable, ops:dict=None):
        self.func = func
        assert self.func is not None
        self.ops = ops
        if not isinstance(domain, Domain):
            raise AttributeError
        self.domain = domain
        self.domain._sets.add(self)

    def __call__(self, x):
        return self.func(x)

    def __invert__(self):
        return Set(self.domain, inv(self.func))

    def __and__(self, other):
        if self.domain is not other.domain:
            raise UserWarning
        return Set(self.domain, MIN(self.func, other.func))

    def __or__(self, other):
        if self.domain is not other.domain:
            raise UserWarning
        return Set(self.domain, MAX(self.func, other.func))

    def __mul__(self, other):
        if self.domain is not other.domain:
            raise UserWarning
        return Set(self.domain, product(self.func, other.func))

    def __sum__(self, other):
        if self.domain is not other.domain:
            raise UserWarning
        return Set(self.domain, bounded_sum(self.func, other.func))

    def __pow__(self, power):
        """pow is used with lingual hedges as defined in fuzzy.functions"""
        return Set(self.domain, lambda x: pow(self.func(x), power))

    def plot(self, low=None, high=None, res=None):
        """Graph the set.
        Use the bounds and resolution of the domain to display the set
        unless specified otherwise.
        """
        low = self.domain.low if low is None else low
        high = self.domain.high if high is None else high
        res = self.domain.res if res is None else res
        R = arange(low, high, res)
        V = [self.func(x) for x in R]
        #print(R)
        #print(V)
        plt.plot(R, V)


class Rule:
    """
    A rule is used to combine fuzzysets of different domains, aggregating the
    results of the previous calculations.

    It works like this:
    >>> temp = Domain("temperature", 0, 100)
    >>> temp.hot = Set(temp, lambda x: 1)
    >>> dist = Domain("distance", 0, 300)
    >>> dist.close = Set(dist, lambda x: 0)
    
    #>>> r = Rule(min, ["distance.close", "temperature.hot"])
    #>>> d1 = temp(32)   # {'temperature.hot': 1}
    #>>> d2 = dist(5)    # {'distance.close': 0}
    #>>> d = d1.copy()   # need to merge the results of the Domains
    #>>> d.update(d2)    # for py3.5: https://www.python.org/dev/peps/pep-0448/
    #>>> r(d)    # min(1, 0)
    #0

    Calling the domains MAY be done async for better performance, a rule only
    needs the dict with the qualified fuzzysets.
    Two or more rules usually are combined using the max() operation.
    As func anything is valid that maps a list of ( [0,1] ) -> [0,1]

    Rules are often used to control the behaviour of complex systems.
    To do this, the output of a rule MAY be associated with a fuzzyset
    of the domain that is to be controlled.
    For simple applications, the return values are sufficient, so we stick
    with that for now.
    """
    def __init__(self, func, fuzzysets, control=None):
        self.func = func
        self.fuzzysets = set(fuzzysets)  # qualified set names with 'domain.set'
        self.control = control

    def __call__(self, d):
        try:
            return self.func(d[name] for name, value in d.items()
                             if name in self.fuzzysets)
        except TypeError:   # none of the fuzzysets in question returned
            return 0

    def plot(self):
        pass


if __name__ == "__main__":
    import doctest
    doctest.testmod()