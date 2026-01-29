"""
FastAPI Application Entry Point
Automotive Vest Analytics API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db
from app.api.routes import indicators_router, regions_router, reports_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager pentru aplicație.
    Rulează la startup și shutdown.
    """
    # Startup
    print(f"Starting {settings.app_name} v{settings.app_version}")
    init_db()
    yield
    # Shutdown
    print("Shutting down...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    ## Automotive Vest Analytics API

    API pentru analiza sectorului automotive din Regiunea Vest a României.

    ### Funcționalități:
    - **Indicatori**: Acces la indicatori statistici și serii temporale
    - **Regiuni**: Informații despre județe și regiuni
    - **Rapoarte**: Generare și export de rapoarte

    ### Surse de date:
    - INS (Institutul Național de Statistică)
    - Eurostat
    - Date regionale ADR Vest
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # În producție, specificați originile permise
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(indicators_router, prefix=settings.api_prefix)
app.include_router(regions_router, prefix=settings.api_prefix)
app.include_router(reports_router, prefix=settings.api_prefix)


@app.get("/")
def root():
    """
    Endpoint principal - informații despre API.
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
        "api_prefix": settings.api_prefix
    }


@app.get("/health")
def health_check():
    """
    Health check endpoint pentru monitorizare.
    """
    return {
        "status": "healthy",
        "version": settings.app_version
    }


@app.get(f"{settings.api_prefix}/info")
def api_info():
    """
    Informații despre configurația API.
    """
    return {
        "region": settings.region_name,
        "counties": settings.counties,
        "data_range": {
            "start": settings.data_start_year,
            "end": settings.data_end_year
        },
        "automotive_caen_codes": settings.automotive_caen_codes
    }
