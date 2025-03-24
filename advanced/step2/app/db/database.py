import os
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Enum, Table, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from app.models.user import UserRole

# Configure SQLAlchemy
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Define SQLAlchemy models
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(Enum(UserRole), default=UserRole.USER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# Create tables
def create_tables():
    """Create database tables"""
    try:
        # Direct table creation approach
        metadata = MetaData()
        
        # Define users table directly if it doesn't exist
        if not engine.dialect.has_table(engine, "users"):
            users = Table(
                "users",
                metadata,
                Column("id", Integer, primary_key=True),
                Column("email", String, unique=True, index=True),
                Column("username", String, unique=True, index=True),
                Column("hashed_password", String),
                Column("role", String),
                Column("is_active", Boolean, default=True),
                Column("created_at", DateTime(timezone=True), server_default=func.now()),
                Column("updated_at", DateTime(timezone=True), onupdate=func.now())
            )
            metadata.create_all(engine)
            print("Created users table directly")
        
        # SQLAlchemy declarative approach
        Base.metadata.create_all(bind=engine)
        print("Created all tables using SQLAlchemy Base")
    except Exception as e:
        print(f"Error creating tables: {e}")
        raise

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()