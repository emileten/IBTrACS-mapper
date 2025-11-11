from datetime import datetime
from typing import Any

from psycopg2.extensions import connection as PGConnection

from app.schemas.storm import Storm, StormCollection


def _to_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value))


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    return float(value)


class StormService:
    """Service for querying storm data from the database."""
    
    def __init__(self, db: PGConnection):
        self.db = db
    
    def get_storms_by_month(self, year: int, month: int) -> StormCollection:
        """
        Retrieve all storms for a given calendar month
        
        Args:
            year: Calendar year
            month: Calendar month (1-12)
            
        Returns:
            StormCollection containing all storms from that month
        """
        query = """
        SELECT *
        FROM storms
        WHERE EXTRACT(YEAR FROM genesis) = %s
          AND EXTRACT(MONTH FROM genesis) = %s
        ORDER BY "ID", time
        """
        
        with self.db.cursor() as cursor:
            cursor.execute(query, (year, month))
            rows = cursor.fetchall()
        
        # Group rows by storm ID (each storm has multiple time points)
        storms_by_id: dict[str, list[dict[str, Any]]] = {}
        for row in rows:
            storm_id = row["ID"]
            storms_by_id.setdefault(storm_id, []).append(row)
        
        # Build Storm objects from grouped rows
        storms = []
        for storm_id, storm_rows in storms_by_id.items():
            first_row = storm_rows[0]
            
            storm = Storm(
                ID=first_row["ID"],
                ATCF_ID=first_row["ATCF_ID"],
                name=first_row["name"],
                basin=first_row["basin"],
                subbasin=first_row["subbasin"],
                season=int(first_row["season"]),
                genesis=_to_datetime(first_row["genesis"]),
                # Time series data - collect from all rows
                time=[_to_datetime(row["time"]) for row in storm_rows],
                lat=[_to_float(row["lat"]) for row in storm_rows],
                lon=[_to_float(row["lon"]) for row in storm_rows],
                wind=[_to_float(row["wind"]) for row in storm_rows],
                mslp=[_to_float(row["mslp"]) for row in storm_rows],
                speed=[_to_float(row["speed"]) for row in storm_rows],
                dist2land=[_to_float(row["dist2land"]) for row in storm_rows],
                classification=[row["classification"] for row in storm_rows],
                rmw=[_to_float(row["rmw"]) for row in storm_rows],
                basins=[row["basin_time"] if row.get("basin_time") else row["basin"] for row in storm_rows],
                subbasins=[row["subbasin_time"] if row.get("subbasin_time") else row["subbasin"] for row in storm_rows],
                agencies=[row["agency"] for row in storm_rows],
                # Wind radii
                R34_NE=[_to_float(row["R34_NE"]) for row in storm_rows],
                R34_SE=[_to_float(row["R34_SE"]) for row in storm_rows],
                R34_SW=[_to_float(row["R34_SW"]) for row in storm_rows],
                R34_NW=[_to_float(row["R34_NW"]) for row in storm_rows],
                R50_NE=[_to_float(row["R50_NE"]) for row in storm_rows],
                R50_SE=[_to_float(row["R50_SE"]) for row in storm_rows],
                R50_SW=[_to_float(row["R50_SW"]) for row in storm_rows],
                R50_NW=[_to_float(row["R50_NW"]) for row in storm_rows],
                R64_NE=[_to_float(row["R64_NE"]) for row in storm_rows],
                R64_SE=[_to_float(row["R64_SE"]) for row in storm_rows],
                R64_SW=[_to_float(row["R64_SW"]) for row in storm_rows],
                R64_NW=[_to_float(row["R64_NW"]) for row in storm_rows],
            )
            storms.append(storm)
        
        return StormCollection(storms=storms)

