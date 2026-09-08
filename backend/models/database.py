from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from config import settings

# 1. Create the SQLAlchemy engine
# This establishes the core connection to PostgreSQL database
engine = create_engine(settings.DATABASE_URL)

# 2. Create a configured "Session" class
# autocommit=False and autoflush=False let us manually control when to save changes
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. Create a Base class
# All your future database models (like User) will inherit from this
Base = declarative_base()

# 4. Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()