# fuzzy - Fuzzy Logic library for Python 3

The first time I publish one of my private libraries. Thanks to hypothesis unit tests, I'm pretty confident that things should work out of the box in most cases. This is the third or fourth time I rebuild this library from scratch to find the sweet spot between ease of use (beautiful is better than ugly!), testability (simple is better than complex!) and potential to optimize for performance (practicality beats purity!). 

### Why a new library?
The first time I was confronted with fuzzy logic, I fell in love with the concept, but after reading books and checking out libraries etc. I found it frustrating how most people make fuzzy logic appear complicated, hard to handle and incorporate in code.
Sure, there are frameworks that allow modelling of functions via GUI, but that's not a solution for a coder, right? Then there's a ton of mathematical research and other cruft that no normal person has time and patience to work through before trying to explore and applying things. Coming from this direction, there are also a number of script-ish (DSL) language frameworks that try to make the IF THEN ELSE pattern work (which I also tried in python, but gave it up because it just looks ugly).
And yes, it's also possible to implement the whole thing completely in a functional style, but you really don't want to work with a recursive structure of 7+ steps by hand, trying not to miss a (..) along the way.
Finally, most education on the subject emphasize sets and membership functions, but fail to mention the importance of the domain (or "universe of discourse"). It's easy to miss this point if you get lost with set operations and membership values, which are actually not that difficult once you can *play* and *explore* how these things look and work!

### The Idea
So, the idea is to have four main parts that work together: Domains, Sets, functions and Rules. You start modelling your system by defining your domain of interest. Then you think about where your interesting points are in that domain and look for a function that might do what you want. In general, fuzzy.functions map any value to [0,1], that's all. Then simply wrap your function in a Set and assign this to the domain in question. Once assigned, you can plot that set and see if it actually looks how you imagined. Now that you have one or more sets, you also can start to combine them with set operations &, |, ~, etc. It's fairly straight forward.
Finally, use the Rules to map input domain to output domain to actually control stuff.

Check the notebook for working examples and documentation.

Have fun!
- Anselm