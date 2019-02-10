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

    datapoints = 2000
    for j in range(5):
        T1 = []
        T2 = []
        T3 = []
        a = [a for a in ascii_letters]
        for i in range(datapoints):
            t1 = time()
            f_1(a);
            t2 = time()
            T1.append(t2 - t1)

            t1 = time()
            f_2(a);
            t2 = time()
            T2.append(t2 - t1)

            t1 = time()
            f_3(a);
            t2 = time()
            T3.append(t2 - t1)

        print(f"Dataset #{j}")
        times = {key: median(val) for key, val in zip(("For loop", "List Comprehension", "Map"), (T1, T2, T3))}
        longest = max(map(len, times))
        for key, val in times.items():
            print(f"{key:{longest}}: {val:.4e}s")
        min_ = min(map(median, (T1, T2, T3)))
        fastest = {val: key for key, val in times.items()}[min_]
        print(f"Fastest was: {fastest}")
        print()

x = list(range(datapoints))
plt.plot(x, T1, label="For loop")
plt.plot(x, T2, label="List Comp")
plt.plot(x, T3, label="map")

plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
plt.tick_params(axis='both', which='major', labelsize=12)
plt.tick_params(axis='both', which='minor', labelsize=12)
plt.xlabel("Datenpunkt", fontsize=14)
plt.ylabel("Laufzeit in s", fontsize=14)
plt.legend(prop={'size': 14})
plt.show()