"""
Utilități pentru conectarea la baza de date din frontend
Cu fallback pe date demo când baza de date nu este disponibilă
"""

import os
import pandas as pd

# Configurare conexiune baza de date
POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "automotive_vest_db")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT", "5432")
POSTGRES_USER = os.environ.get("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "postgres")
POSTGRES_DB = os.environ.get("POSTGRES_DB", "automotive_vest")

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

# Flag global pentru a detecta dacă baza de date e disponibilă
_DB_AVAILABLE = None


def _check_db():
    """Verifică dacă baza de date e disponibilă (cached)"""
    global _DB_AVAILABLE
    if _DB_AVAILABLE is not None:
        return _DB_AVAILABLE
    try:
        import psycopg2
        conn = psycopg2.connect(
            host=POSTGRES_HOST, port=POSTGRES_PORT,
            user=POSTGRES_USER, password=POSTGRES_PASSWORD,
            database=POSTGRES_DB, connect_timeout=3
        )
        # Verifică efectiv că baza de date funcționează cu un query simplu
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        conn.close()
        _DB_AVAILABLE = True
    except Exception:
        _DB_AVAILABLE = False
    return _DB_AVAILABLE


def _reset_db_check():
    """Resetează cache-ul de verificare DB (util după erori)"""
    global _DB_AVAILABLE
    _DB_AVAILABLE = None


def get_engine():
    """Returnează engine-ul SQLAlchemy"""
    from sqlalchemy import create_engine
    return create_engine(DATABASE_URL)


def get_db_connection():
    """Returnează o conexiune psycopg2 directă la baza de date"""
    import psycopg2
    return psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        database=POSTGRES_DB
    )


# ==================== DATE DEMO ====================

def _demo_counties():
    return pd.DataFrame({
        'id': [1, 2, 3, 4],
        'name': ['Arad', 'Caraș-Severin', 'Hunedoara', 'Timiș'],
        'code': ['AR', 'CS', 'HD', 'TM'],
        'latitude': [46.1866, 45.0833, 45.7500, 45.7489],
        'longitude': [21.3123, 21.8833, 22.9000, 21.2087]
    })


def _demo_available_years():
    return [2024, 2023, 2022, 2021, 2020]


def _demo_all_indicators():
    return pd.DataFrame({
        'code': ['AVG_GROSS_SALARY', 'AVG_NET_SALARY', 'EMPLOYEES_COUNT',
                 'UNEMPLOYED_COUNT', 'UNEMPLOYMENT_RATE', 'IND_PROD_INDEX', 'IND_TURNOVER_INDEX'],
        'name': ['Câștigul salarial mediu brut', 'Câștigul salarial mediu net',
                 'Efectiv salariați', 'Număr șomeri', 'Rata șomajului',
                 'Indicele producției industriale', 'Indicele cifrei de afaceri'],
        'category': ['salarii', 'salarii', 'piata_muncii', 'piata_muncii',
                     'piata_muncii', 'industrie', 'industrie'],
        'unit': ['ron', 'ron', 'numar', 'numar', 'procent', 'indice', 'indice'],
        'values_count': [32, 32, 32, 32, 32, 32, 32],
        'min_year': [2020, 2020, 2020, 2020, 2020, 2020, 2020],
        'max_year': [2024, 2024, 2024, 2024, 2024, 2024, 2024]
    })


def _demo_salary_data(year=None):
    counties = ['Arad', 'Caraș-Severin', 'Hunedoara', 'Timiș']
    codes = ['AR', 'CS', 'HD', 'TM']
    gross = [6200, 5400, 5800, 7100]
    net = [3750, 3280, 3520, 4300]
    rows = []
    years = [year] if year else [2024, 2023, 2022, 2021, 2020]
    for y in years:
        for q in [1, 2, 3, 4]:
            for i, county in enumerate(counties):
                adj = (y - 2020) * 200 + q * 50
                rows.append({'county_name': county, 'county_code': codes[i], 'year': y,
                             'quarter': q, 'indicator_code': 'AVG_GROSS_SALARY', 'value': gross[i] + adj})
                rows.append({'county_name': county, 'county_code': codes[i], 'year': y,
                             'quarter': q, 'indicator_code': 'AVG_NET_SALARY', 'value': net[i] + int(adj * 0.6)})
    return pd.DataFrame(rows)


