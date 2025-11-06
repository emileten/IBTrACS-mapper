from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class Storm(BaseModel):
    """Schema for a tropical cyclone storm from IBTrACS database"""
    
    # Identifiers
    ID: str = Field(..., description="Unique ID assigned by IBTrACS")
    ATCF_ID: Optional[str] = Field(None, description="ATCF ID, if available")
    name: str = Field(..., description='Storm name or "NOT_NAMED"')
    
    # Storm metadata
    basin: str = Field(..., description="Basin in which the storm formed")
    subbasin: str = Field(..., description="Subbasin in which the storm formed")
    season: int = Field(..., description="Season/year of storm formation")
    genesis: datetime = Field(..., description="Time of genesis")
    
    # Time series data - arrays of observations
    time: list[datetime] = Field(..., description="Observation times")
    lat: list[float] = Field(..., description="Storm latitude (degrees)")
    lon: list[float] = Field(..., description="Storm longitude (degrees)")
    wind: list[float | None] = Field(..., description="Maximum sustained wind (kt)")
    mslp: list[float | None] = Field(..., description="Central pressure (hPa)")
    speed: list[float | None] = Field(..., description="Storm forward speed (kt)")
    dist2land: list[float | None] = Field(..., description="Distance to land (km)")
    classification: list[str] = Field(..., description="Storm classification")
    rmw: list[float | None] = Field(..., description="Radius of maximum wind (nm)")
    
    # Regional tracking
    basins: list[str] = Field(..., description="Basin identifiers over time")
    subbasins: list[str] = Field(..., description="Subbasin identifiers over time")
    agencies: list[str] = Field(..., description="Reporting agencies over time")
    
    # Wind radii - 34 kt
    R34_NE: list[float | None] = Field(..., description="34 kt wind radii NE quadrant (nm)")
    R34_SE: list[float | None] = Field(..., description="34 kt wind radii SE quadrant (nm)")
    R34_SW: list[float | None] = Field(..., description="34 kt wind radii SW quadrant (nm)")
    R34_NW: list[float | None] = Field(..., description="34 kt wind radii NW quadrant (nm)")
    
    # Wind radii - 50 kt
    R50_NE: list[float | None] = Field(..., description="50 kt wind radii NE quadrant (nm)")
    R50_SE: list[float | None] = Field(..., description="50 kt wind radii SE quadrant (nm)")
    R50_SW: list[float | None] = Field(..., description="50 kt wind radii SW quadrant (nm)")
    R50_NW: list[float | None] = Field(..., description="50 kt wind radii NW quadrant (nm)")
    
    # Wind radii - 64 kt
    R64_NE: list[float | None] = Field(..., description="64 kt wind radii NE quadrant (nm)")
    R64_SE: list[float | None] = Field(..., description="64 kt wind radii SE quadrant (nm)")
    R64_SW: list[float | None] = Field(..., description="64 kt wind radii SW quadrant (nm)")
    R64_NW: list[float | None] = Field(..., description="64 kt wind radii NW quadrant (nm)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "ID": "2005236N16314",
                "ATCF_ID": "AL122005",
                "name": "KATRINA",
                "basin": "NA",
                "subbasin": "GM",
                "season": 2005,
                "genesis": "2005-08-23T18:00:00",
                "time": ["2005-08-23T18:00:00"],
                "lat": [23.1],
                "lon": [-75.1],
                "wind": [30.0],
                "mslp": [1008.0],
                "speed": [10.5],
                "dist2land": [150.0],
                "classification": ["TS"],
                "rmw": [25.0],
                "basins": ["NA"],
                "subbasins": ["GM"],
                "agencies": ["hurdat_atl"],
                "R34_NE": [0.0],
                "R34_SE": [0.0],
                "R34_SW": [0.0],
                "R34_NW": [0.0],
                "R50_NE": [0.0],
                "R50_SE": [0.0],
                "R50_SW": [0.0],
                "R50_NW": [0.0],
                "R64_NE": [0.0],
                "R64_SE": [0.0],
                "R64_SW": [0.0],
                "R64_NW": [0.0],
            }
        }


class StormCollection(BaseModel):
    """Schema for a collection of tropical cyclone storms"""
    
    storms: list["Storm"] = Field(..., description="List of storms")
    
    class Config:
        json_schema_extra = {
            "example": {
                "storms": []
            }
        }

