"""
DJ Track Recommender - combines all scoring logic to recommend compatible tracks.
"""

from src.camelot import spotify_to_camelot, camelot_similarity
from src.scoring import bpm_compatibility, energy_compatibility, combined_score
from src.database import TrackDatabase


class DJRecommender:
    """
    Recommends tracks based on harmonic, BPM, and energy compatibility.
    """
    
    def __init__(self, database: TrackDatabase):
        """
        Args:
            database: Loaded TrackDatabase instance
        """
        self.db = database
    
    def recommend(
        self,
        current_track: dict,
        limit: int = 10,
        energy_direction: str = "maintain",
        weights: dict = None
    ) -> list:
        """
        Get track recommendations based on the current track.
        
        Args:
            current_track: The track dict to match against
            limit: Number of recommendations to return
            energy_direction: "maintain", "build", or "drop"
            weights: Scoring weights for camelot, bpm, energy
        
        Returns:
            List of (track, score, explanation) tuples
        """