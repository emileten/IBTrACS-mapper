from fastapi import APIRouter, Depends
from sqlite3 import Connection

from app.core.database import get_db
from app.schemas.storm import StormCollection
from app.services.storm_service import StormService

router = APIRouter()


@router.get("/storms/{year}/{month}", response_model=StormCollection)
def get_storms(year: int, month: int, db: Connection = Depends(get_db)) -> StormCollection:
    """Get all storms for a given calendar month"""
    service = StormService(db)
    return service.get_storms_by_month(year, month)

