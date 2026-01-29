"""
Script pentru importul datelor din INS (Institutul Național de Statistică)
Tempo Online: http://statistici.insse.ro:8077/tempo-online/
"""

import sys
sys.path.insert(0, '/Users/sorinmaxim/Documents/Proiecte/Vestpolicylab.org/automotive-vest-analytics')

import requests
import pandas as pd
from typing import Optional
from datetime import datetime

from app.database import SessionLocal, init_db
from app.models.indicator import IndicatorDefinition, IndicatorValue, AggregationLevel
from app.models.region import County


# INS Tempo Online API Base URL
TEMPO_BASE_URL = "http://statistici.insse.ro:8077/tempo-ins"


# Mapare matrice INS -> indicator intern
INS_INDICATOR_MAPPING = {
    # Angajați în industrie
    "FOM104A": {
        "indicator_code": "TOTAL_EMPLOYEES",
        "description": "Efectivul salariaților la sfârșitul lunii"
    },
    # Câștiguri salariale
    "FOM106E": {
        "indicator_code": "AVG_SALARY",
        "description": "Câștigul salarial mediu brut lunar"
    },
    # Cifra de afaceri
    "INT101A": {
        "indicator_code": "TOTAL_TURNOVER",
        "description": "Cifra de afaceri din industrie"
    },
    # Export
    "EXP101A": {
        "indicator_code": "TOTAL_EXPORTS",
        "description": "Exporturi FOB"
    },
    # Număr firme
    "INT102J": {
        "indicator_code": "TOTAL_COMPANIES",
        "description": "Numărul de întreprinderi active"
    }
}

# Coduri CAEN pentru automotive
AUTOMOTIVE_CAEN = ["29", "2910", "2920", "2931", "2932"]

# Coduri județe INS
COUNTY_CODES_INS = {
    "TM": "Timiș",
    "AR": "Arad",
    "HD": "Hunedoara",
    "CS": "Caraș-Severin"
}


class INSDataImporter:
    """
    Importator de date din INS Tempo Online.
    """

    def __init__(self, db_session):
        self.db = db_session
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "AutomotiveVestAnalytics/1.0"
        })

    def get_matrix_metadata(self, matrix_code: str) -> Optional[dict]:
        """
        Obține metadata pentru o matrice INS.
        """
        try:
            url = f"{TEMPO_BASE_URL}/matrix/{matrix_code}"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching metadata for {matrix_code}: {e}")
            return None

    def fetch_data(
        self,
        matrix_code: str,
        dimensions: dict,
        start_year: int = 2010,
        end_year: int = 2024
    ) -> Optional[pd.DataFrame]:
        """
        Extrage date dintr-o matrice INS.

        Args:
            matrix_code: Codul matricei (ex: "FOM104A")
            dimensions: Dict cu dimensiuni și valori filtrate
            start_year: Anul de început
            end_year: Anul de sfârșit

        Returns:
            DataFrame cu datele extrase
        """
        try:
            # Construire query
            url = f"{TEMPO_BASE_URL}/matrix/{matrix_code}/data"

            params = {
                "lang": "ro",
                "format": "json"
            }

            # Adaugă filtre pentru dimensiuni
            for dim_code, values in dimensions.items():
                if isinstance(values, list):
                    params[dim_code] = ",".join(values)
                else:
                    params[dim_code] = values

            # Filtru ani
            years = [str(y) for y in range(start_year, end_year + 1)]
            params["PERIOADE"] = ",".join(years)

            response = self.session.get(url, params=params, timeout=60)
            response.raise_for_status()

            data = response.json()

            # Parsare date în DataFrame
            if "cells" in data:
                df = pd.DataFrame(data["cells"])
                return df

            return None

        except requests.RequestException as e:
            print(f"Error fetching data for {matrix_code}: {e}")
            return None

    def import_employees_data(
        self,
        start_year: int = 2010,
        end_year: int = 2024
    ) -> int:
        """
        Importă datele despre angajați din matricea FOM104A.
        """
        print(f"Importing employees data (FOM104A) for {start_year}-{end_year}...")

        # Parametri specifici pentru FOM104A
        dimensions = {
            "CAEN2": AUTOMOTIVE_CAEN,
            "JUDETE": list(COUNTY_CODES_INS.keys()),
            "UM": "Pers"  # Persoane
        }

        df = self.fetch_data("FOM104A", dimensions, start_year, end_year)

        if df is None or df.empty:
            print("No data fetched from INS")
            return 0

        # Procesare și import
        count = self._import_dataframe(
            df=df,
            indicator_code="TOTAL_EMPLOYEES",
            value_column="value",
            year_column="year",
            county_column="county_code"
        )

        print(f"Imported {count} employee records")
        return count

    def import_salary_data(
        self,
        start_year: int = 2010,
        end_year: int = 2024
    ) -> int:
        """
        Importă datele despre salarii din matricea FOM106E.
        """
        print(f"Importing salary data (FOM106E) for {start_year}-{end_year}...")

        dimensions = {
            "CAEN2": AUTOMOTIVE_CAEN,
            "JUDETE": list(COUNTY_CODES_INS.keys()),
            "UM": "Lei"
        }

        df = self.fetch_data("FOM106E", dimensions, start_year, end_year)

        if df is None or df.empty:
            return 0

        count = self._import_dataframe(
            df=df,
            indicator_code="AVG_SALARY",
            value_column="value",
            year_column="year",
            county_column="county_code"
        )

        print(f"Imported {count} salary records")
        return count

    def import_turnover_data(
        self,
        start_year: int = 2010,
        end_year: int = 2024
    ) -> int:
        """
        Importă datele despre cifra de afaceri.
        """
        print(f"Importing turnover data for {start_year}-{end_year}...")

        dimensions = {
            "CAEN2": AUTOMOTIVE_CAEN,
            "JUDETE": list(COUNTY_CODES_INS.keys())
        }

        df = self.fetch_data("INT101A", dimensions, start_year, end_year)

        if df is None or df.empty:
            return 0

        count = self._import_dataframe(
            df=df,
            indicator_code="TOTAL_TURNOVER",
            value_column="value",
            year_column="year",
            county_column="county_code"
        )

        print(f"Imported {count} turnover records")
        return count

    def _import_dataframe(
        self,
        df: pd.DataFrame,
        indicator_code: str,
        value_column: str,
        year_column: str,
        county_column: Optional[str] = None
    ) -> int:
        """
        Importă un DataFrame în baza de date.
        """
        indicator = self.db.query(IndicatorDefinition).filter(
            IndicatorDefinition.code == indicator_code
        ).first()

        if not indicator:
            print(f"Indicator {indicator_code} not found in database")
            return 0

        count = 0

        for _, row in df.iterrows():
            try:
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

                # Upsert
                existing = self.db.query(IndicatorValue).filter(
                    IndicatorValue.indicator_id == indicator.id,
                    IndicatorValue.year == year,
                    IndicatorValue.county_id == county_id,
                    IndicatorValue.aggregation_level == aggregation_level
                ).first()

                if existing:
                    existing.value = value
                else:
                    new_value = IndicatorValue(
                        indicator_id=indicator.id,
                        year=year,
                        value=value,
                        county_id=county_id,
                        aggregation_level=aggregation_level
                    )
                    self.db.add(new_value)

                count += 1

            except (ValueError, KeyError) as e:
                print(f"Error processing row: {e}")
                continue

        self.db.commit()
        return count

    def import_from_csv_file(
        self,
        file_path: str,
        indicator_code: str,
        year_col: str = "An",
        value_col: str = "Valoare",
        county_col: str = "Judet"
    ) -> int:
        """
        Importă date dintr-un fișier CSV local.
        Util când API-ul INS nu este disponibil.
        """
        print(f"Importing from CSV: {file_path}")

        try:
            df = pd.read_csv(file_path, encoding="utf-8")
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding="latin-1")

        return self._import_dataframe(
            df=df,
            indicator_code=indicator_code,
            value_column=value_col,
            year_column=year_col,
            county_column=county_col
        )


