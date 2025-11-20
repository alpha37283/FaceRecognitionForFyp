# backend/database.py
"""
Database connection and session management
"""
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
    """Get database URL based on configuration"""
    if DATABASE_TYPE == "postgresql":
        # Build connection string
        if POSTGRES_PASSWORD:
            return f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
        else:
            # For local PostgreSQL with peer/ident authentication (no password in URL)
            # SQLAlchemy will use system authentication
            return f"postgresql://{POSTGRES_USER}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    elif DATABASE_TYPE == "mysql":
        return f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    else:
        raise ValueError(f"Unsupported database type: {DATABASE_TYPE}. Use 'postgresql' or 'mysql'")


# Create engine
connect_args = {}
if DATABASE_TYPE == "postgresql":
    # PostgreSQL connection arguments
    # For peer authentication, we don't need password in connection string
    # The system will use the current user's authentication
    connect_args = {}
    # If password is provided, it will be in the URL
elif DATABASE_TYPE == "mysql":
    # MySQL connection arguments
    connect_args = {}

# Use psycopg2 driver for PostgreSQL
if DATABASE_TYPE == "postgresql":
    database_url = get_database_url()
    # Replace postgresql:// with postgresql+psycopg2:// for SQLAlchemy
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg2://", 1)
    engine = create_engine(
        database_url,
        connect_args=connect_args,
        echo=False  # Set to True for SQL query logging
    )
else:
    engine = create_engine(
        get_database_url(),
        connect_args=connect_args,
        echo=False  # Set to True for SQL query logging
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database - create all tables"""
    Base.metadata.create_all(bind=engine)

