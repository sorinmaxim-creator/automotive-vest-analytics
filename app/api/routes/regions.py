"""
Endpoint-uri pentru regiuni și județe
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from app.api.dependencies import get_db
from app.models.region import Region, County

router = APIRouter(prefix="/regions", tags=["regions"])


# Schemas Pydantic
class CountyBase(BaseModel):
    name: str
    code: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    population: Optional[int] = None
    area_km2: Optional[float] = None
    is_automotive_hub: bool = False


class CountyResponse(CountyBase):
    id: int
    region_id: int

    class Config:
        from_attributes = True


class RegionBase(BaseModel):
    name: str
    code: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class RegionResponse(RegionBase):
    id: int
    counties: list[CountyResponse] = []

    class Config:
        from_attributes = True


class CountyDetailResponse(CountyResponse):
    """Detalii extinse despre un județ"""
    region_name: str
    # Indicatori sumar - vor fi populați din servicii
    total_companies: Optional[int] = None
    total_employees: Optional[int] = None
    total_turnover: Optional[float] = None


# Endpoints
@router.get("/", response_model=list[RegionResponse])
def list_regions(db: Session = Depends(get_db)):
    """
    Listează toate regiunile disponibile.
    """
    return db.query(Region).all()


@router.get("/{region_code}", response_model=RegionResponse)
def get_region(region_code: str, db: Session = Depends(get_db)):
    """
    Detalii despre o regiune specifică.
    """
    region = db.query(Region).filter(Region.code == region_code).first()

    if not region:
        raise HTTPException(status_code=404, detail="Region not found")

    return region


@router.get("/{region_code}/counties", response_model=list[CountyResponse])
def list_counties_by_region(region_code: str, db: Session = Depends(get_db)):
    """
    Listează județele dintr-o regiune.
    """
    region = db.query(Region).filter(Region.code == region_code).first()

    if not region:
        raise HTTPException(status_code=404, detail="Region not found")

    return region.counties


@router.get("/counties/{county_code}", response_model=CountyDetailResponse)
def get_county(county_code: str, db: Session = Depends(get_db)):
    """
    Detalii despre un județ specific.
    """
    county = db.query(County).filter(County.code == county_code).first()

    if not county:
        raise HTTPException(status_code=404, detail="County not found")

    return CountyDetailResponse(
        id=county.id,
        name=county.name,
        code=county.code,
        region_id=county.region_id,
        region_name=county.region.name,
        latitude=county.latitude,
        longitude=county.longitude,
        population=county.population,
        area_km2=county.area_km2,
        is_automotive_hub=county.is_automotive_hub
    )


@router.get("/counties/{county_code}/map-data")
def get_county_map_data(county_code: str, db: Session = Depends(get_db)):
    """
    Date pentru afișare pe hartă pentru un județ.
    Include coordonate și indicatori principali.
    """
    county = db.query(County).filter(County.code == county_code).first()

    if not county:
        raise HTTPException(status_code=404, detail="County not found")

    return {
        "code": county.code,
        "name": county.name,
        "coordinates": {
            "lat": county.latitude,
            "lon": county.longitude
        },
        "properties": {
            "population": county.population,
            "area_km2": county.area_km2,
            "is_automotive_hub": county.is_automotive_hub
        }
    }


@router.get("/map/all")
def get_all_counties_map_data(db: Session = Depends(get_db)):
    """
    Date pentru hartă pentru toate județele din Regiunea Vest.
    """
    region = db.query(Region).filter(Region.code == "RO42").first()

    if not region:
        return []

    return [
        {
            "code": county.code,
            "name": county.name,
            "coordinates": {
                "lat": county.latitude,
                "lon": county.longitude
            },
            "is_automotive_hub": county.is_automotive_hub
        }
        for county in region.counties
    ]