def _demo_labor_data(year=None):
    counties = ['Arad', 'Caraș-Severin', 'Hunedoara', 'Timiș']
    codes = ['AR', 'CS', 'HD', 'TM']
    employees = [85000, 42000, 58000, 165000]
    unemployed = [4200, 3800, 5100, 6500]
    unemp_rate = [4.9, 8.3, 8.1, 3.9]
    rows = []
    years = [year] if year else [2024, 2023, 2022, 2021, 2020]
    for y in years:
        for q in [1, 2, 3, 4]:
            for i, county in enumerate(counties):
                adj = (y - 2020) * 500
                rows.append({'county_name': county, 'county_code': codes[i], 'year': y, 'quarter': q,
                             'indicator_code': 'EMPLOYEES_COUNT', 'indicator_name': 'Efectiv salariați',
                             'value': employees[i] + adj})
                rows.append({'county_name': county, 'county_code': codes[i], 'year': y, 'quarter': q,
                             'indicator_code': 'UNEMPLOYED_COUNT', 'indicator_name': 'Număr șomeri',
                             'value': max(500, unemployed[i] - (y - 2020) * 100)})
                rows.append({'county_name': county, 'county_code': codes[i], 'year': y, 'quarter': q,
                             'indicator_code': 'UNEMPLOYMENT_RATE', 'indicator_name': 'Rata șomajului',
                             'value': round(max(1.5, unemp_rate[i] - (y - 2020) * 0.2), 1)})
    return pd.DataFrame(rows)


def _demo_industry_data(year=None):
    counties = ['Arad', 'Caraș-Severin', 'Hunedoara', 'Timiș']
    codes = ['AR', 'CS', 'HD', 'TM']
    prod_idx = [105.2, 92.3, 98.7, 112.4]
    turn_idx = [108.1, 89.5, 101.3, 115.6]
    rows = []
    years = [year] if year else [2024, 2023, 2022, 2021, 2020]
    for y in years:
        for q in [1, 2, 3, 4]:
            for i, county in enumerate(counties):
                adj = (y - 2020) * 1.5
                rows.append({'county_name': county, 'county_code': codes[i], 'year': y, 'quarter': q,
                             'indicator_code': 'IND_PROD_INDEX', 'indicator_name': 'Indicele producției industriale',
                             'value': round(prod_idx[i] + adj, 1)})
                rows.append({'county_name': county, 'county_code': codes[i], 'year': y, 'quarter': q,
                             'indicator_code': 'IND_TURNOVER_INDEX', 'indicator_name': 'Indicele cifrei de afaceri',
                             'value': round(turn_idx[i] + adj, 1)})
    return pd.DataFrame(rows)


def _demo_quarterly_evolution(indicator_code, county_code=None):
    counties = ['Arad', 'Caraș-Severin', 'Hunedoara', 'Timiș']
    codes = ['AR', 'CS', 'HD', 'TM']
    base_values = {
        'AVG_GROSS_SALARY': [6200, 5400, 5800, 7100],
        'AVG_NET_SALARY': [3750, 3280, 3520, 4300],
        'EMPLOYEES_COUNT': [85000, 42000, 58000, 165000],
        'UNEMPLOYED_COUNT': [4200, 3800, 5100, 6500],
        'UNEMPLOYMENT_RATE': [4.9, 8.3, 8.1, 3.9],
        'IND_PROD_INDEX': [105.2, 92.3, 98.7, 112.4],
        'IND_TURNOVER_INDEX': [108.1, 89.5, 101.3, 115.6],
    }
    base = base_values.get(indicator_code, [100, 90, 95, 110])
    rows = []
    for y in range(2020, 2025):
        for q in [1, 2, 3, 4]:
            for i, county in enumerate(counties):
                if county_code and codes[i] != county_code:
                    continue
                adj = (y - 2020) * 100 + q * 20
                rows.append({'county_name': county, 'county_code': codes[i], 'year': y, 'quarter': q,
                             'value': round(base[i] + adj, 1), 'period': f"{y} T{q}"})
    return pd.DataFrame(rows)


