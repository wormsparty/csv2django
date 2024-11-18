from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base
SQLALCHEMY_DATABASE_URL = 'sqlite:///./test.db'

# Connect to the database
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=engine)
