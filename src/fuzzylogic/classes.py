"""
classes.py - Domain, Set and Rule classes for fuzzy logic.

Primary abstractions for recursive functions and arrays,
adding logical operaitons for easier handling.
"""

from __future__ import annotations

from random import randint
from typing import Any, Iterable, overload

from numpy.typing import NDArray

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None


import numpy as np

from fuzzylogic import defuzz

from .combinators import MAX, MIN, bounded_sum, product, simple_disjoint_sum
from .functions import Membership, inv, normalize

type Array = (
    NDArray[np.float16]
    | NDArray[np.float32]
    | NDArray[np.float64]
    | NDArray[np.float128]
    | NDArray[np.float256]
)


class FuzzyWarning(UserWarning):
    """Extra Exception so that user code can filter exceptions specific to this lib."""

    pass


NO_DOMAIN_TO_COMPARE = "Domain can't work with no domain."
CANT_COMPARE_DOMAINS = "Can't work with different domains."
NO_DOMAIN = "No domain defined."


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
    >>> temp.hot = Set(lambda x: 0)
    >>> temp.hot(5)
    0

    It is possible now to call derived sets without assignment first!
    >>> from .hedges import very
    >>> (very(~temp.hot) | ~very(temp.hot))(2)
    1.0

    You MUST NOT add arbitrary attributes to an *instance* of Domain - you can
    however subclass or modify the class itself. If you REALLY have to add attributes,
    make sure to "whitelist" it in __slots__ first.

    Use the Domain by calling it with the value in question. This returns a
    dictionary with the degrees of membership per set. You MAY override __call__
    in a subclass to enable concurrent evaluation for performance improvement.
    """

    __slots__ = ["_name", "_low", "_high", "_res", "_sets"]

    def __init__(
        self,
        name: str,
        low: float,
        high: float,
        res: float = 1,
        sets: dict[str, Set] | None = None,
    ) -> None:
        """Define a domain."""
        assert low < high, "higher bound must be greater than lower."
        assert res > 0, "resolution can't be negative or zero"
        assert isinstance(name, str), "Domain Name must be a string."
        assert str.isidentifier(name), "Domain Name must be a valid identifier."
        self._name = name
        self._high = high
        self._low = low
        self._res = res
        self._sets = {} if sets is None else sets  # Name: Set(Function())

    def __call__(self, x: float) -> dict[Set, float]:
        """Pass a value to all sets of the domain and return a dict with results."""
        if not (self._low <= x <= self._high):
            raise FuzzyWarning(f"{x} is outside of domain!")
        return {self._sets[name]: s.func(x) for name, s in self._sets.items()}

    def __len__(self) -> int:
        """Return the size of the domain, as the actual number of possible values, calculated internally."""
        return len(self.range)

    def __str__(self) -> str:
        """Return a string to print()."""
        return self._name

    def __repr__(self) -> str:
        """Return a string so that eval(repr(Domain)) == Domain."""
        return f"Domain('{self._name}', {self._low}, {self._high}, res={self._res}, sets={self._sets})"

    def __eq__(self, other: object) -> bool:
        """Test equality of two domains."""
        if not isinstance(other, Domain):
            return False
        return all([
            self._name == other._name,
            self._low == other._low,
            self._high == other._high,
            self._res == other._res,
            self._sets == other._sets,
        ])

    def __hash__(self) -> int:
        return id(self)

    def __getattr__(self, name: str) -> Set:
        """Get the value of an attribute. Called after __getattribute__ is called with an AttributeError."""
        if name in self._sets:
            return self._sets[name]
        else:
            raise AttributeError(f"{name} is not a set or attribute")

    def __setattr__(self, name: str, value: Set | Membership) -> None:
        """Define a set within a domain or assign a value to a domain attribute."""
        # It's a domain attr
        if name in self.__slots__:
            object.__setattr__(self, name, value)
        # We've got a fuzzyset
        else:
            assert str.isidentifier(name), f"{name} must be an identifier."
            if not isinstance(value, Set):
                # Often useful to just assign a function for simple sets..
                value = Set(value)
            # However, we need the abstraction if we want to use Superfuzzysets (derived sets).
            self._sets[name] = value
            value.domain = self
            value.name = name
            value.array()  # force the array to be calculated for caching

    def __delattr__(self, name: str) -> None:
        """Delete a fuzzy set from the domain."""
        if name in self._sets:
            del self._sets[name]
        else:
            raise FuzzyWarning("Trying to delete a regular attr, this needs extra care.")

    @property
    def range(self) -> Array:
        """Return an arange object with the domain's specifics.

        This is used to conveniently iterate over all possible values
        for plotting etc.

        High upper bound is INCLUDED unlike range.
        """
        if int(self._res) == self._res:
            return np.arange(self._low, self._high + self._res, int(self._res))
        else:
            return np.linspace(self._low, self._high, int((self._high - self._low) / self._res) + 1)

    def min(self, x: float) -> float:
        """Standard way to get the min over all membership funcs.

        It's not just more convenient but also faster than
        to calculate all results, construct a dict, unpack the dict
        and calculate the min from that.
        """
        return min((f(x) for f in self._sets.values()), default=0)

    def max(self, x: float) -> float:
        """Standard way to get the max over all membership funcs."""
        return max((f(x) for f in self._sets.values()), default=0)


class Set:
    """
    A fuzzyset defines a 'region' within a domain.

    The associated membership function defines 'how much' a given value is
    inside this region - how 'true' the value is.

    Sets and functions MUST NOT be mixed because functions don't have
    the methods of the sets needed for the logic.

    Sets that are returned from one of the operations are 'derived sets' or
    'Superfuzzysets' according to Zadeh.

    Note that most checks are merely assertions that can be optimized away.
    DO NOT RELY on these checks and use tests to make sure that only valid calls are made.

    This class uses the classical MIN/MAX operators for AND/OR. To use different operators, simply subclass &
    replace the __and__ and __or__ functions. However, be careful not to mix the classes logically,
    since it might be confusing which operator will be used (left/right binding).

    """

    name = None  # these are set on assignment to the domain! DO NOT MODIFY
    domain = None

    def __init__(
        self,
        func: Membership,
        *,
        name: str | None = None,
        domain: Domain | None = None,
    ):
        self.func: Membership = func
        self.domain: Domain | None = domain
        self.name: str | None = name

        self._center_of_gravity: float | None = None
        self._cached_array: np.ndarray | None = None

    @overload
    def __call__(self, x: float, /) -> float: ...

    @overload
    def __call__(self, x: NDArray[np.float16], /) -> NDArray[np.float16]: ...

    @overload
    def __call__(self, x: NDArray[np.float32], /) -> NDArray[np.float32]: ...

    @overload
    def __call__(self, x: NDArray[np.float64], /) -> NDArray[np.float64]: ...

    @overload
    def __call__(self, x: NDArray[np.float128], /) -> NDArray[np.float128]: ...

    @overload
    def __call__(self, x: NDArray[np.float256], /) -> NDArray[np.float256]: ...

    def __call__(
        self,
        x: float | Array,
    ) -> float | Array:
        if isinstance(x, np.ndarray):
            return np.vectorize(self.func)(x)
        else:
            return self.func(x)

    def __invert__(self) -> Set:
        """Return a new set with 1 - function."""
        assert self.domain is not None, NO_DOMAIN
        return Set(inv(self.func), domain=self.domain)

    def __neg__(self) -> Set:
        """Synonyme for invert."""
        assert self.domain is not None, NO_DOMAIN
        return Set(inv(self.func), domain=self.domain)

    def __and__(self, other: Set) -> Set:
        """Return a new set with modified function."""
        assert self.domain is not None and other.domain is not None, NO_DOMAIN_TO_COMPARE
        assert self.domain == other.domain
        return Set(MIN(self.func, other.func), domain=self.domain)

    def __or__(self, other: Set) -> Set:
        """Return a new set with modified function."""
        assert self.domain == other.domain
        return Set(MAX(self.func, other.func), domain=self.domain)

    def __mul__(self, other: Set) -> Set:
        """Return a new set with modified function."""
        assert self.domain == other.domain
        return Set(product(self.func, other.func), domain=self.domain)

    def __add__(self, other: Set) -> Set:
        """Return a new set with modified function."""
        assert self.domain == other.domain
        return Set(bounded_sum(self.func, other.func), domain=self.domain)

    def __xor__(self, other: Set) -> Set:
        """Return a new set with modified function."""
        assert self.domain == other.domain
        return Set(simple_disjoint_sum(self.func, other.func), domain=self.domain)

    def __pow__(self, power: int) -> Set:
        """Return a new set with modified function."""

        # FYI: pow is used with hedges
        def f(x: float):
            return pow(self.func(x), power)

        return Set(f, domain=self.domain)

    def __eq__(self, other: object) -> bool:
        """A set is equal with another if both return the same values over the same range."""
        if self.domain is None or not isinstance(other, Set) or other.domain is None:
            # It would require complete bytecode analysis to check whether both Sets
            # represent the same recursive functions -
            # additionally, there are infinitely many mathematically equivalent
            # functions that don't have the same bytecode...
            raise FuzzyWarning("Impossible to determine.")

        # however, if domains ARE assigned (whether or not it's the same domain),
        # we simply can check if they map to the same values
        return np.array_equal(self.array(), other.array())

    def __le__(self, other: Set) -> bool:
        """If this <= other, it means this is a subset of the other."""
        assert self.domain is not None and other.domain is not None, NO_DOMAIN_TO_COMPARE
        assert self.domain == other.domain, CANT_COMPARE_DOMAINS
        return all(np.less_equal(self.array(), other.array()))

    def __lt__(self, other: Set) -> bool:
        """If this < other, it means this is a proper subset of the other."""
        assert self.domain is not None and other.domain is not None, NO_DOMAIN_TO_COMPARE
        assert self.domain == other.domain, CANT_COMPARE_DOMAINS
        return all(np.less(self.array(), other.array()))

    def __ge__(self, other: Set) -> bool:
        """If this >= other, it means this is a superset of the other."""
        assert self.domain is not None and other.domain is not None, NO_DOMAIN_TO_COMPARE
        assert self.domain == other.domain, CANT_COMPARE_DOMAINS
        return all(np.greater_equal(self.array(), other.array()))

    def __gt__(self, other: Set) -> bool:
        """If this > other, it means this is a proper superset of the other."""
        assert self.domain is not None and other.domain is not None, NO_DOMAIN_TO_COMPARE
        assert self.domain == other.domain, CANT_COMPARE_DOMAINS
        return all(np.greater(self.array(), other.array()))

    def __len__(self) -> int:
        """Number of membership values in the set, defined by bounds and resolution of domain."""
        assert self.domain is not None, NO_DOMAIN
        return len(self.array())

    @property
    def cardinality(self) -> float:
        """The sum of all values in the set."""
        assert self.domain is not None, NO_DOMAIN
        return sum(self.array())

    @property
    def relative_cardinality(self) -> float:
        """Relative cardinality is the sum of all membership values by float of all values."""
        assert self.domain is not None, NO_DOMAIN
        assert len(self) > 0, "The domain has no element."  # only possible with step=inf, but still..
        return self.cardinality / len(self)

    def concentrated(self) -> Set:
        """
        Alternative to hedge "very".

        Returns a new set that has a reduced amount of values the set includes and to dampen the
        membership of many values.
        """
        return Set(lambda x: self.func(x) ** 2, domain=self.domain)

    def intensified(self) -> Set:
        """
        Alternative to hedges.

        Returns a new set where the membership of values are increased that
        already strongly belong to the set and dampened the rest.
        """

        def f(x: float) -> float:
            return 2 * self.func(x) ** 2 if x < 0.5 else 1 - 2 * (1 - self.func(x) ** 2)

        return Set(f, domain=self.domain)

    def dilated(self) -> Set:
        """Expand the set with more values and already included values are enhanced."""
        return Set(lambda x: self.func(x) ** 1.0 / 2.0, domain=self.domain)

    def multiplied(self, n: float) -> Set:
        """Multiply with a constant factor, changing all membership values."""
        return Set(lambda x: self.func(x) * n, domain=self.domain)

    def plot(self) -> None:
        """Graph the set in the given domain."""
        assert self.domain is not None, NO_DOMAIN
        if not plt:
            raise ImportError(
                "matplotlib not available. Please re-install with 'pip install fuzzylogic[plotting]'"
            )
        R = self.domain.range  # e.g., generated via np.linspace(...)

        cog_val = self.center_of_gravity()

        diffs = np.diff(R)
        tol_value = diffs.min() / 100 if len(diffs) > 0 else 1e-6

        if all(abs(x - cog_val) >= tol_value for x in R):
            R = sorted(set(R).union({cog_val}))

        V = [self.func(x) for x in R]
        plot_color = "#{:06x}".format(randint(0, 0xFFFFFF))
        plt.plot(R, V, label=str(self), color=plot_color, lw=2)
        plt.axvline(cog_val, color=plot_color, linestyle="--", linewidth=1.5, label=f"CoG = {cog_val:.2f}")
        plt.plot(cog_val, self.func(cog_val), "o", color=plot_color, markersize=8)

        plt.title("Fuzzy Set Membership Function")
        plt.xlabel("Domain Value")
        plt.ylabel("Membership Degree")
        plt.legend()
        plt.grid(True)

    def array(self) -> Array:
        """Return an array of all values for this set within the given domain."""
        assert self.domain is not None, NO_DOMAIN
        if self._cached_array is None:
            self._cached_array = np.fromiter((self.func(x) for x in self.domain.range), float)
        return self._cached_array

    def range(self) -> Array:
        """Return the range of the domain."""
        assert self.domain is not None, NO_DOMAIN
        return self.domain.range

    def center_of_gravity(self) -> float:
        """Return the center of gravity for this distribution, within the given domain."""
        if self._center_of_gravity is not None:
            return self._center_of_gravity
        assert self.domain is not None, NO_DOMAIN
        weights = self.array()
        if sum(weights) == 0:
            return 0
        cog = float(np.average(self.domain.range, weights=weights))
        self._center_of_gravity = cog
        return cog

    def __repr__(self) -> str:
        """
        Return a string representation of the Set that reconstructs the set with eval().
        """
        if self.domain is not None:
            return f"{self.domain._name}.{self.name}"  # type: ignore
        return f"Set(({self.func.__qualname__})"

    def __str__(self) -> str:
        """Return a string for print()."""
        if self.domain is not None:
            return f"{self.domain._name}.{self.name}"  # type: ignore
        return f"Set({self.func.__name__})"

    def normalized(self) -> Set:
        """Return a set that is normalized *for this domain* with 1 as max."""
        assert self.domain is not None, NO_DOMAIN
        return Set(normalize(max(self.array()), self.func), domain=self.domain)

    def __hash__(self) -> int:
        return id(self)


class SingletonSet(Set):
    def __init__(self, c: float, no_m: float = 0, c_m: float = 1, domain: Domain | None = None):
        super().__init__(self._singleton_fn(c, no_m, c_m), domain=domain)
        self.c = c
        self.no_m = no_m
        self.c_m = c_m
        self.domain = domain

        self._cached_array: np.ndarray | None = None

    @staticmethod
    def _singleton_fn(c: float, no_m: float = 0, c_m: float = 1) -> Membership:
        return lambda x: c_m if x == c else no_m

    def center_of_gravity(self) -> float:
        """Directly return singleton position"""
        return self.c

    def plot(self) -> None:
        """Graph the singleton set in the given domain,
        ensuring that the singleton's coordinate is included.
        """
        assert self.domain is not None, "NO_DOMAIN"
        if not plt:
            raise ImportError(
                "matplotlib not available. Please re-install with 'pip install fuzzylogic[plotting]'"
            )

        R = self.domain.range
        if self.c not in R:
            R = sorted(set(R).union({self.c}))
        V = [self.func(x) for x in R]
        plt.plot(R, V, label=f"Singleton {self.c}")
        plt.title("Singleton Membership Function")
        plt.xlabel("Domain Value")
        plt.ylabel("Membership")
        plt.legend()
        plt.grid(True)
        plt.show()


class Rule:
    """
    Collection of bound sets spanning a multi-dimensional space of their domains, mapping to a target domain.

    """

    type T = Rule

    def __init__(
        self,
        *args: Rule | dict[Iterable[Set] | Set, Set],
    ) -> None:
        """Define a rule with conditions and a target set."""
        self.conditions: dict[frozenset[Set], Set] = {}
        for arg in args:
            if isinstance(arg, Rule):
                self.conditions |= arg.conditions
            elif isinstance(arg, dict):
                for if_sets, then_set in arg.items():
                    if isinstance(if_sets, Set):
                        if_sets = (if_sets,)
                    self.conditions[frozenset(if_sets)] = then_set  # type: ignore
            else:
                raise TypeError(f"Expected any number of Rule or dict[Set, Set], got {type(arg).__name__}.")

    def __add__(self, other: Rule) -> Rule:
        return Rule({**self.conditions, **other.conditions})

    def __radd__(self, other: Rule | int) -> Rule:
        if isinstance(other, int):  # as sum(...) does implicitely 0 + ...
            return self
        return Rule({**self.conditions, **other.conditions})

    def __or__(self, other: Rule) -> Rule:
        return Rule({**self.conditions, **other.conditions})

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Rule):
            return False
        return self.conditions == other.conditions

    def __getitem__(self, key: Iterable[Set]) -> Set:
        return self.conditions[frozenset(key)]

    def __call__(self, values: dict[Domain, float], method=defuzz.cog) -> float | None:
        """
        Calculate the inferred crisp value based on the fuzzy rules.
        values: dict[Domain, float] - the input values for the fuzzy sets
        method: defuzzification method to use (default: center of gravity) from fuzzylogic.defuzz
        Returns the defuzzified value.
        """
        assert isinstance(values, dict), "Please pass a dict[Domain, float|int] as values."
        assert values, "No condition rules defined!"

        # Extract common target domain and build list of (then_set, firing_strength)
        sample_then_set = next(iter(self.conditions.values()))
        target_domain = getattr(sample_then_set, "domain", None)
        assert target_domain, "Target domain must be defined."

        target_weights: list[tuple[Set, float]] = []
        for if_sets, then_set in self.conditions.items():
            assert then_set.domain == target_domain, "All target sets must be in the same Domain."
            degrees = []
            for s in if_sets:
                assert s.domain is not None, "Domain must be defined for all fuzzy sets."
                degrees.append(s(values[s.domain]))
            firing_strength = min(degrees, default=0)
            if firing_strength > 0:
                target_weights.append((then_set, firing_strength))
        if not target_weights:
            return None

        # For center-of-gravity / centroid:
        if method == defuzz.cog:
            return defuzz.cog(target_weights)

        # For methods that rely on an aggregated membership function:
        points = list(target_domain.range)
        n = len(points)
        step = (
            (target_domain._high - target_domain._low) / (n - 1)
            if n > 1
            else (target_domain._high - target_domain._low)
        )

        def aggregated_membership(x: float) -> float:
            # For each rule, limit its inferred output by its firing strength and then take the max
            return max(min(weight, then_set(x)) for then_set, weight in target_weights)

        match method:
            case defuzz.bisector:
                return defuzz.bisector(aggregated_membership, points, step)
            case defuzz.mom:
                return defuzz.mom(aggregated_membership, points)
            case defuzz.som:
                return defuzz.som(aggregated_membership, points)
            case defuzz.lom:
                return defuzz.lom(aggregated_membership, points)
            case _:
                raise ValueError("Invalid defuzzification method specified.")


def rule_from_table(table: str, references: dict[str, float]) -> Rule:
    """Turn a (2D) string table into a Rule of fuzzy sets.

    ATTENTION: This will eval() all strings in the table.
    This can pose a potential security risk if the table originates from an untrusted source.

    Using a table will considerably reduce the amount of required text to describe all rules,
    but there are two critical drawbacks: Tables are limited to 2 input variables (2D) and they are strings,
    with no IDE support. It is strongly recommended to check the Rule output for consistency.
    For example, a trailing "." will result in a SyntaxError when eval()ed.
    """
    import io
    from itertools import product

    import pandas as pd

    df = pd.read_table(io.StringIO(table), sep=r"\s+")  # type: ignore

    D: dict[tuple[Any, Any], Any] = {
        (
            eval(df.index[x].strip(), references),  # type: ignore
            eval(df.columns[y].strip(), references),  # type: ignore
        ): eval(df.iloc[x, y], references)  # type: ignore
        for x, y in product(range(len(df.index)), range(len(df.columns)))  # type: ignore
    }
    return Rule(D)  # type: ignore


if __name__ == "__main__":
    import doctest

    doctest.testmod()
