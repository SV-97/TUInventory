class MyClass():
    def my_method(self):
        pass

    @classmethod
    def my_classmethod(cls):
        pass

    @staticmethod
    def my_static_method():
        pass

    def __call__(self, *args, **kwargs):
        pass


is_a_function_now = MyClass.my_method
MyClass()() # calls an instance of MyClass

