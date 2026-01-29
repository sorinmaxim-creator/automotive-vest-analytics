"""
Script pentru popularea inițială a bazei de date cu date de referință.
"""

import os
import sys
# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.database import SessionLocal, init_db
from app.models.region import Region, County
from app.models.indicator import IndicatorDefinition, IndicatorCategory, IndicatorUnit
from app.models.company import CompanySector


def seed_regions(db: Session):
    """Populare regiuni și județe."""
    print("Seeding regions and counties...")

    # Verifică dacă există deja
    if db.query(Region).first():
        print("Regions already exist, skipping...")
        return

    # Regiunea Vest
    region_vest = Region(
        name="Regiunea Vest",
        code="RO42",
        latitude=45.7489,
        longitude=21.2087
    )
    db.add(region_vest)
    db.flush()

    # Județele din Regiunea Vest
    counties_data = [
        {
            "name": "Timiș",
            "code": "TM",
            "latitude": 45.7489,
            "longitude": 21.2087,
            "population": 683540,
            "area_km2": 8697,
            "is_automotive_hub": True
        },
        {
            "name": "Arad",
            "code": "AR",
            "latitude": 46.1866,
            "longitude": 21.3123,
            "population": 409072,
            "area_km2": 7754,
            "is_automotive_hub": True
        },
        {
            "name": "Hunedoara",
            "code": "HD",
            "latitude": 45.7500,
            "longitude": 22.9000,
            "population": 372795,
            "area_km2": 7063,
            "is_automotive_hub": False
        },
        {
            "name": "Caraș-Severin",
            "code": "CS",
            "latitude": 45.0833,
            "longitude": 21.8833,
            "population": 254469,
            "area_km2": 8520,
            "is_automotive_hub": False
        }
    ]

    for county_data in counties_data:
        county = County(region_id=region_vest.id, **county_data)
        db.add(county)

    db.commit()
    print(f"Created region {region_vest.name} with {len(counties_data)} counties")


def seed_sectors(db: Session):
    """Populare sectoare CAEN automotive."""
    print("Seeding automotive sectors...")

    if db.query(CompanySector).first():
        print("Sectors already exist, skipping...")
        return

    sectors_data = [
        {
            "caen_code": "2910",
            "caen_name": "Fabricarea autovehiculelor de transport rutier",
            "subsector": "asamblare",
            "description": "Producția de autoturisme, vehicule comerciale și motoare"
        },
        {
            "caen_code": "2920",
            "caen_name": "Producția de caroserii pentru autovehicule",
            "subsector": "componente",
            "description": "Fabricarea de caroserii, remorci și semiremorci"
        },
        {
            "caen_code": "2931",
            "caen_name": "Fabricarea de echipamente electrice și electronice pentru autovehicule",
            "subsector": "componente",
            "description": "Componente electrice, cablaje, sisteme electronice"
        },
        {
            "caen_code": "2932",
            "caen_name": "Fabricarea altor piese și accesorii pentru autovehicule",
            "subsector": "componente",
            "description": "Piese mecanice, sisteme de frânare, transmisii"
        },
        {
            "caen_code": "7112",
            "caen_name": "Activități de inginerie și consultanță tehnică",
            "subsector": "R&D",
            "description": "Servicii de proiectare și dezvoltare automotive"
        }
    ]

    for sector_data in sectors_data:
        sector = CompanySector(**sector_data)
        db.add(sector)

    db.commit()
    print(f"Created {len(sectors_data)} automotive sectors")


