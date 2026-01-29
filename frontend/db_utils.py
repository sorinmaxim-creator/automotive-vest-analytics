"""
Utilități pentru conectarea la baza de date din frontend
"""

import os
import pandas as pd
import psycopg2
from sqlalchemy import create_engine, text

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

def get_engine():
    """Returnează engine-ul SQLAlchemy"""
    return create_engine(DATABASE_URL)

def get_db_connection():
    """Returnează o conexiune psycopg2 directă la baza de date"""
    return psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        database=POSTGRES_DB
    )

def get_indicator_data(indicator_code, year=None, quarter=None, county_code=None):
    """Obține date pentru un indicator specific"""
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

def get_all_indicators():
    """Obține lista tuturor indicatorilor"""
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

def get_counties():
    """Obține lista județelor"""
    engine = get_engine()

    query = """
        SELECT id, name, code, latitude, longitude
        FROM counties
        ORDER BY name
    """

    with engine.connect() as conn:
        df = pd.read_sql(text(query), conn)

    return df

def get_available_years():
    """Obține anii disponibili în date"""
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

def get_salary_comparison(year=None):
    """Obține comparație salarii brut/net pe județe"""
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

def get_labor_market_data(year=None):
    """Obține date despre piața muncii"""
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

def get_industry_indices(year=None):
    """Obține indicii industriali"""
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

def get_quarterly_evolution(indicator_code, county_code=None):
    """Obține evoluția trimestrială pentru un indicator"""
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

def get_county_details(county_code):
    """Obține toate datele pentru un județ"""
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

def export_all_data():
    """Exportă toate datele pentru download"""
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
