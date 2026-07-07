from server.app.database import SessionLocal, engine, Base
from server.app.models import User

# This recreates the database with the NEW structure
Base.metadata.create_all(bind=engine)

def create_admin():
    db = SessionLocal()
    # Check if exists
    exists = db.query(User).filter(User.username == "admin").first()
    if not exists:
        new_admin = User(
            full_name="Mustaquim Ahmad",
            user_id_code="IT-001",
            username="admin", 
            hashed_password="201503" 
        )
        db.add(new_admin)
        db.commit()
        print("✅ NEW IT AUTHORITY REGISTERED!")
        print("Username: admin")
        print("Password: 201503")
    else:
        print("Admin already exists.")
    db.close()

if __name__ == "__main__":
    create_admin()