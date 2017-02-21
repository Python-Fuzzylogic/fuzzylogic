# fuzzy
Fuzzy logic library for Python

First time I publish one of my private libraries. It's been a while since I updated the tests and stuff, so I can't say if things work out of the box, but it should work in general.

The main idea behind this library is to have simple, easy to remember, general functions that are parametrized at first to pre-calculate some of the more complex things so that the many subsequent calls required for handling all the values is fast.

I experimented a little with numba for this purpose, IIRC I hit a roadblock there because the general functions also involve returning functions (for the boolean operations), which I never got around to fix and handle properly.
