-- ============================================
-- AUTOMOTIVE VEST ANALYTICS - DATABASE SCHEMA
-- PostgreSQL 15+
-- ============================================

-- Extensii necesare
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- TABELE DE REFERINȚĂ (DIMENSIUNI)
-- ============================================

-- Regiuni de dezvoltare
CREATE TABLE IF NOT EXISTS regions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    code VARCHAR(10) NOT NULL UNIQUE,  -- ex: "RO42" pentru Vest
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

COMMENT ON TABLE regions IS 'Regiuni de dezvoltare din România';
COMMENT ON COLUMN regions.code IS 'Cod NUTS2 al regiunii';

-- Județe
CREATE TABLE IF NOT EXISTS counties (
    id SERIAL PRIMARY KEY,
    region_id INTEGER NOT NULL REFERENCES regions(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(10) NOT NULL UNIQUE,  -- ex: "TM", "AR"
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    population INTEGER,
    area_km2 DECIMAL(10,2),
    is_automotive_hub BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX idx_counties_region ON counties(region_id);
CREATE INDEX idx_counties_code ON counties(code);

COMMENT ON TABLE counties IS 'Județele din cadrul regiunilor';
COMMENT ON COLUMN counties.is_automotive_hub IS 'Indicator dacă județul este hub automotive major';

-- Sectoare CAEN
CREATE TABLE IF NOT EXISTS company_sectors (
    id SERIAL PRIMARY KEY,
    caen_code VARCHAR(10) NOT NULL UNIQUE,
    caen_name VARCHAR(200) NOT NULL,
    subsector VARCHAR(100),  -- ex: "componente", "asamblare", "R&D"
    is_automotive BOOLEAN DEFAULT TRUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sectors_caen ON company_sectors(caen_code);
CREATE INDEX idx_sectors_subsector ON company_sectors(subsector);

COMMENT ON TABLE company_sectors IS 'Clasificare CAEN pentru sectoare industriale';

-- ============================================
-- TABELE PENTRU INDICATORI
-- ============================================

-- Tipuri enumerate
CREATE TYPE indicator_category AS ENUM (
    'structura_economica',
    'piata_muncii',
    'performanta',
    'inovare',
    'sustenabilitate',
    'comparativ'
);

CREATE TYPE indicator_unit AS ENUM (
    'numar',
    'procent',
    'euro',
    'ron',
    'euro_per_angajat',
    'indice',
    'raport'
);

CREATE TYPE aggregation_level AS ENUM (
    'judet',
    'regiune',
    'tara',
    'ue'
);

-- Definiții indicatori
CREATE TABLE IF NOT EXISTS indicator_definitions (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(200) NOT NULL,
    name_en VARCHAR(200),
    description TEXT,
    methodology TEXT,
    category indicator_category NOT NULL,
    unit indicator_unit NOT NULL,
    data_source VARCHAR(100),
    source_code VARCHAR(100),  -- Cod la sursa de date
    is_calculated SMALLINT DEFAULT 0,
    formula TEXT,
    update_frequency VARCHAR(50),  -- "anual", "trimestrial"
    warning_threshold_low DECIMAL(15,4),
    warning_threshold_high DECIMAL(15,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX idx_indicators_code ON indicator_definitions(code);
CREATE INDEX idx_indicators_category ON indicator_definitions(category);

COMMENT ON TABLE indicator_definitions IS 'Catalog de indicatori statistici';
COMMENT ON COLUMN indicator_definitions.is_calculated IS '1 dacă indicatorul e calculat din alți indicatori';

-- Valori indicatori
CREATE TABLE IF NOT EXISTS indicator_values (
    id SERIAL PRIMARY KEY,
    indicator_id INTEGER NOT NULL REFERENCES indicator_definitions(id) ON DELETE CASCADE,
    county_id INTEGER REFERENCES counties(id) ON DELETE SET NULL,
    year SMALLINT NOT NULL,
    quarter SMALLINT,  -- 1-4, NULL pentru date anuale
    aggregation_level aggregation_level NOT NULL DEFAULT 'regiune',
    value DECIMAL(20,4) NOT NULL,
    is_provisional SMALLINT DEFAULT 0,
    is_estimated SMALLINT DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,

    -- Constraint pentru unicitate
    CONSTRAINT uq_indicator_value UNIQUE (indicator_id, county_id, year, quarter, aggregation_level)
);

CREATE INDEX idx_values_indicator ON indicator_values(indicator_id);
CREATE INDEX idx_values_county ON indicator_values(county_id);
CREATE INDEX idx_values_year ON indicator_values(year);
CREATE INDEX idx_values_aggregation ON indicator_values(aggregation_level);
CREATE INDEX idx_values_lookup ON indicator_values(indicator_id, year, aggregation_level);

COMMENT ON TABLE indicator_values IS 'Valori ale indicatorilor pe dimensiuni temporale și geografice';

-- ============================================
-- TABELE PENTRU DATE COMPANII (AGREGATE)
-- ============================================

-- Date agregate companii (nu date individuale)
CREATE TABLE IF NOT EXISTS aggregated_company_data (
    id SERIAL PRIMARY KEY,
    county_id INTEGER NOT NULL REFERENCES counties(id) ON DELETE CASCADE,
    sector_id INTEGER REFERENCES company_sectors(id) ON DELETE SET NULL,
    year SMALLINT NOT NULL,

    -- Metrici agregate
    total_companies INTEGER,
    total_employees INTEGER,
    total_turnover DECIMAL(18,2),  -- în EUR
    average_employees DECIMAL(10,2),
    average_turnover DECIMAL(18,2),

    -- Distribuție pe dimensiune
    micro_companies INTEGER,   -- <10 angajați
    small_companies INTEGER,   -- 10-49
    medium_companies INTEGER,  -- 50-249
    large_companies INTEGER,   -- 250+

    -- Indicatori derivați
    hhi_index DECIMAL(10,4),  -- Herfindahl-Hirschman Index
    concentration_ratio_top5 DECIMAL(5,2),  -- CR5 în %

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,

    CONSTRAINT uq_aggregated_data UNIQUE (county_id, sector_id, year)
);

CREATE INDEX idx_agg_county_year ON aggregated_company_data(county_id, year);
CREATE INDEX idx_agg_sector ON aggregated_company_data(sector_id);

COMMENT ON TABLE aggregated_company_data IS 'Date agregate despre firme, nu individuale';

-- ============================================
-- TABELE PENTRU RAPOARTE ȘI CACHE
-- ============================================

-- Log rapoarte generate
CREATE TABLE IF NOT EXISTS report_logs (
    id SERIAL PRIMARY KEY,
    report_id UUID DEFAULT uuid_generate_v4(),
    report_type VARCHAR(50) NOT NULL,
    title VARCHAR(200),
    parameters JSONB,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_path VARCHAR(500),
    status VARCHAR(20) DEFAULT 'generated'
);

CREATE INDEX idx_reports_type ON report_logs(report_type);
CREATE INDEX idx_reports_date ON report_logs(generated_at);

-- Cache pentru date procesate
CREATE TABLE IF NOT EXISTS data_cache (
    id SERIAL PRIMARY KEY,
    cache_key VARCHAR(200) NOT NULL UNIQUE,
    cache_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,

    CONSTRAINT chk_expiry CHECK (expires_at > created_at)
);

CREATE INDEX idx_cache_key ON data_cache(cache_key);
CREATE INDEX idx_cache_expiry ON data_cache(expires_at);

-- ============================================
-- TABELE PENTRU IMPORT DATE
-- ============================================

-- Log importuri date
CREATE TABLE IF NOT EXISTS import_logs (
    id SERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL,  -- "INS", "Eurostat", "CSV"
    source_identifier VARCHAR(100),  -- cod matrice/dataset
    import_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    records_imported INTEGER,
    records_updated INTEGER,
    records_failed INTEGER,
    status VARCHAR(20) DEFAULT 'completed',
    error_message TEXT,
    metadata JSONB
);

CREATE INDEX idx_imports_source ON import_logs(source);
CREATE INDEX idx_imports_date ON import_logs(import_date);

-- ============================================
-- VIEWS PENTRU RAPORTARE
-- ============================================

-- View pentru date complete indicator
CREATE OR REPLACE VIEW v_indicator_data AS
SELECT
    iv.id,
    id.code AS indicator_code,
    id.name AS indicator_name,
    id.category,
    id.unit,
    c.name AS county_name,
    c.code AS county_code,
    r.name AS region_name,
    iv.year,
    iv.quarter,
    iv.aggregation_level,
    iv.value,
    iv.is_provisional,
    iv.is_estimated
FROM indicator_values iv
JOIN indicator_definitions id ON iv.indicator_id = id.id
LEFT JOIN counties c ON iv.county_id = c.id
LEFT JOIN regions r ON c.region_id = r.id;

-- View pentru sumar KPI pe an
CREATE OR REPLACE VIEW v_kpi_summary AS
SELECT
    iv.year,
    MAX(CASE WHEN id.code = 'TOTAL_COMPANIES' THEN iv.value END) AS total_companies,
    MAX(CASE WHEN id.code = 'TOTAL_EMPLOYEES' THEN iv.value END) AS total_employees,
    MAX(CASE WHEN id.code = 'TOTAL_TURNOVER' THEN iv.value END) AS total_turnover,
    MAX(CASE WHEN id.code = 'TOTAL_EXPORTS' THEN iv.value END) AS total_exports,
    MAX(CASE WHEN id.code = 'PRODUCTIVITY' THEN iv.value END) AS productivity
FROM indicator_values iv
JOIN indicator_definitions id ON iv.indicator_id = id.id
WHERE iv.aggregation_level = 'regiune'
GROUP BY iv.year
ORDER BY iv.year;

-- View pentru comparație județe
CREATE OR REPLACE VIEW v_county_comparison AS
SELECT
    c.name AS county_name,
    c.code AS county_code,
    id.code AS indicator_code,
    id.name AS indicator_name,
    iv.year,
    iv.value,
    iv.value / NULLIF(AVG(iv.value) OVER (PARTITION BY iv.indicator_id, iv.year), 0) * 100 AS vs_average_pct
FROM indicator_values iv
JOIN indicator_definitions id ON iv.indicator_id = id.id
JOIN counties c ON iv.county_id = c.id
WHERE iv.aggregation_level = 'judet';

-- ============================================
-- FUNCȚII UTILITARE
-- ============================================

-- Funcție pentru calculul ratei de creștere
CREATE OR REPLACE FUNCTION calculate_growth_rate(
    current_value DECIMAL,
    previous_value DECIMAL
) RETURNS DECIMAL AS $$
BEGIN
    IF previous_value IS NULL OR previous_value = 0 THEN
        RETURN NULL;
    END IF;
    RETURN ((current_value - previous_value) / previous_value) * 100;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Funcție pentru CAGR
CREATE OR REPLACE FUNCTION calculate_cagr(
    start_value DECIMAL,
    end_value DECIMAL,
    years INTEGER
) RETURNS DECIMAL AS $$
BEGIN
    IF start_value IS NULL OR start_value <= 0 OR years <= 0 THEN
        RETURN NULL;
    END IF;
    RETURN (POWER(end_value / start_value, 1.0 / years) - 1) * 100;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- ============================================
-- TRIGGERS
-- ============================================

-- Trigger pentru updated_at
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_regions_timestamp
    BEFORE UPDATE ON regions
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trg_counties_timestamp
    BEFORE UPDATE ON counties
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trg_indicators_timestamp
    BEFORE UPDATE ON indicator_definitions
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trg_values_timestamp
    BEFORE UPDATE ON indicator_values
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

-- ============================================
-- GRANTS (pentru producție)
-- ============================================

-- Uncomment pentru producție:
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;
-- GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO app_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;
