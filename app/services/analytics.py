"""
Serviciu pentru calcule și analize statistice
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Optional
from sqlalchemy.orm import Session

from app.models.indicator import IndicatorDefinition, IndicatorValue, AggregationLevel
from app.models.region import County


class AnalyticsService:
    """
    Serviciu pentru analize statistice și calcule derivate.
    """

    def __init__(self, db: Session):
        self.db = db

    def calculate_productivity(
        self,
        value_added: float,
        employees: int
    ) -> float:
        """
        Calculează productivitatea muncii.
        Productivitate = Valoare Adăugată / Număr Angajați
        """
        if employees == 0:
            return 0.0
        return value_added / employees

    def calculate_hhi(self, market_shares: list[float]) -> float:
        """
        Calculează indicele Herfindahl-Hirschman (HHI).
        HHI = Σ(si²) unde si este cota de piață a firmei i

        Interpretare:
        - HHI < 1500: Piață competitivă
        - 1500 ≤ HHI < 2500: Concentrare moderată
        - HHI ≥ 2500: Concentrare ridicată
        """
        return sum(s ** 2 for s in market_shares)

    def calculate_location_quotient(
        self,
        regional_sector_employment: int,
        regional_total_employment: int,
        national_sector_employment: int,
        national_total_employment: int
    ) -> float:
        """
        Calculează coeficientul de localizare (Location Quotient - LQ).

        LQ > 1: Specializare regională în sector
        LQ = 1: Proporție egală cu media națională
        LQ < 1: Subreprezentare regională
        """
        if regional_total_employment == 0 or national_total_employment == 0:
            return 0.0

        regional_share = regional_sector_employment / regional_total_employment
        national_share = national_sector_employment / national_total_employment

        if national_share == 0:
            return 0.0

        return regional_share / national_share

    def calculate_growth_rate(
        self,
        current_value: float,
        previous_value: float
    ) -> float:
        """
        Calculează rata de creștere procentuală.
        """
        if previous_value == 0:
            return 0.0
        return ((current_value - previous_value) / previous_value) * 100

    def calculate_cagr(
        self,
        start_value: float,
        end_value: float,
        years: int
    ) -> float:
        """
        Calculează rata de creștere anuală compusă (CAGR).
        CAGR = (End Value / Start Value)^(1/n) - 1
        """
        if start_value <= 0 or years <= 0:
            return 0.0
        return (pow(end_value / start_value, 1 / years) - 1) * 100

    def get_timeseries_stats(
        self,
        indicator_code: str,
        county_code: Optional[str] = None,
        start_year: int = 2010,
        end_year: int = 2024
    ) -> dict:
        """
        Calculează statistici descriptive pentru o serie temporală.
        """
        indicator = self.db.query(IndicatorDefinition).filter(
            IndicatorDefinition.code == indicator_code
        ).first()

        if not indicator:
            return {}

        query = self.db.query(IndicatorValue.value).filter(
            IndicatorValue.indicator_id == indicator.id,
            IndicatorValue.year >= start_year,
            IndicatorValue.year <= end_year
        )

        if county_code:
            query = query.join(County).filter(County.code == county_code)

        values = [v[0] for v in query.all()]

        if not values:
            return {}

        arr = np.array(values)

        return {
            "count": len(values),
            "mean": float(np.mean(arr)),
            "median": float(np.median(arr)),
            "std": float(np.std(arr)),
            "min": float(np.min(arr)),
            "max": float(np.max(arr)),
            "range": float(np.max(arr) - np.min(arr)),
            "cv": float(np.std(arr) / np.mean(arr) * 100) if np.mean(arr) != 0 else 0
        }

    def calculate_correlation(
        self,
        indicator_code_1: str,
        indicator_code_2: str,
        start_year: int = 2010,
        end_year: int = 2024
    ) -> dict:
        """
        Calculează corelația între doi indicatori.
        """
        ind1 = self.db.query(IndicatorDefinition).filter(
            IndicatorDefinition.code == indicator_code_1
        ).first()
        ind2 = self.db.query(IndicatorDefinition).filter(
            IndicatorDefinition.code == indicator_code_2
        ).first()

        if not ind1 or not ind2:
            return {"error": "Indicator not found"}

        # Get values for both indicators
        values1 = self.db.query(
            IndicatorValue.year, IndicatorValue.value
        ).filter(
            IndicatorValue.indicator_id == ind1.id,
            IndicatorValue.year >= start_year,
            IndicatorValue.year <= end_year,
            IndicatorValue.aggregation_level == AggregationLevel.REGION
        ).all()

        values2 = self.db.query(
            IndicatorValue.year, IndicatorValue.value
        ).filter(
            IndicatorValue.indicator_id == ind2.id,
            IndicatorValue.year >= start_year,
            IndicatorValue.year <= end_year,
            IndicatorValue.aggregation_level == AggregationLevel.REGION
        ).all()

        # Align by year
        dict1 = {v.year: v.value for v in values1}
        dict2 = {v.year: v.value for v in values2}

        common_years = set(dict1.keys()) & set(dict2.keys())

        if len(common_years) < 3:
            return {"error": "Not enough data points"}

        arr1 = np.array([dict1[y] for y in sorted(common_years)])
        arr2 = np.array([dict2[y] for y in sorted(common_years)])

        correlation, p_value = stats.pearsonr(arr1, arr2)

        return {
            "indicator_1": indicator_code_1,
            "indicator_2": indicator_code_2,
            "correlation": round(correlation, 4),
            "p_value": round(p_value, 4),
            "n_observations": len(common_years),
            "interpretation": self._interpret_correlation(correlation)
        }

    def _interpret_correlation(self, r: float) -> str:
        """Interpretare corelație Pearson."""
        abs_r = abs(r)
        direction = "pozitivă" if r > 0 else "negativă"

        if abs_r < 0.1:
            return "Fără corelație semnificativă"
        elif abs_r < 0.3:
            return f"Corelație {direction} slabă"
        elif abs_r < 0.5:
            return f"Corelație {direction} moderată"
        elif abs_r < 0.7:
            return f"Corelație {direction} puternică"
        else:
            return f"Corelație {direction} foarte puternică"

    def forecast_simple(
        self,
        indicator_code: str,
        years_ahead: int = 3,
        method: str = "linear"
    ) -> dict:
        """
        Prognoză simplă bazată pe trend.

        Metode disponibile:
        - linear: Regresie liniară
        - average: Media ultimilor 3 ani
        """
        indicator = self.db.query(IndicatorDefinition).filter(
            IndicatorDefinition.code == indicator_code
        ).first()

        if not indicator:
            return {"error": "Indicator not found"}

        values = self.db.query(
            IndicatorValue.year, IndicatorValue.value
        ).filter(
            IndicatorValue.indicator_id == indicator.id,
            IndicatorValue.aggregation_level == AggregationLevel.REGION
        ).order_by(IndicatorValue.year).all()

        if len(values) < 5:
            return {"error": "Not enough historical data"}

        years = np.array([v.year for v in values])
        vals = np.array([v.value for v in values])

        last_year = int(years[-1])
        forecast_years = list(range(last_year + 1, last_year + years_ahead + 1))

        if method == "linear":
            slope, intercept, r_value, _, _ = stats.linregress(years, vals)
            forecast_values = [slope * y + intercept for y in forecast_years]
            confidence = r_value ** 2
        else:  # average
            avg = np.mean(vals[-3:])
            forecast_values = [avg] * years_ahead
            confidence = 0.5

        return {
            "indicator": indicator_code,
            "method": method,
            "historical_years": years.tolist(),
            "historical_values": vals.tolist(),
            "forecast_years": forecast_years,
            "forecast_values": [round(v, 2) for v in forecast_values],
            "confidence": round(confidence, 2)
        }

    def compare_counties(
        self,
        indicator_code: str,
        year: int = 2023
    ) -> dict:
        """
        Comparație între județe pentru un indicator.
        """
        indicator = self.db.query(IndicatorDefinition).filter(
            IndicatorDefinition.code == indicator_code
        ).first()

        if not indicator:
            return {"error": "Indicator not found"}

        values = self.db.query(
            County.name,
            County.code,
            IndicatorValue.value
        ).join(
            IndicatorValue, County.id == IndicatorValue.county_id
        ).filter(
            IndicatorValue.indicator_id == indicator.id,
            IndicatorValue.year == year
        ).all()

        if not values:
            return {"error": "No data available"}

        data = {v.code: {"name": v.name, "value": v.value} for v in values}

        # Calculate regional average
        avg = np.mean([v.value for v in values])

        # Add comparison to average
        for code in data:
            data[code]["vs_average"] = round(
                ((data[code]["value"] - avg) / avg) * 100, 2
            ) if avg != 0 else 0

        return {
            "indicator": indicator_code,
            "indicator_name": indicator.name,
            "year": year,
            "unit": indicator.unit.value,
            "regional_average": round(avg, 2),
            "counties": data
        }
