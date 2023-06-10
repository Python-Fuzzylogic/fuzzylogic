# FAQ'S

Q: I'm triying to make a simple rule IF A then B
but if I write 
``` 
R1 = Rule({A: B})
R1 = Rule({temp.hot: motor.fast}) 
```
Gives me an error -> TypeError: 'Set' object is not iterable

A: Rules are there to map sets of one domain to a single set of another, so it expects the left side to be an iterable like a tuple.Try `R1 = Rule({(temp.hot, ): motor.fast})` That should do the trick.

---

Q: I'm wondering which papers/books you followed for the program. I just started learning fuzzy logic and can't find a good paper or book. Thanks a lot.

A: I've learned the basics of fuzzy logic in my CS study at university, many years ago, but I can't give you those resources.
The book I followed mostly, idea and definition-wise is [Fuzzy Logic and Control: Software and Hardware Applications, Vol. 2 by Mohammad Jamshidi, Nader Vadiee and Timothy Ross]( https://books.google.de/books/about/Fuzzy_Logic_and_Control.html?id=fN9SAAAAMAAJ&redir_esc=y )

Oh, and there are excellent youtube videos on the subject that also inspired me:
[Lecture series by Prof S Chakraverty](https://www.youtube.com/watch?v=oWqXwCEfY78 )
and [examples like](https://youtu.be/R4TPFpYXvS0)