def _demo_county_details(county_code):
    code_to_name = {'AR': 'Arad', 'CS': 'Caraș-Severin', 'HD': 'Hunedoara', 'TM': 'Timiș'}
    indicators = {
        'AVG_GROSS_SALARY': ('Câștigul salarial mediu brut', 'ron', 6500),
        'AVG_NET_SALARY': ('Câștigul salarial mediu net', 'ron', 3900),
        'UNEMPLOYMENT_RATE': ('Rata șomajului', 'procent', 4.5),
        'EMPLOYEES_COUNT': ('Efectiv salariați', 'numar', 85000),
        'UNEMPLOYED_COUNT': ('Număr șomeri', 'numar', 4200),
        'IND_PROD_INDEX': ('Indicele producției industriale', 'indice', 105.2),
        'IND_TURNOVER_INDEX': ('Indicele cifrei de afaceri', 'indice', 108.1),
    }
    rows = []
    for y in range(2020, 2025):
        for q in [1, 2, 3, 4]:
            for code, (name, unit, base_val) in indicators.items():
                adj = (y - 2020) * 50 + q * 10
                rows.append({'indicator_code': code, 'indicator_name': name, 'unit': unit,
                             'year': y, 'quarter': q, 'value': round(base_val + adj, 1)})
    return pd.DataFrame(rows)


def _demo_export_all():
    counties = ['Arad', 'Caraș-Severin', 'Hunedoara', 'Timiș']
    codes = ['AR', 'CS', 'HD', 'TM']
    indicators = [
        ('AVG_GROSS_SALARY', 'Câștigul salarial mediu brut', 'ron', [6200, 5400, 5800, 7100]),
        ('AVG_NET_SALARY', 'Câștigul salarial mediu net', 'ron', [3750, 3280, 3520, 4300]),
        ('EMPLOYEES_COUNT', 'Efectiv salariați', 'numar', [85000, 42000, 58000, 165000]),
        ('UNEMPLOYMENT_RATE', 'Rata șomajului', 'procent', [4.9, 8.3, 8.1, 3.9]),
    ]
    rows = []
    for y in range(2020, 2025):
        for q in [1, 2, 3, 4]:
            for ind_code, ind_name, unit, base_vals in indicators:
                for i, county in enumerate(counties):
                    adj = (y - 2020) * 100 + q * 20
                    rows.append({
                        'judet': county, 'cod_judet': codes[i],
                        'indicator': ind_name, 'cod_indicator': ind_code,
                        'unitate': unit, 'an': y, 'trimestru': q,
                        'valoare': round(base_vals[i] + adj, 1)
                    })
    return pd.DataFrame(rows)


# ==================== FUNCȚII PUBLICE CU FALLBACK ====================

def get_indicator_data(indicator_code, year=None, quarter=None, county_code=None):
    """Obține date pentru un indicator specific"""
    if not _check_db():
        return pd.DataFrame()

    try:
        from sqlalchemy import text
        engine = get_engine()

        query = """
            SELECT
                c.name as county_name,
                c.code as county_code,
                iv.year,
                iv.quarter,
                iv.value,
                id.name as indicator_name,
                id.unit
            FROM indicator_values iv
            JOIN indicator_definitions id ON iv.indicator_id = id.id
            JOIN counties c ON iv.county_id = c.id
            WHERE id.code = :indicator_code
        """

        params = {"indicator_code": indicator_code}

        if year:
            query += " AND iv.year = :year"
            params["year"] = year

        if quarter:
            query += " AND iv.quarter = :quarter"
            params["quarter"] = quarter

        if county_code:
            query += " AND c.code = :county_code"
            params["county_code"] = county_code

        query += " ORDER BY iv.year DESC, iv.quarter DESC, c.name"

        with engine.connect() as conn:
            df = pd.read_sql(text(query), conn, params=params)

        return df
    except Exception:
        _reset_db_check()
        return pd.DataFrame()


