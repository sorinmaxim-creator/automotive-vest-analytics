"""
Endpoint-uri pentru generare rapoarte
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
import io

from app.api.dependencies import get_db
from app.models.indicator import IndicatorDefinition, IndicatorValue, AggregationLevel
from app.models.region import Region, County

router = APIRouter(prefix="/reports", tags=["reports"])


# Schemas
class ReportRequest(BaseModel):
    title: str
    year: int
    county_codes: Optional[list[str]] = None
    indicator_codes: Optional[list[str]] = None
    include_charts: bool = True


class ReportMetadata(BaseModel):
    id: str
    title: str
    generated_at: datetime
    year: int
    format: str


# Endpoints
@router.get("/templates")
def list_report_templates():
    """
    Listează șabloanele de rapoarte disponibile.
    """
    return [
        {
            "id": "quarterly_summary",
            "name": "Raport Trimestrial Sumar",
            "description": "Sumar al principalilor indicatori pentru trimestrul curent"
        },
        {
            "id": "annual_full",
            "name": "Raport Anual Complet",
            "description": "Analiză completă a sectorului automotive pe anul selectat"
        },
        {
            "id": "county_comparison",
            "name": "Comparație Județe",
            "description": "Comparație detaliată între județele Regiunii Vest"
        },
        {
            "id": "trend_analysis",
            "name": "Analiză Tendințe",
            "description": "Evoluția indicatorilor pe ultimii 5 ani"
        },
        {
            "id": "kpi_dashboard",
            "name": "Dashboard KPI",
            "description": "Principalii indicatori de performanță"
        }
    ]


@router.get("/export/excel")
def export_to_excel(
    year: int = Query(default=2023, ge=2000, le=2030),
    indicator_codes: Optional[str] = None,  # comma-separated
    db: Session = Depends(get_db)
):
    """
    Exportă datele în format Excel.
    """
    import pandas as pd
    from io import BytesIO

    # Parse indicator codes
    codes = indicator_codes.split(",") if indicator_codes else None

    # Query data
    query = db.query(
        IndicatorDefinition.code,
        IndicatorDefinition.name,
        IndicatorValue.year,
        IndicatorValue.value,
        County.name.label("county_name")
    ).join(
        IndicatorValue, IndicatorDefinition.id == IndicatorValue.indicator_id
    ).outerjoin(
        County, IndicatorValue.county_id == County.id
    ).filter(
        IndicatorValue.year == year
    )

    if codes:
        query = query.filter(IndicatorDefinition.code.in_(codes))

    results = query.all()

    # Create DataFrame
    df = pd.DataFrame(results, columns=["Cod", "Indicator", "An", "Valoare", "Județ"])

    # Write to Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Date', index=False)

    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=automotive_vest_{year}.xlsx"
        }
    )


@router.get("/export/csv")
def export_to_csv(
    year: int = Query(default=2023, ge=2000, le=2030),
    indicator_code: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Exportă datele în format CSV.
    """
    import csv
    from io import StringIO

    query = db.query(
        IndicatorDefinition.code,
        IndicatorDefinition.name,
        IndicatorValue.year,
        IndicatorValue.value,
        County.name.label("county_name")
    ).join(
        IndicatorValue, IndicatorDefinition.id == IndicatorValue.indicator_id
    ).outerjoin(
        County, IndicatorValue.county_id == County.id
    ).filter(
        IndicatorValue.year == year
    )

    if indicator_code:
        query = query.filter(IndicatorDefinition.code == indicator_code)

    results = query.all()

    # Create CSV
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Cod", "Indicator", "An", "Valoare", "Județ"])

    for row in results:
        writer.writerow(row)

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=automotive_vest_{year}.csv"
        }
    )


@router.post("/generate")
def generate_report(request: ReportRequest, db: Session = Depends(get_db)):
    """
    Generează un raport personalizat.
    Returnează metadata raportului și URL pentru descărcare.
    """
    import uuid

    report_id = str(uuid.uuid4())

    # În implementarea completă, aici s-ar genera efectiv raportul
    # și s-ar salva pentru descărcare ulterioară

    return {
        "report_id": report_id,
        "status": "generated",
        "download_url": f"/api/v1/reports/download/{report_id}",
        "metadata": ReportMetadata(
            id=report_id,
            title=request.title,
            generated_at=datetime.now(),
            year=request.year,
            format="pdf"
        )
    }


@router.get("/summary/{year}")
def get_annual_summary(year: int, db: Session = Depends(get_db)):
    """
    Sumar anual pentru afișare rapidă în dashboard.
    """
    # Query pentru indicatorii principali
    summary_indicators = [
        "TOTAL_COMPANIES",
        "TOTAL_EMPLOYEES",
        "TOTAL_TURNOVER",
        "TOTAL_EXPORTS",
        "PRODUCTIVITY"
    ]

    summary = {
        "year": year,
        "region": "Regiunea Vest",
        "indicators": {},
        "generated_at": datetime.now().isoformat()
    }

    for code in summary_indicators:
        indicator = db.query(IndicatorDefinition).filter(
            IndicatorDefinition.code == code
        ).first()

        if indicator:
            value = db.query(IndicatorValue).filter(
                IndicatorValue.indicator_id == indicator.id,
                IndicatorValue.year == year,
                IndicatorValue.aggregation_level == AggregationLevel.REGION
            ).first()

            # Get previous year for comparison
            prev_value = db.query(IndicatorValue).filter(
                IndicatorValue.indicator_id == indicator.id,
                IndicatorValue.year == year - 1,
                IndicatorValue.aggregation_level == AggregationLevel.REGION
            ).first()

            change_pct = None
            if value and prev_value and prev_value.value != 0:
                change_pct = ((value.value - prev_value.value) / prev_value.value) * 100

            summary["indicators"][code] = {
                "name": indicator.name,
                "value": value.value if value else None,
                "unit": indicator.unit.value,
                "change_pct": round(change_pct, 2) if change_pct else None
            }

    return summary
