"""
Script pentru importul datelor BSL (Balanța Socială a Locurilor de muncă)
din fișierele Excel ale Regiunii Vest în baza de date.
"""

import os
import re
import pandas as pd
from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Configurare
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/automotive_vest")

# Mapping pentru indicatori BSL
BSL_INDICATORS = {
    "INDICII PRODUCŢIEI INDUSTRIALE": {
        "code": "IND_PROD_INDEX",
        "name": "Indicele producției industriale",
        "category": "performanta",
        "unit": "indice",
        "start_row_offset": 3,  # rânduri după header
        "counties": ["Arad", "Caraş-Severin", "Hunedoara", "Timiş"]
    },
    "INDICII VALORICI AI CIFREI DE AFACERI": {
        "code": "IND_TURNOVER_INDEX",
        "name": "Indicele cifrei de afaceri din industrie",
        "category": "performanta",
        "unit": "indice",
        "start_row_offset": 3,
        "counties": ["Arad", "Caraş-Severin", "Hunedoara", "Timiş"]
    },
    "EFECTIVUL SALARIAŢILOR": {
        "code": "EMPLOYEES_COUNT",
        "name": "Efectivul salariaților",
        "category": "piata_muncii",
        "unit": "numar",
        "start_row_offset": 3,
        "counties": ["Arad", "Caraş-Severin", "Hunedoara", "Timiş"]
    },
    "CÂŞTIGUL SALARIAL MEDIU BRUT": {
        "code": "AVG_GROSS_SALARY",
        "name": "Câștigul salarial mediu brut",
        "category": "piata_muncii",
        "unit": "ron",
        "start_row_offset": 3,
        "counties": ["Arad", "Caraş-Severin", "Hunedoara", "Timiş"]
    },
    "CÂŞTIGUL SALARIAL MEDIU NET": {
        "code": "AVG_NET_SALARY",
        "name": "Câștigul salarial mediu net",
        "category": "piata_muncii",
        "unit": "ron",
        "start_row_offset": 3,
        "counties": ["Arad", "Caraş-Severin", "Hunedoara", "Timiş"]
    },
    "NUMĂRUL ŞOMERILOR ÎNREGISTRAŢI": {
        "code": "UNEMPLOYED_COUNT",
        "name": "Numărul șomerilor înregistrați",
        "category": "piata_muncii",
        "unit": "numar",
        "start_row_offset": 3,
        "counties": ["Arad", "Caraş-Severin", "Hunedoara", "Timiş"]
    },
    "RATA ŞOMAJULUI ÎNREGISTRAT": {
        "code": "UNEMPLOYMENT_RATE",
        "name": "Rata șomajului înregistrat",
        "category": "piata_muncii",
        "unit": "procent",
        "start_row_offset": 3,
        "counties": ["Arad", "Caraş-Severin", "Hunedoara", "Timiş"]
    }
}

# Mapping luni
MONTHS_RO = {
    'ianuarie': 1, 'februarie': 2, 'martie': 3, 'aprilie': 4,
    'mai': 5, 'iunie': 6, 'iulie': 7, 'august': 8,
    'septembrie': 9, 'octombrie': 10, 'noiembrie': 11, 'decembrie': 12,
    'ian': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'iun': 6, 'iul': 7,
    'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
}

# Mapping județe la coduri
COUNTY_CODES = {
    "Arad": "AR",
    "Caraş-Severin": "CS",
    "Caras-Severin": "CS",
    "Hunedoara": "HD",
    "Timiş": "TM",
    "Timis": "TM",
    "Regiunea VEST": "VEST"
}


def extract_month_year_from_filename(filename):
    """Extrage luna și anul din numele fișierului"""
    filename_lower = filename.lower()

    # Pattern pentru anul
    year_match = re.search(r'20\d{2}', filename)
    year = int(year_match.group()) if year_match else None

    # Pattern pentru lună
    month = None
    for month_name, month_num in MONTHS_RO.items():
        if month_name in filename_lower:
            month = month_num
            break

    return month, year


