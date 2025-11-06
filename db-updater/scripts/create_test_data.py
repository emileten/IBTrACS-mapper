"""
Create a test data sample from the IBTrACS CSV.
This script downloads the full CSV, extracts a subset, and saves it for testing.
"""
import pandas as pd
import requests
import tempfile
import os
from pathlib import Path

# Configuration
TEST_DATA_DIR = Path(__file__).parent.parent / "tests" / "data"
TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)
TEST_CSV_PATH = TEST_DATA_DIR / "ibtracs_sample.csv"

# Sample criteria: Get storms from a specific year/season
# Note: SEASON column contains strings, not integers
SAMPLE_SEASON = "2020"  # Adjust as needed (use string)
MAX_STORMS = 10  # Limit number of storms in sample


def download_sample():
    """Download full CSV and create a sample"""
    url = "https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r01/access/csv/ibtracs.ALL.list.v04r01.csv"
    
    print(f"Downloading full IBTrACS CSV...")
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False) as tmp:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                tmp.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    print(f"\rDownloaded: {percent:.1f}%", end='', flush=True)
        
        tmp_path = tmp.name
    
    print(f"\nReading CSV...")
    df = pd.read_csv(tmp_path, low_memory=False, nrows=None)
    print(f"Loaded {len(df)} rows")
    
    # Filter by season
    if 'SEASON' in df.columns:
        # Convert SEASON to string and filter out any non-numeric values (like 'Year' header)
        df['SEASON_STR'] = df['SEASON'].astype(str)
        df_filtered = df[df['SEASON_STR'] == str(SAMPLE_SEASON)].head(MAX_STORMS)
        if len(df_filtered) == 0:
            # If no storms found for that season, try a more recent season
            print(f"No storms found for season {SAMPLE_SEASON}, trying recent seasons...")
            recent_seasons = sorted([s for s in df['SEASON_STR'].unique() if s.isdigit()], reverse=True)[:5]
            print(f"Available recent seasons: {recent_seasons}")
            if recent_seasons:
                df_filtered = df[df['SEASON_STR'] == recent_seasons[0]].head(MAX_STORMS)
                print(f"Using season {recent_seasons[0]} instead")
        df_filtered = df_filtered.drop(columns=['SEASON_STR'], errors='ignore')
    else:
        # If no SEASON column, just take first N storms
        df_filtered = df.head(MAX_STORMS)
    
    print(f"Selected {len(df_filtered)} storms for sample")
    
    # Save sample
    print(f"Saving sample to {TEST_CSV_PATH}...")
    df_filtered.to_csv(TEST_CSV_PATH, index=False)
    
    # Clean up
    os.unlink(tmp_path)
    
    print(f"Test data sample created: {TEST_CSV_PATH}")
    print(f"Sample contains {len(df_filtered)} storms")


if __name__ == "__main__":
    download_sample()