def get_all_indicators():
    """Obține lista tuturor indicatorilor"""
    if not _check_db():
        return _demo_all_indicators()

    try:
        from sqlalchemy import text
        engine = get_engine()

        query = """
            SELECT
                id.code,
                id.name,
                id.category::text as category,
                id.unit::text as unit,
                COUNT(iv.id) as values_count,
                MIN(iv.year) as min_year,
                MAX(iv.year) as max_year
            FROM indicator_definitions id
            LEFT JOIN indicator_values iv ON id.id = iv.indicator_id
            GROUP BY id.code, id.name, id.category, id.unit
            ORDER BY id.name
        """

        with engine.connect() as conn:
            df = pd.read_sql(text(query), conn)

        return df
    except Exception:
        _reset_db_check()
        return _demo_all_indicators()


def get_counties():
    """Obține lista județelor"""
    if not _check_db():
        return _demo_counties()

    try:
        from sqlalchemy import text
        engine = get_engine()

        query = """
            SELECT id, name, code, latitude, longitude
            FROM counties
            ORDER BY name
        """

        with engine.connect() as conn:
            df = pd.read_sql(text(query), conn)

        return df
    except Exception:
        _reset_db_check()
        return _demo_counties()


def get_available_years():
    """Obține anii disponibili în date"""
    if not _check_db():
        return _demo_available_years()

    try:
        from sqlalchemy import text
        engine = get_engine()

        query = """
            SELECT DISTINCT year
            FROM indicator_values
            ORDER BY year DESC
        """

        with engine.connect() as conn:
            result = conn.execute(text(query))
            years = [row[0] for row in result]

        return years
    except Exception:
        _reset_db_check()
        return _demo_available_years()


def get_salary_comparison(year=None):
    """Obține comparație salarii brut/net pe județe"""
    if not _check_db():
        return _demo_salary_data(year)

    try:
        from sqlalchemy import text
        engine = get_engine()

        query = """
            SELECT
                c.name as county_name,
                c.code as county_code,
                iv.year,
                iv.quarter,
                id.code as indicator_code,
                iv.value
            FROM indicator_values iv
            JOIN indicator_definitions id ON iv.indicator_id = id.id
            JOIN counties c ON iv.county_id = c.id
            WHERE id.code IN ('AVG_GROSS_SALARY', 'AVG_NET_SALARY')
        """

        params = {}
        if year:
            query += " AND iv.year = :year"
            params["year"] = year

        query += " ORDER BY iv.year DESC, iv.quarter DESC, c.name"

        with engine.connect() as conn:
            df = pd.read_sql(text(query), conn, params=params)

        return df
    except Exception:
        _reset_db_check()
        return _demo_salary_data(year)


def get_labor_market_data(year=None):
    """Obține date despre piața muncii"""
    if not _check_db():
        return _demo_labor_data(year)

    try:
        from sqlalchemy import text
        engine = get_engine()

        query = """
            SELECT
                c.name as county_name,
                c.code as county_code,
                iv.year,
                iv.quarter,
                id.code as indicator_code,
                id.name as indicator_name,
                iv.value
            FROM indicator_values iv
            JOIN indicator_definitions id ON iv.indicator_id = id.id
            JOIN counties c ON iv.county_id = c.id
            WHERE id.code IN ('EMPLOYEES_COUNT', 'UNEMPLOYED_COUNT', 'UNEMPLOYMENT_RATE')
        """

        params = {}
        if year:
            query += " AND iv.year = :year"
            params["year"] = year

        query += " ORDER BY iv.year DESC, iv.quarter DESC, c.name"

        with engine.connect() as conn:
            df = pd.read_sql(text(query), conn, params=params)

        return df
    except Exception:
        _reset_db_check()
        return _demo_labor_data(year)


