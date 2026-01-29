"""
Serviciu pentru importul datelor din surse externe
"""

import pandas as pd
import requests
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.indicator import IndicatorDefinition, IndicatorValue, AggregationLevel
from app.models.region import Region, County
from app.config import settings


class DataImportService:
    """
    Serviciu pentru importul și actualizarea datelor din surse externe.
    Surse suportate: INS (Tempo Online), Eurostat, fișiere locale.
    """

    def __init__(self, db: Session):
        self.db = db

    # ==================== INS TEMPO ONLINE ====================

    def import_from_ins_tempo(
        self,
        matrix_code: str,
        indicator_code: str,
        filters: Optional[dict] = None
    ) -> int:
        """
        Importă date din INS Tempo Online.

        Args:
            matrix_code: Codul matricei INS (ex: "FOM104A")
            indicator_code: Codul indicatorului intern
            filters: Filtre pentru selecția datelor

        Returns:
            Numărul de înregistrări importate
        """
        # INS Tempo API base URL
        base_url = "http://statistici.insse.ro:8077/tempo-ins/matrix"

        try:
            # Get matrix metadata
            response = requests.get(f"{base_url}/{matrix_code}")
            response.raise_for_status()

            # Parse and import data
            # Implementare specifică pentru structura INS
            # ...

            return 0  # Placeholder

        except requests.RequestException as e:
            print(f"Error fetching INS data: {e}")
            return 0

    # ==================== EUROSTAT ====================

    def import_from_eurostat(
        self,
        dataset_code: str,
        indicator_code: str,
        geo_filter: str = "RO",
        time_filter: Optional[tuple] = None
    ) -> int:
        """
        Importă date din Eurostat.

        Args:
            dataset_code: Codul datasetului Eurostat (ex: "nama_10_a64")
            indicator_code: Codul indicatorului intern
            geo_filter: Filtru geografic (cod țară/regiune)
            time_filter: Tuple (start_year, end_year)

        Returns:
            Numărul de înregistrări importate
        """
        try:
            import eurostat

            # Fetch data from Eurostat
            df = eurostat.get_data_df(dataset_code)

            if df is None or df.empty:
                return 0

            # Filter by geography
            if "geo" in df.columns:
                df = df[df["geo"].str.contains(geo_filter, na=False)]

            # Filter by time
            if time_filter:
                start_year, end_year = time_filter
                # Eurostat uses different time column names
                time_cols = [c for c in df.columns if c.startswith("20") or c.startswith("19")]
                df = df[["geo"] + [c for c in time_cols if start_year <= int(c) <= end_year]]

            # Get indicator definition
            indicator = self.db.query(IndicatorDefinition).filter(
                IndicatorDefinition.code == indicator_code
            ).first()

            if not indicator:
                print(f"Indicator {indicator_code} not found")
                return 0

            # Import values
            count = 0
            for _, row in df.iterrows():
                for col in df.columns:
                    if col.isdigit():
                        year = int(col)
                        value = row[col]

                        if pd.notna(value):
                            self._upsert_indicator_value(
                                indicator_id=indicator.id,
                                year=year,
                                value=float(value),
                                aggregation_level=AggregationLevel.COUNTRY
                            )
                            count += 1

            self.db.commit()
            return count

        except Exception as e:
            print(f"Error importing from Eurostat: {e}")
            self.db.rollback()
            return 0

    # ==================== LOCAL FILES ====================

    def import_from_csv(
        self,
        file_path: str,
        indicator_code: str,
        year_column: str = "year",
        value_column: str = "value",
        county_column: Optional[str] = None
    ) -> int:
        """
        Importă date dintr-un fișier CSV local.

        Args:
            file_path: Calea către fișierul CSV
            indicator_code: Codul indicatorului intern
            year_column: Numele coloanei pentru an
            value_column: Numele coloanei pentru valoare
            county_column: Numele coloanei pentru județ (opțional)

        Returns:
            Numărul de înregistrări importate
        """
        try:
            df = pd.read_csv(file_path)

            indicator = self.db.query(IndicatorDefinition).filter(
                IndicatorDefinition.code == indicator_code
            ).first()

            if not indicator:
                print(f"Indicator {indicator_code} not found")
                return 0

            count = 0
            for _, row in df.iterrows():
                year = int(row[year_column])
                value = float(row[value_column])

                county_id = None
                aggregation_level = AggregationLevel.REGION

                if county_column and county_column in row:
                    county_code = row[county_column]
                    county = self.db.query(County).filter(
                        County.code == county_code
                    ).first()
                    if county:
                        county_id = county.id
                        aggregation_level = AggregationLevel.COUNTY

                self._upsert_indicator_value(
                    indicator_id=indicator.id,
                    year=year,
                    value=value,
                    county_id=county_id,
                    aggregation_level=aggregation_level
                )
                count += 1

            self.db.commit()
            return count

        except Exception as e:
            print(f"Error importing from CSV: {e}")
            self.db.rollback()
            return 0

    def import_from_excel(
        self,
        file_path: str,
        sheet_name: str,
        indicator_code: str,
        year_column: str = "An",
        value_column: str = "Valoare",
        county_column: Optional[str] = None
    ) -> int:
        """
        Importă date dintr-un fișier Excel.
        """
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            # Similar logic to CSV import
            return self._import_dataframe(
                df, indicator_code, year_column, value_column, county_column
            )
        except Exception as e:
            print(f"Error importing from Excel: {e}")
            return 0

    # ==================== HELPER METHODS ====================

    def _upsert_indicator_value(
        self,
        indicator_id: int,
        year: int,
        value: float,
        county_id: Optional[int] = None,
        aggregation_level: AggregationLevel = AggregationLevel.REGION,
        quarter: Optional[int] = None,
        is_provisional: bool = False
    ):
        """
        Insert or update an indicator value.
        """
        existing = self.db.query(IndicatorValue).filter(
            IndicatorValue.indicator_id == indicator_id,
            IndicatorValue.year == year,
            IndicatorValue.county_id == county_id,
            IndicatorValue.aggregation_level == aggregation_level
        )

        if quarter:
            existing = existing.filter(IndicatorValue.quarter == quarter)

        existing = existing.first()

        if existing:
            existing.value = value
            existing.is_provisional = int(is_provisional)
        else:
            new_value = IndicatorValue(
                indicator_id=indicator_id,
                year=year,
                value=value,
                county_id=county_id,
                aggregation_level=aggregation_level,
                quarter=quarter,
                is_provisional=int(is_provisional)
            )
            self.db.add(new_value)

    def _import_dataframe(
        self,
        df: pd.DataFrame,
        indicator_code: str,
        year_column: str,
        value_column: str,
        county_column: Optional[str] = None
    ) -> int:
        """
        Helper method to import a DataFrame.
        """
        indicator = self.db.query(IndicatorDefinition).filter(
            IndicatorDefinition.code == indicator_code
        ).first()

        if not indicator:
            return 0

        count = 0
        for _, row in df.iterrows():
            try:
                year = int(row[year_column])
                value = float(row[value_column])

                county_id = None
                aggregation_level = AggregationLevel.REGION

                if county_column and pd.notna(row.get(county_column)):
                    county = self.db.query(County).filter(
                        County.code == str(row[county_column])
                    ).first()
                    if county:
                        county_id = county.id
                        aggregation_level = AggregationLevel.COUNTY

                self._upsert_indicator_value(
                    indicator_id=indicator.id,
                    year=year,
                    value=value,
                    county_id=county_id,
                    aggregation_level=aggregation_level
                )
                count += 1
            except (ValueError, KeyError) as e:
                continue

        self.db.commit()
        return count

    def validate_import(self, indicator_code: str) -> dict:
        """
        Validează datele importate pentru un indicator.
        """
        indicator = self.db.query(IndicatorDefinition).filter(
            IndicatorDefinition.code == indicator_code
        ).first()

        if not indicator:
            return {"error": "Indicator not found"}

        values = self.db.query(IndicatorValue).filter(
            IndicatorValue.indicator_id == indicator.id
        ).all()

        years = [v.year for v in values]

        return {
            "indicator_code": indicator_code,
            "total_records": len(values),
            "year_range": (min(years), max(years)) if years else None,
            "missing_years": self._find_missing_years(years),
            "null_values": sum(1 for v in values if v.value is None),
            "negative_values": sum(1 for v in values if v.value and v.value < 0)
        }

    def _find_missing_years(self, years: list[int]) -> list[int]:
        """Find missing years in a sequence."""
        if not years:
            return []
        full_range = set(range(min(years), max(years) + 1))
        return sorted(full_range - set(years))
