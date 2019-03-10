def login(e_mail, password):
    """Log user into application
    Checks if there's a user of given name in the database,
    if the given password is correct and returns the user 
    if both is the case

    Args:
        e_mail (str): e_mail of the user that wants to log in
        password (str): user provided password to check against
    """
    e_mail = e_mail.lower()
    with CSession() as session:
        try:
            user = session.query(classes.User)
                .filter_by(e_mail=e_mail).first()
            user_at_gate = classes.User(
                e_mail, 
                password, 
                salt=user.salt)
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
            raise ValueError(f"Attemped login from unknown user {e_mail}")
