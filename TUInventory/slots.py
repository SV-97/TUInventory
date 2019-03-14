from functools import wraps
from secrets import choice, compare_digest
from string import ascii_letters, digits

import sqlalchemy

import classes
import keys
from logger import logger


CSession = classes.setup_context_session(classes.engine)


def synchronized(function):
    """Function-decorator to automatically add the instance a function returns to DB"""
    @wraps(function)
    def synchronized_function(*args, **kwargs):
        instance = function(*args, **kwargs)
        try:
            save_to_db(instance)
        except sqlalchemy.exc.IntegrityError: # uid already in db
            raise classes.IntegrityError(str(args) + str(kwargs))
        return instance
    return synchronized_function


def save_to_db(instance):
    """Save instance to it's corresponding table"""
    with CSession() as session:
        session.add(instance)


@synchronized
def create_user(*args, **kwargs):
    """Create a new user"""
    new_user = classes.User(*args, **kwargs)
    return new_user


@synchronized
def create_admin(*args, **kwargs):
    """Create a new admin"""
    new_admin = classes.User(*args, **kwargs)
    new_admin.is_admin = True
    return new_admin


def login(e_mail, password):
    """Log user into application
    Checks if there's a user of given name in the database,
    if the given password is correct and returns the user if both is the case
    Args:
        e_mail (str): e_mail of the user that wants to log in
        password (str): user provided password to check against
    """
    e_mail = e_mail.lower()
    with CSession() as session:
        try:
            user = session.query(classes.User).filter_by(e_mail=e_mail).first()
            user_at_gate = classes.User(e_mail, password, salt=user.salt)
            if compare_digest(user_at_gate.password, user.password):
                session.expunge(user)
                logger.info(f"Successfully logged in as {user.uid}")
                return user
            else:
                logger.info(f"Attempted login with wrong password for user {e_mail}")
                return None
        except (AttributeError, ValueError) as e: #user not found exception
            logger.info(f"Attempted login from unknown user {e_mail}")
            raise ValueError(f"Attemped login from unknown user {e_mail}")


def logout():
    """Log user out of application"""
    pass 


@synchronized
def create_device(article):
    new_device = classes.Device()
    new_device.article = article
    return new_device


@synchronized
def create_article(*args, **kwargs):
    return classes.Article(*args, **kwargs)


@synchronized
def create_location(*args, **kwargs):
    return classes.Location(*args, **kwargs)
    

@synchronized
def create_producer(*args, **kwargs):
    return classes.Producer(*args, **kwargs)


def generate_password(len_=15):
    """Generate an human readable password of given length"""
    alphabet = ascii_letters
    without = list("O0Il")
    pw_chars = alphabet + digits + "!,;.-_+-*()[]{}$%=?€#'~ß§&"
    pw_chars = "".join((letter for letter in pw_chars if letter not in without))
    pw = "".join((choice(pw_chars) for i in range(len_)))
    return pw


def reset_password(user):
    user.salt = user.new_salt()
    password = generate_password()
    user.hash(password)
    return password


def reset_admin_password(user, path_public, path_private):
    try:
        cipher, decipher = keys.read_keys(path_public, path_private)
    except ValueError:
        raise ValueError(f"Invalid RSA private-key at {path_private}!")
    text = b"True"
    ciphertext = cipher.encrypt(text)
    if compare_digest(decipher.decrypt(ciphertext), text):
        keys.generate_key(path_public, path_private)
        new_password = reset_password(user)
        return new_password
    else:
        return None


if __name__ == "__main__":
    from datetime import datetime

    with CSession() as session: 
        loc = session.query(classes.Location).first()
        session.add(loc)

    print(list(map(lambda x: str(x), loc.users)))

    user = create_user(str(datetime.now()), "password", "name", "surname", "94123 12315-123")
        
    with CSession() as session:
        session.add(user)
        session.add(loc)
        user.location = loc

    print(user.uid)
    print(user.location.uid)

    with CSession() as session:
        session.add(user)
        session.add(loc)
        user.name = "updated"

    admin = create_admin(str(datetime.now()), "password", "name", "surname", "94123 12315-123")
    print(admin.is_admin)

    with CSession() as session: 
        article = session.query(classes.Article).first()
        session.add(article)
        session.add_all(article.devices)

    list(map(print, article.devices))