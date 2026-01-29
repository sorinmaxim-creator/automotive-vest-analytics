"""
Modele pentru companii și sectoare
"""

from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class CompanySector(Base):
    """
    Subsector din industria automotive
    """
    __tablename__ = "company_sectors"

    id = Column(Integer, primary_key=True, index=True)

    # Identificare CAEN
    caen_code = Column(String(10), nullable=False, unique=True)
    caen_name = Column(String(200), nullable=False)

    # Clasificare internă
    subsector = Column(String(100), nullable=True)  # ex: "componente", "asamblare", "R&D"
    is_automotive = Column(Boolean, default=True)

    # Descriere
    description = Column(Text, nullable=True)

    # Relații
    companies = relationship("Company", back_populates="sector")

    def __repr__(self):
        return f"<CompanySector(caen_code='{self.caen_code}', name='{self.caen_name}')>"


class Company(Base):
    """
    Firmă din sectorul automotive (date agregate, nu individuale)
    Folosit pentru analize de concentrare și structură
    """
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)

    # Identificare (anonimizată pentru date publice)
    company_id = Column(String(50), nullable=False, unique=True)  # ID intern, nu CUI

    # Localizare
    county_id = Column(Integer, ForeignKey("counties.id"), nullable=False)

    # Sector
    sector_id = Column(Integer, ForeignKey("company_sectors.id"), nullable=False)

    # Dimensiune (clasă)
    size_class = Column(String(20), nullable=True)  # "micro", "mica", "medie", "mare"

    # Date agregate (ultimul an disponibil)
    employees_count = Column(Integer, nullable=True)
    turnover = Column(Float, nullable=True)  # Cifră de afaceri
    year_data = Column(Integer, nullable=True)  # Anul datelor

    # Caracteristici
    is_foreign_owned = Column(Boolean, nullable=True)
    is_exporter = Column(Boolean, nullable=True)
    has_rd_activity = Column(Boolean, nullable=True)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Relații
    county = relationship("County", back_populates="companies")
    sector = relationship("CompanySector", back_populates="companies")

    def __repr__(self):
        return f"<Company(id='{self.company_id}', county_id={self.county_id})>"


class AggregatedCompanyData(Base):
    """
    Date agregate despre firme pe județ/an
    Pentru a evita stocarea datelor individuale sensibile
    """
    __tablename__ = "aggregated_company_data"

    id = Column(Integer, primary_key=True, index=True)

    # Dimensiuni
    county_id = Column(Integer, ForeignKey("counties.id"), nullable=False)
    sector_id = Column(Integer, ForeignKey("company_sectors.id"), nullable=True)
    year = Column(Integer, nullable=False, index=True)

    # Metrici agregate
    total_companies = Column(Integer, nullable=True)
    total_employees = Column(Integer, nullable=True)
    total_turnover = Column(Float, nullable=True)
    average_employees = Column(Float, nullable=True)
    average_turnover = Column(Float, nullable=True)

    # Distribuție pe dimensiune
    micro_companies = Column(Integer, nullable=True)  # <10 angajați
    small_companies = Column(Integer, nullable=True)  # 10-49
    medium_companies = Column(Integer, nullable=True)  # 50-249
    large_companies = Column(Integer, nullable=True)  # 250+

    # Indicatori derivați
    hhi_index = Column(Float, nullable=True)  # Indice Herfindahl-Hirschman
    concentration_ratio_top5 = Column(Float, nullable=True)  # CR5

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    def __repr__(self):
        return f"<AggregatedCompanyData(county_id={self.county_id}, year={self.year})>"
