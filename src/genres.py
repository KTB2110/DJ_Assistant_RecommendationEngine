"""
Genre similarity engine using audio feature centroids.
"""

import pandas as pd
from sklearn.preprocessing import StandardScaler
from scipy.spatial.distance import pdist, squareform


AUDIO_FEATURES = [
    'energy', 'danceability', 'valence', 'tempo',
    'acousticness', 'instrumentalness', 'speechiness', 
    'liveness', 'loudness'
]


class GenreSimilarity:
    """
    Computes and queries genre similarity based on audio features.
    """
    
    def __init__(self):
        self.genre_profiles = None
        self.genre_profiles_normalized = None
        self.distance_matrix = None
        self.scaler = None
    
    def fit(self, dataset: pd.DataFrame):
        """
        Compute genre profiles and distance matrix from dataset.
        """

        genre_means = dataset.groupby('track_genre')[AUDIO_FEATURES].mean()
        self.genre_profiles = genre_means

        self.scaler = StandardScaler()
        normalized_values = self.scaler.fit_transform(genre_means)
        self.genre_profiles_normalized = pd.DataFrame(
            normalized_values,
            index=genre_means.index,
            columns=genre_means.columns
        )

        distances = pdist(self.genre_profiles_normalized, metric='euclidean')
        self.distance_matrix = pd.DataFrame(
            squareform(distances),
            index=self.genre_profiles_normalized.index,
            columns=self.genre_profiles_normalized.index
        )

    def get_similar_genres(self, genre: str, top_k: int = 10) -> list:
        """
        Get most similar genres with distance and explanation.
        """
        if genre not in self.distance_matrix.index:
            raise ValueError(f"Genre '{genre}' not found in dataset")
        
        # Get distances, sort, skip self (distance = 0)
        distances = self.distance_matrix[genre].sort_values()[1:top_k + 1]
        
        results = []
        for similar_genre, distance in distances.items():
            results.append({
                "genre": similar_genre,
                "distance": round(distance, 3),
                "explanation": self._explain_similarity(genre, similar_genre)
        })
    
        return results
    
    def _explain_similarity(self, genre1: str, genre2: str, top_features: int = 2) -> str:
        """
        Explain why two genres are similar based on their closest features.
        """
        # Get raw feature values for both genres
        profile1 = self.genre_profiles.loc[genre1]
        profile2 = self.genre_profiles.loc[genre2]

        # Calculate absolute difference for each feature
        differences = abs(profile1 - profile2)
        
        # Get the features with smallest differences (most similar)
        closest_features = differences.sort_values().head(top_features).index.tolist()
        
        # Build explanation string
        explanations = []
        for feature in closest_features:
            val1 = profile1[feature]
            val2 = profile2[feature]
            
            # Format based on feature type
            if feature == 'tempo':
                explanations.append(f"{feature} ({val1:.0f} vs {val2:.0f} BPM)")
            elif feature == 'loudness':
                explanations.append(f"{feature} ({val1:.1f} vs {val2:.1f} dB)")
            else:
                explanations.append(f"{feature} ({val1:.2f} vs {val2:.2f})")
        
        return "Similar " + " and ".join(explanations)

if __name__ == "__main__":
    from database import TrackDatabase
    
    # Loading data
    db = TrackDatabase()
    db.load()
    
    # Fitting genre similarity
    gs = GenreSimilarity()
    gs.fit(db.dataset)
    
    # Test it
    results = gs.get_similar_genres("hip-hop", top_k=5)
    for r in results:
        print(f"{r['genre']}: {r['distance']} — {r['explanation']}")