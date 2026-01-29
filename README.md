# Automotive Vest Analytics

Aplicație de analiză a sectorului automotive din Regiunea Vest a României.

## Despre Proiect

Această aplicație oferă un instrument de suport decizional pentru actorii regionali (administrație publică, agenții de dezvoltare, investitori, clustere și mediul academic), oferind o imagine clară asupra performanței, competitivității și tendințelor sectorului automotive.

### Funcționalități

- **Dashboard-uri interactive** cu indicatori cheie (KPIs)
- **Hărți tematice** pentru vizualizare geografică
- **Analize comparative** între județe, sectoare și perioade
- **Proiecții și scenarii** de evoluție
- **Generare automată de rapoarte** (PDF, Excel)
- **Export date** în multiple formate

### Indicatori Monitorizați

| Categorie | Indicatori |
|-----------|------------|
| Structură economică | Nr. firme, dimensiune medie, concentrare (HHI) |
| Piața muncii | Angajați, salarii, productivitate |
| Performanță | Cifră de afaceri, valoare adăugată, export |
| Inovare | Cheltuieli R&D, brevete |
| Sustenabilitate | Dependență importuri |

## Stack Tehnologic

- **Backend:** FastAPI + SQLAlchemy + PostgreSQL
- **Frontend:** Streamlit
- **Analiză:** Pandas, NumPy, SciPy
- **Vizualizări:** Plotly, Folium

## Instalare

### Cerințe

- Python 3.11+
- PostgreSQL 15+
- Docker (opțional)

### Opțiunea 1: Instalare Locală

```bash
# Clonare repository
cd automotive-vest-analytics

# Creare environment virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# sau: venv\Scripts\activate  # Windows

# Instalare dependențe
pip install -r requirements.txt

# Configurare
cp .env.example .env
# Editează .env cu configurările tale

# Inițializare bază de date
python scripts/seed_database.py

# Pornire API
uvicorn app.main:app --reload --port 8000

# Într-un alt terminal - pornire frontend
streamlit run frontend/app.py
```

### Opțiunea 2: Cu Docker

```bash
# Pornire toate serviciile
docker-compose up -d

# Verificare status
docker-compose ps

# Vizualizare logs
docker-compose logs -f
```

## Utilizare

### Acces Aplicație

- **Frontend Streamlit:** http://localhost:8501
- **API Documentation:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Import Date

```bash
# Import date din INS
python scripts/import_ins.py

# Import date din Eurostat
python scripts/import_eurostat.py
```

### API Endpoints

| Endpoint | Descriere |
|----------|-----------|
| `GET /api/v1/indicators` | Lista indicatori |
| `GET /api/v1/indicators/{code}/timeseries` | Serie temporală |
| `GET /api/v1/regions` | Lista regiuni |
| `GET /api/v1/reports/export/excel` | Export Excel |

## Structura Proiectului

```
automotive-vest-analytics/
├── app/
│   ├── api/routes/       # Endpoint-uri API
│   ├── models/           # Modele SQLAlchemy
│   ├── services/         # Logică de business
│   └── database/         # Configurare DB
├── frontend/
│   ├── pages/            # Pagini Streamlit
│   └── components/       # Componente reutilizabile
├── scripts/              # Scripturi import date
├── data/                 # Date locale
└── tests/                # Teste
```

## Surse de Date

- **INS** (Tempo Online) - Date naționale și regionale
- **Eurostat** - Date europene comparative
- **ONRC/ANAF** - Date despre firme (agregate)
- **ADR Vest** - Date regionale specifice

## Dezvoltare

### Rulare Teste

```bash
pytest tests/ -v
```

### Migrări Bază de Date

```bash
# Creare migrare
alembic revision --autogenerate -m "descriere"

# Aplicare migrări
alembic upgrade head
```

## Roadmap

### MVP (Versiunea Curentă)
- [x] Dashboard principal cu 5 KPIs
- [x] Hartă interactivă județe
- [x] Comparații temporale
- [x] Export Excel/CSV

### Versiunea 1.1
- [ ] Integrare API INS (live)
- [ ] Sistem de alerte automate
- [ ] Rapoarte PDF personalizate

### Versiunea 2.0
- [ ] Predicții ML
- [ ] Multi-tenancy
- [ ] API public

## Licență

Proiect dezvoltat pentru Vest Policy Lab.

## Contact

Pentru întrebări sau sugestii, contactați echipa de dezvoltare.
