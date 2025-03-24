import os
import sys

# Add the project root to sys.path to allow importing from app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import engine, Base, User
from app.utils.security import get_password_hash
from app.models.user import UserRole

def init_database():
    print("Creating database tables...")
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Verify users table exists
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Tables in database: {tables}")
    
    if "users" in tables:
        print("Users table created successfully!")
    else:
        print("ERROR: Users table was not created!")

    # Optionally create a default admin user
    from sqlalchemy.orm import Session
    with Session(engine) as session:
        # Check if admin user already exists
        admin = session.query(User).filter(User.email == "admin@example.com").first()
        if not admin:
            print("Creating default admin user...")
            admin_user = User(
                email="admin@example.com",
                username="admin",
                hashed_password=get_password_hash("AdminP@ss123"),
                role=UserRole.ADMIN
            )
            session.add(admin_user)
            session.commit()
            print("Default admin user created.")

if __name__ == "__main__":
    init_database()