# from pylab import plot, show
from numpy import arange

domains = {}
rules = []


class FuzzyFunction(object):
    """All FuzzyFunction classes are subclassed from this.

    FuzzyFunction classes are initialized with parameters and then used by calls
    with one single value. All FuzzyFunctions map arbitrary values to [0,1].
    """

    def __call__(self, x):
        return self.f(x)

    def __invert__(self):
        return NOT(self)

    def __and__(self, other):
        return AND(self, other)

    def __or__(self, other):
        return OR(self, other)

    def __repr__(self):
        return "{0}({1})".format(self.__class__.__name__, self.__dict__)

    def __str__(self):
        return "{0}({1})".format(self.__class__.__name__, self.__dict__)


# These basic operators are defined here to avoid an import-loop


class AND(FuzzyFunction):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __call__(self, x):
        return min(self.a(x), self.b(x))


class OR(FuzzyFunction):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __call__(self, x):
        return max(self.a(x), self.b(x))


class NOT(FuzzyFunction):
    def __init__(self, f):
        self.f = f

    def __call__(self, x):
        return 1 - self.f(x)


class Domain(object):
    def __init__(self, name, limits, resolution=1.0):
        """
        A domain normally is a linguistic variable in a system that usually
        corresponds with a physical unit and a range of valid values.
        Fuzzy-Sets or 'linguistic terms' are defined within domains by their
        function which map measurements within the domain onto degrees of
        membership (floats in the [0,1] range) for that linguistic term.


        name
            Full name of the domain

        limits
            Tuple with minimum and maximum values, order determines the graph
            for visualisation. Theoretically inf is allowed, but there's
            no way to handle it correctly.

        resolution
            Float that indicates the error margines of measurement and the steps
            for visualisation.
        """
        # the fuzzysets as attributes
        self.sets = {}
        assert limits[0] <= limits[1], "Lower limit > upper limit!"
        self.name = name
        self.limits = limits
        self.resolution = resolution
        domains[name] = self

    def __str__(self):
        return "Domain(%s)" % self.name

    def __getattr__(self, name):
        if name in self.sets:
            return self.sets[name]
        else:
            raise AttributeError

    def __setattr__(self, name, fuzzyfunc):
        # it's not actually a fuzzyfunc but a domain attr
        if name in ["name", "limits", "resolution", "sets"]:
            object.__setattr__(self, name, fuzzyfunc)
        # we've got a fuzzyset within this domain defined by a fuzzyfunc
        else:
            self.sets[name] = fuzzyfunc

    def plot(self):
        r = arange(self.limits[0], self.limits[1] + self.resolution, self.resolution)
        for s in self.sets.values():
            print(r, s)
            # plot(s(r))
        # show()

    def __call__(self, x):
        for name, f in self.sets.items():
            print(name, f(x))


class Rule(object):
    """Collection of fuzzysets and operators for inference.

    A rule has two mandatory arguments: IF and THEN, both being valid
    python expressions that evaluate to functions that take a single argument
    (usually fuzzyfunctions).
    For evaluation and inference of IF and THEN default functions or those
    provided via optional arguments are used.

    To evaluate concrete values (for defuzzification) simply call the Rule
    as a function.
    """

    def __init__(self, IF, THEN, believe=1, and_=None, or_=None, not_=None, inference_=None):
        """The core fuzzy logic.

        IF is a string representing a condition using qualified fuzzy sets
         (that is the *name* of the domain and the *name* of the set NOT
        the variable that was used for the domain!).
        THEN is a string representing a lingual hedge with a SINGLE fuzzy set
        or another rule.
        believe is a factor that is applied to the result of the rule,
        taking into account that rules may be subject to uncertainty.
        and_, or_ and not_ are the FuzzyFunctions that are used to
        implement the given operations for this rule. A user may choose to
        use a different function for a specific case and override these.
        """
        if and_ is not None:
            FuzzyFunction.__and__ = and_
        if or_ is not None:
            FuzzyFunction.__or__ = or_
        if not_ is not None:
            FuzzyFunction.__invert__ = not_

        # self.inference = inference_ if inference is not None else MAXMIN

        locals().update(domains)

        self.if_result = eval(IF)
        rules.append(self)

    def __call__(self):
        return self.if_result


if __name__ == "__main__":
    import cProfile
    from timeit import Timer

    from . import fuzzification as fuzzy

    temp = 25
    month = 9

    a = fuzzy.constant(0)

    year = Domain("year", limits=(1, 12))

    def definition():
        year.summer = fuzzy.trapezoid(4, 6, 7, 9, inverse=True)

    year = Domain("year", limits=(1, 12))
    year.summer = fuzzy.trapezoid(4, 6, 7, 9)

    def call():
        return a(8.6)

    cProfile.run("definition()")
    print(Timer(definition).timeit())

    cProfile.run("call")
    print(Timer(call).timeit())

    temp = Domain("temperature", limits=(0, 100))
    temp.hot = fuzzy.linear(5, 35)

    import doctest

    doctest.testmod()
