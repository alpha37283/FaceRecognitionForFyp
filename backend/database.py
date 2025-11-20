# backend/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from backend.config import (
    DATABASE_TYPE,
    POSTGRES_HOST,
    POSTGRES_PORT,
    POSTGRES_DB,
    POSTGRES_USER,
    POSTGRES_PASSWORD,
    MYSQL_HOST,
    MYSQL_PORT,
    MYSQL_DB,
    MYSQL_USER,
    MYSQL_PASSWORD,
)

Base = declarative_base()


def get_database_url():
    if DATABASE_TYPE == "postgresql":
        # Build connection string
        if POSTGRES_PASSWORD:
            return f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
        else:
            return f"postgresql://{POSTGRES_USER}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    elif DATABASE_TYPE == "mysql":
        return f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    else:
        raise ValueError(f"Unsupported database type: {DATABASE_TYPE}. Use 'postgresql' or 'mysql'")


connect_args = {}

if DATABASE_TYPE == "postgresql":
    database_url = get_database_url()
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg2://", 1)
    engine = create_engine(database_url, connect_args=connect_args, echo=False)
else:
    engine = create_engine(get_database_url(), connect_args=connect_args, echo=False)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)