def seed_indicators(db: Session):
    """Populare definițiile indicatorilor."""
    print("Seeding indicator definitions...")

    if db.query(IndicatorDefinition).first():
        print("Indicators already exist, skipping...")
        return

    indicators_data = [
        # Structură economică
        {
            "code": "TOTAL_COMPANIES",
            "name": "Număr total firme automotive",
            "name_en": "Total automotive companies",
            "category": IndicatorCategory.ECONOMIC_STRUCTURE,
            "unit": IndicatorUnit.NUMBER,
            "data_source": "ONRC",
            "description": "Numărul total de firme active în sectorul automotive"
        },
        {
            "code": "AVG_COMPANY_SIZE",
            "name": "Dimensiune medie firme (angajați)",
            "name_en": "Average company size (employees)",
            "category": IndicatorCategory.ECONOMIC_STRUCTURE,
            "unit": IndicatorUnit.NUMBER,
            "data_source": "INS",
            "description": "Numărul mediu de angajați per firmă în sector"
        },
        {
            "code": "HHI_INDEX",
            "name": "Indicele Herfindahl-Hirschman",
            "name_en": "Herfindahl-Hirschman Index",
            "category": IndicatorCategory.ECONOMIC_STRUCTURE,
            "unit": IndicatorUnit.INDEX,
            "is_calculated": 1,
            "formula": "SUM(market_share^2)",
            "description": "Indice de concentrare a pieței (0-10000)"
        },

        # Piața muncii
        {
            "code": "TOTAL_EMPLOYEES",
            "name": "Număr total angajați",
            "name_en": "Total employees",
            "category": IndicatorCategory.LABOR_MARKET,
            "unit": IndicatorUnit.NUMBER,
            "data_source": "INS",
            "description": "Numărul total de angajați în sectorul automotive"
        },
        {
            "code": "AVG_SALARY",
            "name": "Salariu mediu brut",
            "name_en": "Average gross salary",
            "category": IndicatorCategory.LABOR_MARKET,
            "unit": IndicatorUnit.RON,
            "data_source": "INS",
            "description": "Salariul mediu brut lunar în sector"
        },
        {
            "code": "PRODUCTIVITY",
            "name": "Productivitatea muncii",
            "name_en": "Labor productivity",
            "category": IndicatorCategory.LABOR_MARKET,
            "unit": IndicatorUnit.EURO_PER_EMPLOYEE,
            "is_calculated": 1,
            "formula": "value_added / employees",
            "description": "Valoare adăugată per angajat"
        },

        # Performanță economică
        {
            "code": "TOTAL_TURNOVER",
            "name": "Cifră de afaceri totală",
            "name_en": "Total turnover",
            "category": IndicatorCategory.PERFORMANCE,
            "unit": IndicatorUnit.EURO,
            "data_source": "INS",
            "description": "Cifra de afaceri totală a sectorului"
        },
        {
            "code": "VALUE_ADDED",
            "name": "Valoare adăugată brută",
            "name_en": "Gross value added",
            "category": IndicatorCategory.PERFORMANCE,
            "unit": IndicatorUnit.EURO,
            "data_source": "INS",
            "description": "Valoarea adăugată brută generată de sector"
        },
        {
            "code": "TOTAL_EXPORTS",
            "name": "Export total",
            "name_en": "Total exports",
            "category": IndicatorCategory.PERFORMANCE,
            "unit": IndicatorUnit.EURO,
            "data_source": "INS",
            "description": "Valoarea totală a exporturilor sectorului"
        },
        {
            "code": "INVESTMENTS",
            "name": "Investiții totale",
            "name_en": "Total investments",
            "category": IndicatorCategory.PERFORMANCE,
            "unit": IndicatorUnit.EURO,
            "data_source": "INS",
            "description": "Investiții brute de capital fix în sector"
        },

        # Inovare
        {
            "code": "RD_EXPENDITURE",
            "name": "Cheltuieli R&D",
            "name_en": "R&D expenditure",
            "category": IndicatorCategory.INNOVATION,
            "unit": IndicatorUnit.EURO,
            "data_source": "Eurostat",
            "description": "Cheltuieli totale pentru cercetare și dezvoltare"
        },
        {
            "code": "PATENTS",
            "name": "Număr brevete",
            "name_en": "Number of patents",
            "category": IndicatorCategory.INNOVATION,
            "unit": IndicatorUnit.NUMBER,
            "data_source": "EPO",
            "description": "Numărul de brevete înregistrate în sector"
        },

        # Comparativ
        {
            "code": "GDP_SHARE",
            "name": "Pondere în PIB regional",
            "name_en": "Share of regional GDP",
            "category": IndicatorCategory.COMPARATIVE,
            "unit": IndicatorUnit.PERCENT,
            "is_calculated": 1,
            "formula": "(sector_gva / regional_gdp) * 100",
            "description": "Contribuția sectorului la PIB-ul regional"
        },
        {
            "code": "LOCATION_QUOTIENT",
            "name": "Coeficient de localizare (LQ)",
            "name_en": "Location Quotient",
            "category": IndicatorCategory.COMPARATIVE,
            "unit": IndicatorUnit.RATIO,
            "is_calculated": 1,
            "formula": "(regional_sector/regional_total) / (national_sector/national_total)",
            "description": "Grad de specializare regională în sector"
        },

        # Sustenabilitate și risc
        {
            "code": "IMPORT_DEPENDENCY",
            "name": "Dependența de importuri componente",
            "name_en": "Component import dependency",
            "category": IndicatorCategory.SUSTAINABILITY,
            "unit": IndicatorUnit.PERCENT,
            "data_source": "INS",
            "description": "Ponderea componentelor importate în producție"
        }
    ]

    for ind_data in indicators_data:
        indicator = IndicatorDefinition(**ind_data)
        db.add(indicator)

    db.commit()
    print(f"Created {len(indicators_data)} indicator definitions")


