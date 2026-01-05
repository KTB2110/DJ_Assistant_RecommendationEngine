"""
DJ Track Recommender - combines all scoring logic to recommend compatible tracks.
"""

from src.camelot import spotify_to_camelot, camelot_similarity
from src.scoring import bpm_compatibility, feature_compatibility, loudness_compatibility
from src.camelot import spotify_to_camelot, camelot_similarity, get_musical_key
from src.database import TrackDatabase
from src.genres import GenreSimilarity
import pandas as pd

AUDIO_FEATURES = [
    'energy', 'danceability', 'valence', 'tempo',
    'acousticness', 'instrumentalness', 'speechiness',
    'liveness', 'loudness'
]

DEFAULT_MASTER_WEIGHTS = {
    'bpm': 0.35,
    'energy': 0.35,
    'features': 0.30
}

ADVANCED_MASTER_WEIGHTS = {
    'bpm': 0.275,
    'energy': 0.275,
    'features': 0.45
}

DEFAULT_FEATURE_WEIGHTS = {
    'danceability': 1.0,
    'valence': 1.0,
    'acousticness': 1.0,
    'instrumentalness': 1.0,
    'speechiness': 1.0,
    'liveness': 1.0,
    'loudness': 1.0
}   

DEFAULT_FEATURE_DIRECTIONS = {
    'danceability': 'maintain',
    'valence': 'maintain',
    'acousticness': 'maintain',
    'instrumentalness': 'maintain',
    'speechiness': 'maintain',
    'liveness': 'maintain',
    'loudness': 'maintain'
}


