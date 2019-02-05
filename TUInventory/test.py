from datetime import datetime

import sqlalchemy

import classes

Session = classes.orm.sessionmaker(bind=classes.engine)
session = Session()

user = classes.User(str(datetime.now()), "123", "vorname", "nachname", "09123 1513")

try:
    session.add(user)
    session.commit()
    user.uid # make uid accessible outside of session
    session.expunge(user)
except sqlalchemy.exc.IntegrityError:
    session.rollback()
finally:
    session.close()
print(user.uid)

CSession = classes.setup_context_session(classes.engine)
user = classes.User(str(datetime.now()), "123", "vorname", "nachname", "09123 1513")
with CSession() as session:
    session.add(user)
print(user.uid)
print(user.phonenumber)
print(user.salt)
print(user.password)