from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()


# Read the database URL
DATABASE_URL = os.getenv("DATABASE_URL")

# Ensure it's loaded
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set. Check your .env file.")

# Set up SQLAlchemy engine and base
engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
