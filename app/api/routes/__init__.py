"""
API Routes Package
"""

from app.api.routes.indicators import router as indicators_router
from app.api.routes.regions import router as regions_router
from app.api.routes.reports import router as reports_router

__all__ = ["indicators_router", "regions_router", "reports_router"]