def clean_numeric_value(val):
    """Curăță și convertește o valoare numerică"""
    if pd.isna(val) or val == 'X' or val == 'x' or val == '-':
        return None

    if isinstance(val, (int, float)):
        return float(val)

    # Curăță stringul
    val_str = str(val).strip()
    val_str = val_str.replace(' ', '').replace('\xa0', '')

    # Format european (1.234,56) sau românesc
    if ',' in val_str and '.' in val_str:
        if val_str.rindex(',') > val_str.rindex('.'):
            val_str = val_str.replace('.', '').replace(',', '.')
        else:
            val_str = val_str.replace(',', '')
    elif ',' in val_str:
        val_str = val_str.replace(',', '.')

    try:
        return float(val_str)
    except ValueError:
        return None


def find_indicator_section(df, indicator_key):
    """Găsește secțiunea unui indicator în DataFrame"""
    for idx, row in df.iterrows():
        cell_val = str(row.iloc[0]) if pd.notna(row.iloc[0]) else ''
        if indicator_key in cell_val.upper():
            return idx
    return None


def extract_indicator_data(df, start_row, indicator_config, month, year):
    """Extrage datele pentru un indicator specific"""
    data = []

    # Găsește rândul cu lunile
    month_row = None
    for i in range(start_row, min(start_row + 10, len(df))):
        row_vals = df.iloc[i].astype(str).str.lower().tolist()
        if any(m in str(v) for v in row_vals for m in ['ian', 'feb', 'mar', 'oct', 'nov', 'dec']):
            month_row = i
            break

    if month_row is None:
        return data

    # Găsește coloana pentru luna curentă
    month_cols = []
    for col_idx, val in enumerate(df.iloc[month_row]):
        val_str = str(val).lower().strip() if pd.notna(val) else ''
        for month_name, month_num in MONTHS_RO.items():
            if month_name in val_str and month_num == month:
                month_cols.append(col_idx)

    # Dacă nu găsim coloana exactă, luăm ultima coloană cu date
    if not month_cols:
        # Folosim ultima coloană numerică
        month_cols = [len(df.columns) - 2]  # Penultima coloană de obicei

    # Extrage datele pentru fiecare județ
    for i in range(month_row + 1, min(month_row + 10, len(df))):
        row = df.iloc[i]
        county_name = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ''

        # Normalizare nume județ
        county_code = None
        for name, code in COUNTY_CODES.items():
            if name.lower() in county_name.lower():
                county_code = code
                break

        if county_code and county_code != "VEST":
            for col_idx in month_cols[:1]:  # Luăm doar prima coloană găsită
                value = clean_numeric_value(row.iloc[col_idx])
                if value is not None:
                    data.append({
                        'county_code': county_code,
                        'year': year,
                        'month': month,
                        'value': value,
                        'indicator_code': indicator_config['code']
                    })

    return data


def process_bsl_file(file_path):
    """Procesează un fișier BSL și extrage toate datele"""
    print(f"\nProcesare: {file_path.name}")

    month, year = extract_month_year_from_filename(file_path.name)
    if not month or not year:
        print(f"  Nu s-a putut extrage luna/anul din: {file_path.name}")
        return []

    print(f"  Perioadă: {month}/{year}")

    all_data = []

    try:
        # Citește primul sheet
        df = pd.read_excel(file_path, sheet_name=0, header=None)

        for indicator_key, indicator_config in BSL_INDICATORS.items():
            start_row = find_indicator_section(df, indicator_key)
            if start_row is not None:
                data = extract_indicator_data(df, start_row, indicator_config, month, year)
                all_data.extend(data)
                print(f"  {indicator_config['code']}: {len(data)} înregistrări")

    except Exception as e:
        print(f"  Eroare la procesare: {str(e)}")

    return all_data