def seed_sample_data(db: Session):
    """Populare date de exemplu pentru testare."""
    print("Seeding sample indicator values...")

    from app.models.indicator import IndicatorValue, AggregationLevel

    # Verifică dacă există deja date
    if db.query(IndicatorValue).first():
        print("Sample data already exists, skipping...")
        return

    # Get indicator IDs
    employees_ind = db.query(IndicatorDefinition).filter_by(code="TOTAL_EMPLOYEES").first()
    turnover_ind = db.query(IndicatorDefinition).filter_by(code="TOTAL_TURNOVER").first()
    companies_ind = db.query(IndicatorDefinition).filter_by(code="TOTAL_COMPANIES").first()

    # Get county IDs
    timis = db.query(County).filter_by(code="TM").first()
    arad = db.query(County).filter_by(code="AR").first()
    hunedoara = db.query(County).filter_by(code="HD").first()
    caras = db.query(County).filter_by(code="CS").first()

    # Sample data - employees by county and year
    sample_employees = [
        # Timiș
        (employees_ind.id, timis.id, 2019, 28500),
        (employees_ind.id, timis.id, 2020, 27200),
        (employees_ind.id, timis.id, 2021, 29100),
        (employees_ind.id, timis.id, 2022, 31500),
        (employees_ind.id, timis.id, 2023, 33200),
        # Arad
        (employees_ind.id, arad.id, 2019, 18200),
        (employees_ind.id, arad.id, 2020, 17500),
        (employees_ind.id, arad.id, 2021, 18800),
        (employees_ind.id, arad.id, 2022, 20100),
        (employees_ind.id, arad.id, 2023, 21500),
        # Hunedoara
        (employees_ind.id, hunedoara.id, 2019, 4200),
        (employees_ind.id, hunedoara.id, 2020, 3900),
        (employees_ind.id, hunedoara.id, 2021, 4100),
        (employees_ind.id, hunedoara.id, 2022, 4400),
        (employees_ind.id, hunedoara.id, 2023, 4600),
        # Caraș-Severin
        (employees_ind.id, caras.id, 2019, 1100),
        (employees_ind.id, caras.id, 2020, 1050),
        (employees_ind.id, caras.id, 2021, 1150),
        (employees_ind.id, caras.id, 2022, 1200),
        (employees_ind.id, caras.id, 2023, 1250),
    ]

    for ind_id, county_id, year, value in sample_employees:
        db.add(IndicatorValue(
            indicator_id=ind_id,
            county_id=county_id,
            year=year,
            value=value,
            aggregation_level=AggregationLevel.COUNTY
        ))

    # Regional totals
    for year in range(2019, 2024):
        county_values = [v[3] for v in sample_employees if v[2] == year]
        total = sum(county_values)
        db.add(IndicatorValue(
            indicator_id=employees_ind.id,
            county_id=None,
            year=year,
            value=total,
            aggregation_level=AggregationLevel.REGION
        ))

    # Sample turnover data (millions EUR)
    sample_turnover = [
        (turnover_ind.id, None, 2019, 8500000000, AggregationLevel.REGION),
        (turnover_ind.id, None, 2020, 7800000000, AggregationLevel.REGION),
        (turnover_ind.id, None, 2021, 9200000000, AggregationLevel.REGION),
        (turnover_ind.id, None, 2022, 10500000000, AggregationLevel.REGION),
        (turnover_ind.id, None, 2023, 11200000000, AggregationLevel.REGION),
    ]

    for ind_id, county_id, year, value, level in sample_turnover:
        db.add(IndicatorValue(
            indicator_id=ind_id,
            county_id=county_id,
            year=year,
            value=value,
            aggregation_level=level
        ))

    # Sample companies count
    sample_companies = [
        (companies_ind.id, None, 2019, 385, AggregationLevel.REGION),
        (companies_ind.id, None, 2020, 372, AggregationLevel.REGION),
        (companies_ind.id, None, 2021, 398, AggregationLevel.REGION),
        (companies_ind.id, None, 2022, 425, AggregationLevel.REGION),
        (companies_ind.id, None, 2023, 448, AggregationLevel.REGION),
    ]

    for ind_id, county_id, year, value, level in sample_companies:
        db.add(IndicatorValue(
            indicator_id=ind_id,
            county_id=county_id,
            year=year,
            value=value,
            aggregation_level=level
        ))

    db.commit()
    print("Sample data created successfully")


def main():
    """Main function to run all seeds."""
    print("=" * 50)
    print("Automotive Vest Analytics - Database Seeding")
    print("=" * 50)

    # Initialize database tables
    init_db()

    # Create session
    db = SessionLocal()

    try:
        seed_regions(db)
        seed_sectors(db)
        seed_indicators(db)
        seed_sample_data(db)

        print("=" * 50)
        print("Database seeding completed successfully!")
        print("=" * 50)

    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
