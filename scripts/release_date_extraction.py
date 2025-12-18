"""
One-time script to fetch release dates for all tracks from Spotify API.
"""
import os
import time
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
from tqdm import tqdm  # Progress bar
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent

import sys
sys.path.append(str(PROJECT_ROOT))

from src.database import TrackDatabase

OUTPUT_PATH = PROJECT_ROOT / 'data' / 'processed' / 'track_release_dates.csv'

db = TrackDatabase()
db.load()
df = db.dataset

load_dotenv()

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials())

track_ids = df['track_id'].tolist()

def chunk_list(lst, chunk_size):
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

# Resuming from existing file if present
if os.path.exists(OUTPUT_PATH):
    existing = pd.read_csv(OUTPUT_PATH)
    release_dates = dict(zip(existing['track_id'], existing['release_date']))
    print(f"Resuming from {len(release_dates)} tracks")
    
    # Filtering out track_ids we already have
    track_ids = [tid for tid in track_ids if tid not in release_dates]
    print(f"Remaining tracks to fetch: {len(track_ids)}")
else:
    release_dates = {}

# Now creating batches from only the remaining tracks if existing file was found
batches = list(chunk_list(track_ids, 50))
print(f"Batches to process: {len(batches)}")


# Fetching release dates in batches
for i, batch in enumerate(tqdm(batches, desc="Fetching release dates")):
    results = sp.tracks(batch)
    
    for track in results['tracks']:
        if track is not None:
            release_dates[track['id']] = track['album']['release_date']
        
    time.sleep(0.5)
    
    # Saving every 10 batches (500 tracks)
    if (i + 1) % 10 == 0:
        df_progress = pd.DataFrame(
            list(release_dates.items()), 
            columns=['track_id', 'release_date']
        )
        df_progress.to_csv(OUTPUT_PATH, index=False)
        print(f"\nSaved progress: {len(release_dates)} tracks")

# Final save
df_final = pd.DataFrame(
    list(release_dates.items()), 
    columns=['track_id', 'release_date']
)
df_final.to_csv(OUTPUT_PATH, index=False)
print(f"\nComplete! Saved {len(release_dates)} tracks to {OUTPUT_PATH}")


