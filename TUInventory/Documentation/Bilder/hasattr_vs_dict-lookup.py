import threading
import queue
from time import sleep, time
import matplotlib.pyplot as plt
import timeit

class B():
    def __init__(self):
        self.status = False

    def reset(self):
        self.status = True

class A():
    def __init__(self):
        self.timeout = B()
        for i in range(100):
            setattr(self, f"{i}", i)
    def refresh(self):
        if "timeout" in self.__dict__:
            self.timeout.reset()
    def refresh_2(self):
        if hasattr(self, "timeout"):
            self.timeout.reset()

for j in range(1, 4):
    a = A()
    T1 = []
    T2 = []
    t1 = time()
    t2 = time()

    for i in range(1000):
        t1 = time()
        a.refresh()
        t2 = time()
        T1.append(t2 - t1)
        t1 = time()
        a.refresh_2()
        t2 = time()
        T2.append(t2 - t1)

    plt.subplot(3, 1, j)
    plt.plot([x for x in range(len(T1))], T1, label=f"dict lookup: {sum(T1)/len(T1):.2e}s")
    plt.plot([x for x in range(len(T2))], T2, label=f"hasattr: {sum(T2)/len(T2):.2e}s")
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    plt.xlabel("Datapoint", fontsize=12)
    plt.ylabel("Time in s", fontsize=12)
    plt.legend(prop={'size': 12})
plt.show()