import dis


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
    def dict_lookup_(self):
        if "timeout" in self.__dict__:
            self.timeout.reset()
    def hasattr_(self):
        if hasattr(self, "timeout"):
            self.timeout.reset()

    
a = A()


def hasattr_():
    if hasattr(a, "timeout"):
        a.timeout.reset()


def dict_lookup_():
    if "timeout" in a.__dict__:
        a.timeout.reset()


print(f"{'hasattr':-^50}")
print(dis.dis(hasattr_))
print("\n")
print(f"{'dict-lookup':-^50}")
print(dis.dis(dict_lookup_))