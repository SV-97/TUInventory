
import sqlalchemy

import classes

# Session = sqlalchemy.orm.sessionmaker(bind=classes.engine)
CSession = classes.setup_context_session(classes.engine)

def save_to_db(instance):
    """Save instance to it's corresponding table
    ToDo: Error handling if uid already exists
    """
    with CSession() as session:
        session.add(instance)

def toggle_admin_tools(is_admin):
    pass # hide and show widgets depending on admin_status

def update_user_dependant(user):
    pass 

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

def login(e_mail, password):
    """Log user into application"""
    with CSession() as session:
        try:
            user = session.query(classes.User).filter_by(e_mail=e_mail).first()
            user_at_gate = classes.User(e_mail, password, salt=user.salt)
            if user_at_gate.password == user.password:
                toggle_admin_tools(user.is_admin)
                update_user_dependant(user)
                session.expunge(user)
                return user
            else:
                return None
        except ValueError as e: #user not found exception
            print(e)
            pass # show error message


def logout():
    """Log user out of application"""
    pass 


if __name__ == "__main__":
    user = login("schokoladenkönig@googlemail.com", "12345ibimsdaspasswort")
    print(user.e_mail)