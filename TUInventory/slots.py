import threading
from time import sleep, time

import sqlalchemy

import classes

Session = sqlalchemy.orm.sessionmaker(bind=classes.engine)
CSession = classes.ContextSession.setup(classes.engine)

def save_to_db(instance):
    """Save instance to it's corresponding table
    ToDo: Error handling if uid already exists
    """
    with CSession() as session:
        session.add(instance)

def toggle_admin_tools(is_admin):
    pass # hide and show widgets depending on admin_status

def update_user_dependant(user):
    pass # update elements that hold user-sensitive data like a name on display

def create_user():
    e_mail = ""
    password = ""
    name = ""
    surname = ""
    location = ""
    phonenumber = ""
    new_user = classes.User(e_mail, password, name, surname, phonenumber)
    new_user.location = location
    save_to_db(new_user)
    return new_user

def create_admin():
    """Create a new admin"""
    new_admin = create_user()
    new_admin.is_admin = True
    save_to_db(new_admin)
    return new_admin

def login():
    """Log user into application"""
    e_mail = ""
    password = ""
    user_at_gate = classes.User(e_mail, password)
    try:
        with CSession() as session:
            user = session.query(classes.User).filter_by(e_mail == user_at_gate.e_mail).first()
    except Exception as e: #user not found exception
        pass # show error message
    if user_at_gate.password == user.password:
        toggle_admin_tools(user.is_admin)
        update_user_dependant(user)
        return user
    else:
        return None

def logout():
    """Log user out of application"""
    pass


class Timeout(threading.Thread):
    def __init__(self, timeout, function, args=[]):
        """Timer that runs in background and executes a function if it's not refreshed
        Args:
            function: function that is executed once time runs out
            timeout: time in seconds after which the timeout executes the function
            args: arguments for function
        """
        super().__init__()
        self.timeout = timeout
        self.function = function
        self.args = args
        self.lock = threading.Lock()
        self.timed_out = False
        self.reset()

    def _refresh_timer(self):
        with self.lock:
            return self.timeout - (time() - self.last_interaction_timestamp)

    timer = property(fget=_refresh_timer)

    def reset(self):
        """Reset the internal timer"""
        with self.lock:
            if not self.timed_out:
                self.is_reset = True
                self.last_interaction_timestamp = time()

    def run(self):
        with self.lock:
            if self.is_reset:
                self.is_reset = False           
            else:
                self.timed_out = True
                self.function(*self.args)
                return
            difference_to_timeout = self.timeout - (time() - self.last_interaction_timestamp)
        sleep(difference_to_timeout)
        self.run() 

if __name__ == "__main__":

    timeout = Timeout(timeout=10, resolution=2, function=print, args=["timed out"])
    timeout.start()

    reset_thread = threading.Thread(target=lambda: timeout.reset() if input() else None) # function for testing - reset on input
    reset_thread.start()
    t = 0
    delta_t = 3
    while not timeout.timed_out:
        print(f"Not timed out yet - {t:.2f} seconds passed")
        t += delta_t
        print(f"internal timer is at {timeout.timer:.2f}s")
        sleep(delta_t)
    timeout.join()
    reset_thread.join()