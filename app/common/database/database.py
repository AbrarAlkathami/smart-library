from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker , declarative_base

# Fetch database URL from environment variables
# DATABASE_URL = "postgresql://postgres:password@localhost:5432/Bookstore"
DATABASE_URL = "postgresql://aalkathami001:Passw0rd@localhost:5432/postgres"

engine = create_engine(DATABASE_URL)
session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()