def get_industry_indices(year=None):
    """Obține indicii industriali"""
    if not _check_db():
        return _demo_industry_data(year)

    try:
        from sqlalchemy import text
        engine = get_engine()

        query = """
            SELECT
                c.name as county_name,
                c.code as county_code,
                iv.year,
                iv.quarter,
                id.code as indicator_code,
                id.name as indicator_name,
                iv.value
            FROM indicator_values iv
            JOIN indicator_definitions id ON iv.indicator_id = id.id
            JOIN counties c ON iv.county_id = c.id
            WHERE id.code IN ('IND_PROD_INDEX', 'IND_TURNOVER_INDEX')
        """

        params = {}
        if year:
            query += " AND iv.year = :year"
            params["year"] = year

        query += " ORDER BY iv.year DESC, iv.quarter DESC, c.name"

        with engine.connect() as conn:
            df = pd.read_sql(text(query), conn, params=params)

        return df
    except Exception:
        _reset_db_check()
        return _demo_industry_data(year)


def get_quarterly_evolution(indicator_code, county_code=None):
    """Obține evoluția trimestrială pentru un indicator"""
    if not _check_db():
        return _demo_quarterly_evolution(indicator_code, county_code)

    try:
        from sqlalchemy import text
        engine = get_engine()

        query = """
            SELECT
                c.name as county_name,
                c.code as county_code,
                iv.year,
                iv.quarter,
                iv.value,
                CONCAT(iv.year, ' T', iv.quarter) as period
            FROM indicator_values iv
            JOIN indicator_definitions id ON iv.indicator_id = id.id
            JOIN counties c ON iv.county_id = c.id
            WHERE id.code = :indicator_code
        """

        params = {"indicator_code": indicator_code}

        if county_code:
            query += " AND c.code = :county_code"
            params["county_code"] = county_code

        query += " ORDER BY iv.year, iv.quarter, c.name"

        with engine.connect() as conn:
            df = pd.read_sql(text(query), conn, params=params)

        return df
    except Exception:
        _reset_db_check()
        return _demo_quarterly_evolution(indicator_code, county_code)


def get_county_details(county_code):
    """Obține toate datele pentru un județ"""
    if not _check_db():
        return _demo_county_details(county_code)

    try:
        from sqlalchemy import text
        engine = get_engine()

        query = """
            SELECT
                id.code as indicator_code,
                id.name as indicator_name,
                id.unit::text as unit,
                iv.year,
                iv.quarter,
                iv.value
            FROM indicator_values iv
            JOIN indicator_definitions id ON iv.indicator_id = id.id
            JOIN counties c ON iv.county_id = c.id
            WHERE c.code = :county_code
            ORDER BY id.name, iv.year DESC, iv.quarter DESC
        """

        with engine.connect() as conn:
            df = pd.read_sql(text(query), conn, params={"county_code": county_code})

        return df
    except Exception:
        _reset_db_check()
        return _demo_county_details(county_code)


def export_all_data():
    """Exportă toate datele pentru download"""
    if not _check_db():
        return _demo_export_all()

    try:
        from sqlalchemy import text
        engine = get_engine()

        query = """
            SELECT
                c.name as judet,
                c.code as cod_judet,
                id.name as indicator,
                id.code as cod_indicator,
                id.unit::text as unitate,
                iv.year as an,
                iv.quarter as trimestru,
                iv.value as valoare
            FROM indicator_values iv
            JOIN indicator_definitions id ON iv.indicator_id = id.id
            JOIN counties c ON iv.county_id = c.id
            ORDER BY c.name, id.name, iv.year DESC, iv.quarter DESC
        """

        with engine.connect() as conn:
            df = pd.read_sql(text(query), conn)

        return df
    except Exception:
        _reset_db_check()
        return _demo_export_all()
