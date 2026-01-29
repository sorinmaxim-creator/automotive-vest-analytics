"""
Modele pentru regiuni și județe
"""

from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class Region(Base):
    """
    Regiune de dezvoltare (ex: Regiunea Vest)
    """
    __tablename__ = "regions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    code = Column(String(10), nullable=False, unique=True)  # ex: "RO42" pentru Vest

    # Coordonate pentru centrul regiunii (pentru hărți)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # Relații
    counties = relationship("County", back_populates="region")

    def __repr__(self):
        return f"<Region(name='{self.name}', code='{self.code}')>"


class County(Base):
    """
    Județ din cadrul unei regiuni
    """
    __tablename__ = "counties"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(10), nullable=False, unique=True)  # ex: "TM", "AR"

    # Foreign key către regiune
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=False)

    # Coordonate pentru centrul județului
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # Populație și suprafață (date de bază)
    population = Column(Integer, nullable=True)
    area_km2 = Column(Float, nullable=True)

    # Flag pentru județe cu activitate automotive semnificativă
    is_automotive_hub = Column(Boolean, default=False)

    # Relații
    region = relationship("Region", back_populates="counties")
    indicator_values = relationship("IndicatorValue", back_populates="county")
    companies = relationship("Company", back_populates="county")

    def __repr__(self):
        return f"<County(name='{self.name}', code='{self.code}')>"
