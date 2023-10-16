import db
from getpass import getpass

if __name__ == "__main__":
    username = input("Input new user name:")
    password = getpass("Input the password:")
    auth = int(input("Input the new auth level for the user:"))
    with db.Session(db.engine) as session:
        new = db.user(username, password, auth)
        session.add(new)
        session.commit()