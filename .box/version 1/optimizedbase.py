
from numpy import arange
from fuzzification import *

from pylab import plot, show


from timeit import Timer
import cProfile



class Domain(object):
    #__slots__ = ['name', 'limits', 'sets', 'resolution']

    sets = {}

    def __init__(self, name, limits=(float('-inf'), float('+inf')), resolution=1.0):
        """
        A domain normally is a single variable in a system that has a
        physical unit and a range of valid values.
        FuzzySets are defined within domains and only meaningful within their limits.

        Dmains (also called 'universes of discourse') can be used as keys in dicts.


        limits
            Tuple with minimum and maximum values, order determines the graph
            for visualisation.
        resolution
            Float that indicates the error margines of measurement and the steps
            for visualisation.
        """
        assert limits[0] <= limits[1], 'Lower limit > upper limit!'
        self.name = name
        self.limits = limits
        self.resolution = resolution

    def __repr__(self):
        return self.name

    def __str__(self):
        return "Domain(%s)" % self.name
       
    def __getattr__(self, name):
        return self.sets[name]
    
    def __setattr__(self, name, value):
        if name == 'name':
            self.__dict__['name'] = value
        elif name == 'limits':
            self.__dict__['limits'] = value
        elif name == 'resolution':
            self.__dict__['resolution'] = value
        else:    
            assert isinstance(value, FuzzyFunction), '%s is not a FuzzyFunction!' % value
            self.sets[name] = FuzzySet(self.name, value)

class FuzzySet(object):
    __slots__ = ['domain', 'func']

    def __init__(self, domain, fuzzyfunc=constant(1)):
        """A Fuzzy Set is responsible for mapping concrete values to fits and back.

        Within a domain of discourse, the same functions for (de-)fuzzyification
        should be used for the same meaning.

        This maps a certain value within the domain of discourse
        (temperature, length, velocity, ..) to a degree of membership.
        Using the specified function.

        vars
        ----

        domain
            String to identify values of the same domain
        fuzzyfunc
            Function that is called exactly with 1 float and it returns a float
            within [0,1] to map values to degrees of membership.
            Functions of the fuzzification module take parameters at instantiation
            to define the behavior.


        """
        self.domain = domain
        self.func = fuzzyfunc

    def __call__(self, value):
        return self.func(value)

    def __and__(self, other):
        assert isinstance(other, FuzzySet), 'Only FuzzySets can be combined, other is %s' % type(other)
        return FuzzySet(self.domain, lambda x: min(self(x), other(x)))

    def __or__(self, other):
        assert isinstance(other, FuzzySet), 'Only FuzzySets can be combined, other is %s' % type(other)
        return FuzzySet(self.domain, lambda x: max(self(x), other(x)))

    def __invert__(self):
        return FuzzySet(self.domain, ~self.func)

    def __iter__(self):
        for x in arange(self.domain.limits[0], self.domain.limits[1] + 1, self.domain.resolution):
            yield self.func(x)

    def draw(self):
        try:
            r = arange(self.domain.limits[0], self.domain.limits[1] + 1, self.domain.resolution)
            v = [self.func(x) for x in r]
            plot(r, v)
            show()
        except ValueError:
            print "Can't draw fuzzyset, domain %s has no limits." % self.domain


class Rule(object):
    def __init__(self, IF, THEN, believe=1):
        pass

if __name__ == "__main__":
    temp = 25
    month = 9

    d = Domain('d')
    a = FuzzySet(d)
    
    def test():
        return ~~~~~~a(8.6)

    cProfile.run('test()')
    print Timer(test).timeit()

    temp = Domain("temperature", limits=(0,100))
    temp.hot = linearB(5, 35)

    mild = temp.hot & ~temp.hot


    import doctest
    doctest.testmod()
