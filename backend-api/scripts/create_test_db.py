"""
Create a subset database for testing containing only storms with genesis in August 2025
"""

import sqlite3
import os

# Source and destination paths
SOURCE_DB = "/Users/emiletenezakis/ibtracs/ibtracs/data/storms.db"
DEST_DB = "tests/data/storms.db"

# Create destination directory if it doesn't exist
os.makedirs(os.path.dirname(DEST_DB), exist_ok=True)

# Connect to source database
print(f"Connecting to source database: {SOURCE_DB}")
source_conn = sqlite3.connect(SOURCE_DB)
source_conn.row_factory = sqlite3.Row

# Get table schema
cursor = source_conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='storms'")
create_table_sql = cursor.fetchone()[0]

# Query for storms with genesis in August 2025
print("Querying storms with genesis in August 2025...")
query = """
SELECT * FROM storms 
WHERE strftime('%Y', genesis) = '2025' 
  AND strftime('%m', genesis) = '08'
ORDER BY ID, time
"""
cursor = source_conn.execute(query)
rows = cursor.fetchall()
print(f"Found {len(rows)} rows")

if len(rows) == 0:
    print("WARNING: No storms found for August 2025")
    print("This might be because the data doesn't go that far into the future.")
    print("Would you like to use a different month/year?")
    source_conn.close()
    exit(1)

# Create destination database
print(f"Creating subset database: {DEST_DB}")
if os.path.exists(DEST_DB):
    os.remove(DEST_DB)

dest_conn = sqlite3.connect(DEST_DB)
dest_cursor = dest_conn.cursor()

# Create table with same schema
dest_cursor.execute(create_table_sql)

# Get column names
column_names = [description[0] for description in cursor.description]
placeholders = ','.join(['?'] * len(column_names))

# Insert rows
print(f"Inserting {len(rows)} rows into subset database...")
for row in rows:
    dest_cursor.execute(f"INSERT INTO storms VALUES ({placeholders})", tuple(row))

dest_conn.commit()

# Verify
count = dest_cursor.execute("SELECT COUNT(*) FROM storms").fetchone()[0]
print(f"Subset database created successfully with {count} rows")

# Show unique storms
unique_storms = dest_cursor.execute("""
    SELECT DISTINCT ID, name, basin, season, genesis 
    FROM storms 
    ORDER BY genesis
""").fetchall()

print(f"\nUnique storms in subset ({len(unique_storms)}):")
for storm in unique_storms:
    print(f"  {storm[1]} ({storm[2]}, {storm[3]}) - Genesis: {storm[4]}")

# Close connections
source_conn.close()
dest_conn.close()

print(f"\nTest database created at: {DEST_DB}")

