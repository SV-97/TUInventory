import threading
import queue
from time import sleep, time
import matplotlib.pyplot as plt

class Queues(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True
        self.in_queue = queue.Queue()
        self.out_queue = queue.Queue()
    def run(self):
        while True:
            job = self.in_queue.get()
            job += 1
            self.out_queue.put(job)
            self.in_queue.task_done()


class Locks(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True
        self.lock_in = threading.Lock()
        self.lock_out = threading.Lock()
        self._val_in = 0
        self._val_out = 0
    def get_val_in(self):
        with self.lock_in:
            return self._val_in
    def set_val_in(self, val):
        with self.lock_in:
            self._val_in = val
    val_in = property(get_val_in, set_val_in)
    def get_val_out(self):
        with self.lock_out:
            return self._val_out
    def set_val_out(self, val):
        with self.lock_out:
            self._val_out = val
    val_out = property(get_val_out, set_val_out)
    def run(self):
        while True:
            self.val_out = self.val_in + 1
i = 0


i += 1
T1 = []
T2 = []

val = 1
list_manager = Queues()
list_manager.start()
while not val == 20000:
    t1 = time()
    list_manager.in_queue.put(val)
    val = list_manager.out_queue.get()
    t2 = time()
    T1.append(t2 - t1)
    
val = 1

locks = Locks()
locks.start()
while not val == 20000:
    t3 = time()
    locks.val_in = val
    val = locks.val_out
    t4 = time()
    T2.append(t4 - t3)

average_T1 = sum(T1)/len(T1)
average_T2 = sum(T2)/len(T2)
T1_x = [i for i in range(len(T1))]
T2_x = [i for i in range(len(T2))]
plt.plot(T1_x, T1, label=f"Queues")
plt.plot(T2_x, T2, label=f"Polling")
plt.plot((T2_x[0], T2_x[-1]), (average_T1, average_T1), label=f"Durchschnitt Queues = {average_T1:.2e}s")
plt.plot((T2_x[0], T2_x[-1]), (average_T2, average_T2), label=f"Durchschnitt Polling = {average_T2:.2e}s")

plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
plt.tick_params(axis='both', which='major', labelsize=12)
plt.tick_params(axis='both', which='minor', labelsize=12)
plt.xlabel("Datenpunkt", fontsize=14)
plt.ylabel("Reaktionszeit in s", fontsize=14)
plt.legend(prop={'size': 14})
plt.show()