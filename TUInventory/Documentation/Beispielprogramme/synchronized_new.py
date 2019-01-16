def synchronized(function):
    """Function-decorator to automatically add the instance a function returns to DB"""
    def synchronized_function(*args, **kwargs):
        instance = function(*args, **kwargs)
        save_to_db(instance)
        return instance
    return synchronized_function