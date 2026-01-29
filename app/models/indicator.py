"""
Modele pentru indicatori statistici
"""

from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class IndicatorCategory(enum.Enum):
    """Categorii de indicatori"""
    ECONOMIC_STRUCTURE = "structura_economica"
    LABOR_MARKET = "piata_muncii"
    PERFORMANCE = "performanta"
    INNOVATION = "inovare"
    SUSTAINABILITY = "sustenabilitate"
    COMPARATIVE = "comparativ"


class IndicatorUnit(enum.Enum):
    """Unități de măsură"""
    NUMBER = "numar"
    PERCENT = "procent"
    EURO = "euro"
    RON = "ron"
    EURO_PER_EMPLOYEE = "euro_per_angajat"
    INDEX = "indice"
    RATIO = "raport"


class AggregationLevel(enum.Enum):
    """Nivel de agregare"""
    COUNTY = "judet"
    REGION = "regiune"
    COUNTRY = "tara"
    EU = "ue"


class IndicatorDefinition(Base):
    """
    Definiția unui indicator statistic
    """
    __tablename__ = "indicator_definitions"

    id = Column(Integer, primary_key=True, index=True)

    # Identificare
    code = Column(String(50), nullable=False, unique=True)  # ex: "IND_001"
    name = Column(String(200), nullable=False)
    name_en = Column(String(200), nullable=True)  # Nume în engleză

    # Descriere
    description = Column(Text, nullable=True)
    methodology = Column(Text, nullable=True)  # Metodologie de calcul

    # Clasificare
    category = Column(Enum(IndicatorCategory), nullable=False)
    unit = Column(Enum(IndicatorUnit), nullable=False)

    # Sursă
    data_source = Column(String(100), nullable=True)  # ex: "INS", "Eurostat"
    source_code = Column(String(100), nullable=True)  # Cod indicator la sursă

    # Metadate
    is_calculated = Column(Integer, default=0)  # 1 dacă e calculat din alți indicatori
    formula = Column(Text, nullable=True)  # Formula de calcul (dacă e cazul)
    update_frequency = Column(String(50), nullable=True)  # ex: "anual", "trimestrial"

    # Praguri pentru alerte
    warning_threshold_low = Column(Float, nullable=True)
    warning_threshold_high = Column(Float, nullable=True)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Relații
    values = relationship("IndicatorValue", back_populates="indicator")

    def __repr__(self):
        return f"<IndicatorDefinition(code='{self.code}', name='{self.name}')>"


class IndicatorValue(Base):
    """
    Valoare a unui indicator pentru un an și locație specifică
    """
    __tablename__ = "indicator_values"

    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    indicator_id = Column(Integer, ForeignKey("indicator_definitions.id"), nullable=False)
    county_id = Column(Integer, ForeignKey("counties.id"), nullable=True)  # Null pentru nivel regional/național

    # Dimensiuni temporale
    year = Column(Integer, nullable=False, index=True)
    quarter = Column(Integer, nullable=True)  # 1-4, null pentru date anuale

    # Nivel de agregare
    aggregation_level = Column(Enum(AggregationLevel), nullable=False, default=AggregationLevel.COUNTY)

    # Valoarea propriu-zisă
    value = Column(Float, nullable=False)

    # Metadate despre valoare
    is_provisional = Column(Integer, default=0)  # Date provizorii
    is_estimated = Column(Integer, default=0)  # Date estimate/interpolate
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Relații
    indicator = relationship("IndicatorDefinition", back_populates="values")
    county = relationship("County", back_populates="indicator_values")

    def __repr__(self):
        return f"<IndicatorValue(indicator_id={self.indicator_id}, year={self.year}, value={self.value})>"
