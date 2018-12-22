from classes import engine, setup_context_session 
# Ausserdem werden benoetigte Klassen etc. eingebunden

CSession = setup_context_session(engine)
# ... Instanziieren der Klassen zu user1 und user2 sowie location1
with CSession() as session:
    session.add(user1)
    session.add_all([user1, location1])