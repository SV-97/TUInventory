from functools import partial

def synchronized(function, decorated=False, *args, **kwargs):
    """Function-decorator to automatically add the instance a function returns to DB"""
    if not decorated:
        return partial(synchronized, function, True)
    else:
        instance = function(*args, **kwargs)
        save_to_db(instance)
        return instance