def setup_database(engine):
    """Inițializează structura bazei de date"""
    with engine.connect() as conn:
        # Crează regiunea Vest dacă nu există
        conn.execute(text("""
            INSERT INTO regions (name, code)
            VALUES ('Regiunea Vest', 'RO42')
            ON CONFLICT (code) DO NOTHING
        """))

        # Obține ID-ul regiunii
        result = conn.execute(text("SELECT id FROM regions WHERE code = 'RO42'"))
        region_id = result.fetchone()[0]

        # Crează județele
        counties = [
            ('Arad', 'AR', 46.1866, 21.3123),
            ('Caraș-Severin', 'CS', 45.0833, 21.8833),
            ('Hunedoara', 'HD', 45.7500, 22.9000),
            ('Timiș', 'TM', 45.7489, 21.2087)
        ]

        for name, code, lat, lon in counties:
            conn.execute(text("""
                INSERT INTO counties (region_id, name, code, latitude, longitude)
                VALUES (:region_id, :name, :code, :lat, :lon)
                ON CONFLICT (code) DO UPDATE SET name = :name
            """), {"region_id": region_id, "name": name, "code": code, "lat": lat, "lon": lon})

        # Crează definițiile indicatorilor
        for key, config in BSL_INDICATORS.items():
            conn.execute(text(f"""
                INSERT INTO indicator_definitions (code, name, category, unit, data_source)
                VALUES (:code, :name, '{config['category']}'::indicator_category, '{config['unit']}'::indicator_unit, 'BSL INS')
                ON CONFLICT (code) DO UPDATE SET name = :name
            """), {
                "code": config['code'],
                "name": config['name']
            })

        conn.commit()
        print("Structura bazei de date inițializată.")


def import_data_to_db(engine, all_data):
    """Importă datele în baza de date"""
    if not all_data:
        print("Nu sunt date de importat.")
        return 0

    imported = 0

    with engine.connect() as conn:
        for record in all_data:
            try:
                # Obține ID-ul județului
                result = conn.execute(text(
                    "SELECT id FROM counties WHERE code = :code"
                ), {"code": record['county_code']})
                county_row = result.fetchone()
                if not county_row:
                    continue
                county_id = county_row[0]

                # Obține ID-ul indicatorului
                result = conn.execute(text(
                    "SELECT id FROM indicator_definitions WHERE code = :code"
                ), {"code": record['indicator_code']})
                indicator_row = result.fetchone()
                if not indicator_row:
                    continue
                indicator_id = indicator_row[0]

                # Calculează trimestrul
                quarter = (record['month'] - 1) // 3 + 1

                # Inserează sau actualizează valoarea
                conn.execute(text("""
                    INSERT INTO indicator_values
                    (indicator_id, county_id, year, quarter, aggregation_level, value)
                    VALUES (:indicator_id, :county_id, :year, :quarter, 'judet', :value)
                    ON CONFLICT (indicator_id, county_id, year, quarter, aggregation_level)
                    DO UPDATE SET value = :value, updated_at = CURRENT_TIMESTAMP
                """), {
                    "indicator_id": indicator_id,
                    "county_id": county_id,
                    "year": record['year'],
                    "quarter": quarter,
                    "value": record['value']
                })

                imported += 1

            except Exception as e:
                print(f"  Eroare la import: {str(e)}")

        conn.commit()

    return imported


def main():
    """Funcția principală"""
    # Calea către folderul cu documente
    docs_folder = Path(__file__).parent.parent.parent / "Documente suport"

    if not docs_folder.exists():
        # Încercăm și în /app/data/import pentru server
        docs_folder = Path("/app/data/import")
        if not docs_folder.exists():
            print(f"Folderul cu documente nu există: {docs_folder}")
            return

    print(f"Folder documente: {docs_folder}")

    # Găsește toate fișierele BSL
    bsl_files = []
    for pattern in ["BSL*.xlsx", "BSL*.xls"]:
        bsl_files.extend(docs_folder.glob(pattern))

    bsl_files = sorted(bsl_files)
    print(f"\nFișiere BSL găsite: {len(bsl_files)}")

    if not bsl_files:
        print("Nu s-au găsit fișiere BSL pentru import.")
        return

    # Conectare la baza de date
    engine = create_engine(DATABASE_URL)

    # Setup inițial
    setup_database(engine)

    # Procesează fiecare fișier
    all_data = []
    for file_path in bsl_files:
        file_data = process_bsl_file(file_path)
        all_data.extend(file_data)

    print(f"\nTotal înregistrări extrase: {len(all_data)}")

    # Import în baza de date
    imported = import_data_to_db(engine, all_data)
    print(f"Înregistrări importate/actualizate: {imported}")

    # Log import
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO import_logs (source, source_identifier, records_imported, status)
            VALUES ('BSL', 'Regiunea Vest', :count, 'completed')
        """), {"count": imported})
        conn.commit()

    print("\nImport finalizat cu succes!")


if __name__ == "__main__":
    main()
