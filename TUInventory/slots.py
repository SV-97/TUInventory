from secrets import choice, compare_digest
from string import ascii_letters, digits

import sqlalchemy

import classes
import keys
from logger import logger


CSession = classes.setup_context_session(classes.engine)


def save_to_db(instance):
    """Save instance to it's corresponding table
    ToDo: Error handling if uid already exists
    """
    with CSession() as session:
        session.add(instance)


def update_user_dependant(user):
    pass


def create_user(e_mail, password, name, surname, location, phonenumber):
    new_user = classes.User(e_mail, password, name, surname, phonenumber)
    new_user.location = location
    save_to_db(new_user)
    return new_user


def create_admin(new_admin):
    """Create a new admin"""
    new_admin.is_admin = True
    save_to_db(new_admin)
    return new_admin


def login(e_mail, password):
    """Log user into application"""
    e_mail = e_mail.lower()
    with CSession() as session:
        try:
            user = session.query(classes.User).filter_by(e_mail=e_mail).first()
            user_at_gate = classes.User(e_mail, password, salt=user.salt)
            if compare_digest(user_at_gate.password, user.password):
                update_user_dependant(user)
                session.expunge(user)
                logger.info(f"Successfully logged in as {user.uid}")
                return user
            else:
                logger.info(f"Attempted login with wrong password for user {e_mail}")
                return None
        except (AttributeError, ValueError) as e: #user not found exception
            logger.info(f"Attempted login from unknown user {e_mail}")
            pass # show error message


def logout():
    """Log user out of application"""
    pass 


def create_device(article):
    new_device = classes.Device()
    new_device.article = article
    save_to_db(new_device)
    return new_device


def create_location():
    pass


def create_producer():
    pass


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
    #catch error if invalid key or no public key
    cipher, decipher = keys.read_keys(path_public, path_private)
    text = b"True"
    ciphertext = cipher.encrypt(text)
    if compare_digest(decipher.decrypt(ciphertext), text):
        keys.generate_key(path_public, path_private)
        new_password = reset_password(user)
        return new_password
    else:
        return None


if __name__ == "__main__":
    user = login("schokoladenkönig@googlemail.com", "12345ibimsdaspasswort")
    print(user.e_mail)