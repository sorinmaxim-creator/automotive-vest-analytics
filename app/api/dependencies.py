"""
Dependențe comune pentru API
"""

from typing import Generator
from sqlalchemy.orm import Session
from app.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Dependency pentru obținerea sesiunii de bază de date.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