class DJRecommender:
    """
    Recommends tracks based on harmonic, BPM, and energy compatibility.
    """
    
    def __init__(self, database: TrackDatabase, genre_engine: GenreSimilarity = None):
        """
        Args:
            database: Loaded TrackDatabase instance
            genre_engine: GenreSimilarity instance for genre matching
        """

        if database.dataset is None:
            raise ValueError("Database must be loaded first")
        if genre_engine.distance_matrix is None:
            raise ValueError("GenreSimilarity must be fitted first")
        

        self.db = database
        self.genre_engine = genre_engine

    def _filter_by_genre(self, current_track: dict, genre_filter: list = None) -> pd.DataFrame:
        """
        Filter database by genre or similar genres.
        """

        df = self.db.dataset.copy()

        df = df[df['track_id'] != current_track.get('track_id')]
        if not genre_filter:
            similar_genres = self.genre_engine.get_similar_genres(current_track.get('track_genre'), top_k=5)
            genre_filter = [g['genre'] for g in similar_genres]
            genre_filter.append(current_track.get('track_genre'))
            

        return df[df['track_genre'].isin(genre_filter)]

    def _build_target_vector(self, current_track: dict, directions: dict, step: float = 0.15) -> dict:
        """Build target vector based on directions."""
        target = {}
        
        for feature, direction in directions.items():
            current_value = current_track.get(feature, 0.5)
            
            if direction in ["build", "faster"]:
                target[feature] = min(1.0, current_value + step)
            elif direction in ["drop", "slower"]:
                target[feature] = max(0.0, current_value - step)
            else:
                target[feature] = current_value
        
        return target

    def _is_custom_feature_weights(self, feature_weights: dict) -> bool:
        """Check if user has customized any feature weights."""
        
        for key, value in feature_weights.items():
            if DEFAULT_FEATURE_WEIGHTS.get(key) != value:
                return True
        return False

    def _vector_similarity(self, candidate: dict, target: dict, features: list, weights: dict = None) -> float:
        """Calculate weighted cosine similarity."""
        import numpy as np
        from sklearn.metrics.pairwise import cosine_similarity
        
        if weights is None:
            weights = {f: 1.0 for f in features}
        
        candidate_vec = np.array([candidate.get(f, 0.5) * weights.get(f, 1.0) for f in features])
        target_vec = np.array([target.get(f, 0.5) * weights.get(f, 1.0) for f in features])
        
        similarity = cosine_similarity([candidate_vec], [target_vec])[0][0]
        
        return max(0.0, similarity)

    def _score_candidates(self, current_track, candidates, bpm_direction, energy_direction, 
                        feature_directions, master_weights, feature_weights, bpm_tolerance):
        
        results = []
        current_camelot = spotify_to_camelot(current_track['key'], current_track['mode'])
        
        target = self._build_target_vector(current_track, feature_directions)

        # Check if user customized feature weights
        if self._is_custom_feature_weights(feature_weights):
            master_weights = ADVANCED_MASTER_WEIGHTS.copy()
        
        for _, candidate in candidates.iterrows():
            scores = {}
            
            # 1. BPM score (rule-based)
            scores['bpm'] = bpm_compatibility(
                current_track['tempo'],
                candidate['tempo'],
                tolerance=bpm_tolerance,
                direction=bpm_direction
            )
            
            # 2. Energy score (rule-based, separate from features)
            scores['energy'] = feature_compatibility(
                current_track['energy'],
                candidate['energy'],
                direction=energy_direction
            )
            
            # 3. Feature similarity (vector-based, excludes energy)
            feature_list = [f for f in feature_directions.keys() if f != 'loudness']
            feature_sim = self._vector_similarity(
                candidate.to_dict(), 
                target, 
                feature_list,
                feature_weights
            )

            loudness_score = loudness_compatibility(
                current_track['loudness'],
                candidate['loudness'],
                direction=feature_directions.get('loudness', 'maintain')
            )

            scores['features'] = feature_sim * 0.85 + loudness_score * 0.15
            
            # 4. Total score (weighted)
            scores['total_score'] = (
                scores['bpm'] * master_weights['bpm'] +
                scores['energy'] * master_weights['energy'] +
                scores['features'] * master_weights['features']
            )
            
            # 5. Camelot info
            candidate_camelot = spotify_to_camelot(candidate['key'], candidate['mode'])
            camelot_info = {
                'camelot_key': candidate_camelot,
                'camelot_score': camelot_similarity(current_camelot, candidate_camelot),
                'musical_key': get_musical_key(candidate['key'], candidate['mode'])
            }
            
            results.append({
                'track': candidate.to_dict(),
                'scores': scores,
                'total_score': scores['total_score'],
                'camelot_info': camelot_info
            })
        
        return results


    def recommend(
        self,
        current_track: dict,
        bpm_direction: str = "maintain",
        energy_direction: str = "maintain",
        feature_directions: dict = None,
        limit: int = 10,
        master_weights: dict = None,
        feature_weights: dict = None,
        bpm_tolerance: float = 0.07,
        genre_filter: list = None,
        camelot_threshold: float = 0.7
    ) -> list:
        
        # Set defaults
        if feature_directions is None:
            feature_directions = DEFAULT_FEATURE_DIRECTIONS.copy()
        if feature_weights is None:
            feature_weights = DEFAULT_FEATURE_WEIGHTS.copy()
        if master_weights is None:
            master_weights = DEFAULT_MASTER_WEIGHTS.copy()
        
        # 1. Filter by genre
        candidates = self._filter_by_genre(current_track, genre_filter)
        
        # 2. Score all candidates
        results = self._score_candidates(
            current_track, candidates, bpm_direction, energy_direction,
            feature_directions, master_weights, feature_weights, bpm_tolerance
        )
        
        # 3. Filter by harmonic compatibility
        harmonically_compatible = [
            r for r in results
            if r['camelot_info']['camelot_score'] >= camelot_threshold
        ]

        # 3.5 Remove duplicates by track name + artist
        seen_tracks = set()
        unique_results = []
        for r in harmonically_compatible:
            track_key = (r['track']['track_name'].lower(), r['track']['artists'].lower())
            if track_key not in seen_tracks:
                seen_tracks.add(track_key)
                unique_results.append(r)
        harmonically_compatible = unique_results
        
        # 4. Sort by total_score (vibe match)
        harmonically_compatible.sort(key=lambda x: x['total_score'], reverse=True)
        
        # 5. Return top results
        return harmonically_compatible[:limit]
    