def create_sample_csv_files():
    """
    Creează fișiere CSV de exemplu pentru import manual.
    """
    import os

    data_dir = "/Users/sorinmaxim/Documents/Proiecte/Vestpolicylab.org/automotive-vest-analytics/data/raw"

    # Date angajați
    employees_data = {
        "An": [],
        "Judet": [],
        "Valoare": []
    }

    base_employees = {"TM": 28000, "AR": 18000, "HD": 4000, "CS": 1000}

    for year in range(2010, 2024):
        for county, base in base_employees.items():
            growth = 1 + (year - 2010) * 0.03  # 3% creștere anuală
            # Scădere în 2020 (pandemic)
            if year == 2020:
                growth *= 0.95
            employees_data["An"].append(year)
            employees_data["Judet"].append(county)
            employees_data["Valoare"].append(int(base * growth))

    df_employees = pd.DataFrame(employees_data)
    df_employees.to_csv(f"{data_dir}/employees_automotive.csv", index=False)
    print(f"Created: {data_dir}/employees_automotive.csv")

    # Date cifră de afaceri (milioane EUR)
    turnover_data = {
        "An": [],
        "Judet": [],
        "Valoare": []
    }

    base_turnover = {"TM": 4000, "AR": 2500, "HD": 500, "CS": 120}

    for year in range(2010, 2024):
        for county, base in base_turnover.items():
            growth = 1 + (year - 2010) * 0.05  # 5% creștere anuală
            if year == 2020:
                growth *= 0.92
            turnover_data["An"].append(year)
            turnover_data["Judet"].append(county)
            turnover_data["Valoare"].append(round(base * growth, 2))

    df_turnover = pd.DataFrame(turnover_data)
    df_turnover.to_csv(f"{data_dir}/turnover_automotive.csv", index=False)
    print(f"Created: {data_dir}/turnover_automotive.csv")

    return True


def main():
    """
    Main function pentru import date INS.
    """
    print("=" * 50)
    print("INS Data Import - Automotive Vest Analytics")
    print("=" * 50)

    # Inițializare DB
    init_db()
    db = SessionLocal()

    try:
        importer = INSDataImporter(db)

        # Opțiune 1: Import din API INS (necesită acces la rețea)
        # total = 0
        # total += importer.import_employees_data(2015, 2023)
        # total += importer.import_salary_data(2015, 2023)
        # total += importer.import_turnover_data(2015, 2023)

        # Opțiune 2: Generare fișiere CSV sample și import local
        print("\nGenerating sample CSV files...")
        create_sample_csv_files()

        print("\nImporting from CSV files...")
        data_dir = "/Users/sorinmaxim/Documents/Proiecte/Vestpolicylab.org/automotive-vest-analytics/data/raw"

        total = 0
        total += importer.import_from_csv_file(
            f"{data_dir}/employees_automotive.csv",
            "TOTAL_EMPLOYEES"
        )
        total += importer.import_from_csv_file(
            f"{data_dir}/turnover_automotive.csv",
            "TOTAL_TURNOVER"
        )

        print("=" * 50)
        print(f"Total records imported: {total}")
        print("=" * 50)

    except Exception as e:
        print(f"Error during import: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
