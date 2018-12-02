>>> from sys import getsizeof
>>> a = [i for i in range(10)]
>>> b = (i for i in range(10))
>>> getsizeof(a)
192
>>> getsizeof(b)
88
>>> type(a)
<class 'list'>
>>> type(b)
<class 'generator'>
>>> a[0]
0
>>> b[0]
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: 'generator' object is not subscriptable
>>> sum(a)+sum(a)
90
>>> sum(b)+sum(b)
45
>>> 
