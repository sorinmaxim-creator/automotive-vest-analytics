"""
Endpoint-uri pentru indicatori statistici
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

from app.api.dependencies import get_db
from app.models.indicator import (
    IndicatorDefinition,
    IndicatorValue,
    IndicatorCategory,
    AggregationLevel
)

router = APIRouter(prefix="/indicators", tags=["indicators"])


# Schemas Pydantic
class IndicatorBase(BaseModel):
    code: str
    name: str
    category: str
    unit: str
    description: Optional[str] = None


class IndicatorResponse(IndicatorBase):
    id: int
    data_source: Optional[str] = None

    class Config:
        from_attributes = True


class IndicatorValueResponse(BaseModel):
    year: int
    quarter: Optional[int] = None
    value: float
    county_code: Optional[str] = None
    aggregation_level: str
    is_provisional: bool = False

    class Config:
        from_attributes = True


class TimeSeriesResponse(BaseModel):
    indicator_code: str
    indicator_name: str
    unit: str
    data: list[IndicatorValueResponse]


class ComparisonResponse(BaseModel):
    indicator_code: str
    indicator_name: str
    unit: str
    comparisons: dict[str, float]  # {"Timiș": 100, "Arad": 80, ...}


# Endpoints
@router.get("/", response_model=list[IndicatorResponse])
def list_indicators(
    category: Optional[IndicatorCategory] = None,
    db: Session = Depends(get_db)
):
    """
    Listează toți indicatorii disponibili.
    Opțional, filtrare pe categorie.
    """
    query = db.query(IndicatorDefinition)

    if category:
        query = query.filter(IndicatorDefinition.category == category)

    return query.all()


@router.get("/categories")
def list_categories():
    """
    Listează categoriile de indicatori disponibile.
    """
    return [
        {"code": cat.value, "name": cat.name.replace("_", " ").title()}
        for cat in IndicatorCategory
    ]


@router.get("/{indicator_code}", response_model=IndicatorResponse)
def get_indicator(indicator_code: str, db: Session = Depends(get_db)):
    """
    Detalii despre un indicator specific.
    """
    indicator = db.query(IndicatorDefinition).filter(
        IndicatorDefinition.code == indicator_code
    ).first()

    if not indicator:
        raise HTTPException(status_code=404, detail="Indicator not found")

    return indicator


@router.get("/{indicator_code}/timeseries", response_model=TimeSeriesResponse)
def get_indicator_timeseries(
    indicator_code: str,
    county_code: Optional[str] = None,
    aggregation_level: AggregationLevel = AggregationLevel.REGION,
    start_year: int = Query(default=2010, ge=2000, le=2030),
    end_year: int = Query(default=2024, ge=2000, le=2030),
    db: Session = Depends(get_db)
):
    """
    Serie temporală pentru un indicator.
    """
    indicator = db.query(IndicatorDefinition).filter(
        IndicatorDefinition.code == indicator_code
    ).first()

    if not indicator:
        raise HTTPException(status_code=404, detail="Indicator not found")

    query = db.query(IndicatorValue).filter(
        IndicatorValue.indicator_id == indicator.id,
        IndicatorValue.year >= start_year,
        IndicatorValue.year <= end_year,
        IndicatorValue.aggregation_level == aggregation_level
    )

    if county_code:
        query = query.join(IndicatorValue.county).filter_by(code=county_code)

    values = query.order_by(IndicatorValue.year).all()

    return TimeSeriesResponse(
        indicator_code=indicator.code,
        indicator_name=indicator.name,
        unit=indicator.unit.value,
        data=[
            IndicatorValueResponse(
                year=v.year,
                quarter=v.quarter,
                value=v.value,
                county_code=v.county.code if v.county else None,
                aggregation_level=v.aggregation_level.value,
                is_provisional=bool(v.is_provisional)
            )
            for v in values
        ]
    )


@router.get("/{indicator_code}/compare", response_model=ComparisonResponse)
def compare_indicator_by_county(
    indicator_code: str,
    year: int = Query(default=2023, ge=2000, le=2030),
    db: Session = Depends(get_db)
):
    """
    Comparație a unui indicator între județe pentru un an dat.
    """
    indicator = db.query(IndicatorDefinition).filter(
        IndicatorDefinition.code == indicator_code
    ).first()

    if not indicator:
        raise HTTPException(status_code=404, detail="Indicator not found")

    values = db.query(IndicatorValue).filter(
        IndicatorValue.indicator_id == indicator.id,
        IndicatorValue.year == year,
        IndicatorValue.aggregation_level == AggregationLevel.COUNTY
    ).all()

    comparisons = {v.county.name: v.value for v in values if v.county}

    return ComparisonResponse(
        indicator_code=indicator.code,
        indicator_name=indicator.name,
        unit=indicator.unit.value,
        comparisons=comparisons
    )


@router.get("/kpi/summary")
def get_kpi_summary(
    year: int = Query(default=2023, ge=2000, le=2030),
    db: Session = Depends(get_db)
):
    """
    Sumar KPI-uri principale pentru dashboard.
    """
    kpi_codes = [
        "TOTAL_EMPLOYEES",
        "TOTAL_TURNOVER",
        "TOTAL_EXPORTS",
        "PRODUCTIVITY",
        "TOTAL_COMPANIES"
    ]

    kpis = {}
    for code in kpi_codes:
        indicator = db.query(IndicatorDefinition).filter(
            IndicatorDefinition.code == code
        ).first()

        if indicator:
            value = db.query(IndicatorValue).filter(
                IndicatorValue.indicator_id == indicator.id,
                IndicatorValue.year == year,
                IndicatorValue.aggregation_level == AggregationLevel.REGION
            ).first()

            kpis[code] = {
                "name": indicator.name,
                "value": value.value if value else None,
                "unit": indicator.unit.value
            }

    return kpis
