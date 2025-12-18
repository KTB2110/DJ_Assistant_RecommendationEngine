"""
Database module for loading and searching the Spotify tracks dataset.
"""

from pathlib import Path
from datasets import load_dataset
from thefuzz import fuzz
import pandas as pd


class TrackDatabase:
    """
    Handles loading and querying the Spotify tracks dataset.
    """
    
    def __init__(self):
        """Load the dataset from Hugging Face."""
        self.dataset = None
    
    def load(self):
        """Load the dataset into memory."""
        self.dataset = load_dataset("maharshipandya/spotify-tracks-dataset")['train'].to_pandas()

        # Merging release dates if file exists
        release_dates_path = Path(__file__).parent.parent / 'data' / 'processed' / 'track_release_dates.csv'
        if release_dates_path.exists():
            release_dates = pd.read_csv(release_dates_path)
            release_dates['release_year'] = release_dates['release_date'].str[:4].astype(int)
            
            self.dataset = self.dataset.merge(
                release_dates[['track_id', 'release_year']], 
                on='track_id', 
                how='left'
            )
            print(f"Loaded {len(self.dataset)} tracks with release years")
        else:
            print(f"Loaded {len(self.dataset)} tracks (no release dates file)")
    
    def search(self, query: str, limit: int = 10) -> list:
        """
        Fuzzy search for tracks by name or artist.
        """
        if self.dataset is None:
            raise ValueError("Database not loaded. Call load() first.")
    
        results = []
        
        for _, track in self.dataset.iterrows():
            # Combining track name and artist for matching
            track_string = f"{track['track_name']} {track['artists']}"
            
            # Scoring the match
            score = fuzz.token_set_ratio(query.lower(), track_string.lower())
            
            if score > 60: 
                results.append((score, track.to_dict()))
    
        results.sort(key=lambda x: x[0], reverse=True)
        
        return [track for _, track in results[:limit]]
    
    def get_track(self, track_id: str) -> dict:
        """
        Get a track by its Spotify ID.
        """
        if self.dataset is None:
            raise ValueError("Database not loaded. Call load() first.")
        
        # DataFrame filtering instead of loop
        match = self.dataset[self.dataset['track_id'] == track_id]
        
        if len(match) == 0:
            return None
        
        return match.iloc[0].to_dict()  # Return first match as dict

if __name__ == "__main__":
    db = TrackDatabase()
    
    print("Loading database...")
    db.load()
    print(f"Loaded {len(db.dataset)} tracks")
    
    print("\nSearching for 'Strobe Deadmau5'...")
    results = db.search("Strobe Deadmau5", limit=5)
    
    for track in results:
        print(f"  {track['track_name']} - {track['artists']}: Release in {track.get('release_year', 'N/A')}")