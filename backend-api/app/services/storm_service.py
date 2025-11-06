from datetime import datetime
from sqlite3 import Connection

from app.schemas.storm import Storm, StormCollection


class StormService:
    """Service for querying storm data from the database"""
    
    def __init__(self, db: Connection):
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
        SELECT * FROM storms 
        WHERE strftime('%Y', genesis) = ? 
        AND strftime('%m', genesis) = ?
        ORDER BY ID, time
        """
        
        cursor = self.db.execute(query, (str(year), f"{month:02d}"))
        rows = cursor.fetchall()
        
        # Group rows by storm ID (each storm has multiple time points)
        storms_by_id = {}
        for row in rows:
            storm_id = row['ID']
            if storm_id not in storms_by_id:
                storms_by_id[storm_id] = []
            storms_by_id[storm_id].append(row)
        
        # Build Storm objects from grouped rows
        storms = []
        for storm_id, storm_rows in storms_by_id.items():
            first_row = storm_rows[0]
            
            storm = Storm(
                ID=first_row['ID'],
                ATCF_ID=first_row['ATCF_ID'],
                name=first_row['name'],
                basin=first_row['basin'],
                subbasin=first_row['subbasin'],
                season=first_row['season'],
                genesis=datetime.fromisoformat(first_row['genesis']),
                # Time series data - collect from all rows
                time=[datetime.fromisoformat(row['time']) for row in storm_rows],
                lat=[row['lat'] for row in storm_rows],
                lon=[row['lon'] for row in storm_rows],
                wind=[row['wind'] for row in storm_rows],
                mslp=[row['mslp'] for row in storm_rows],
                speed=[row['speed'] for row in storm_rows],
                dist2land=[row['dist2land'] for row in storm_rows],
                classification=[row['classification'] for row in storm_rows],
                rmw=[row['rmw'] for row in storm_rows],
                basins=[row['basin'] for row in storm_rows],
                subbasins=[row['subbasin'] for row in storm_rows],
                agencies=[row['agency'] for row in storm_rows],
                # Wind radii
                R34_NE=[row['R34_NE'] for row in storm_rows],
                R34_SE=[row['R34_SE'] for row in storm_rows],
                R34_SW=[row['R34_SW'] for row in storm_rows],
                R34_NW=[row['R34_NW'] for row in storm_rows],
                R50_NE=[row['R50_NE'] for row in storm_rows],
                R50_SE=[row['R50_SE'] for row in storm_rows],
                R50_SW=[row['R50_SW'] for row in storm_rows],
                R50_NW=[row['R50_NW'] for row in storm_rows],
                R64_NE=[row['R64_NE'] for row in storm_rows],
                R64_SE=[row['R64_SE'] for row in storm_rows],
                R64_SW=[row['R64_SW'] for row in storm_rows],
                R64_NW=[row['R64_NW'] for row in storm_rows],
            )
            storms.append(storm)
        
        return StormCollection(storms=storms)

