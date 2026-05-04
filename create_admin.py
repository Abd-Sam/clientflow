from app import app, db, User
import getpass 
from werkzeug.security import generate_password_hash

username = input("Username: ")
password = getpass.getpass("Password: ")



with app.app_context():
    existing = User.query.filter_by(username=username).first()
    if existing:
        print(f"{username} already exists in the database.")
    else:
        password_hash = generate_password_hash(password)
        new_user=User(username=username, password_hash=password_hash)
        db.session.add(new_user)
        db.session.commit()
        print(f"Admin user '{username}' created.")