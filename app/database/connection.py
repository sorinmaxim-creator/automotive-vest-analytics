"""
Conexiune la baza de date PostgreSQL
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# Engine SQLAlchemy
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class pentru modele
Base = declarative_base()


def get_db():
    """
    Dependency pentru obținerea sesiunii de bază de date.
    Folosit în FastAPI cu Depends().
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Inițializare bază de date - creare tabele.
    """
    Base.metadata.create_all(bind=engine)
