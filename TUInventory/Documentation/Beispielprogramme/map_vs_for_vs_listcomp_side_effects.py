from statistics import median
from string import ascii_letters
import tempfile
from time import time

import matplotlib.pyplot as plt

with tempfile.TemporaryFile("w+") as out:
    def printer(a):
        print(a, file=out)

    def f_1(a):
        for b in a:
            printer(b)

    def f_2(a):
        [printer(b) for b in a]

    def f_3(a):
        map(printer, a)
 
...