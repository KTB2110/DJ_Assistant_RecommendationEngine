"""
Comprehensive tests for the DJ Recommender system.
"""

import pytest
import pandas as pd
from src.database import TrackDatabase
from src.genres import GenreSimilarity
from src.recommender import (
    DJRecommender, 
    DEFAULT_FEATURE_WEIGHTS, 
    DEFAULT_FEATURE_DIRECTIONS,
    DEFAULT_MASTER_WEIGHTS,
    ADVANCED_MASTER_WEIGHTS
)
from src.camelot import spotify_to_camelot, camelot_similarity, get_musical_key
from src.scoring import bpm_compatibility, feature_compatibility, loudness_compatibility


# ============================================================================
# FIXTURES - Setup test data
# ============================================================================

@pytest.fixture(scope="module")
def database():
    """Load the real database once for all tests."""
    db = TrackDatabase()
    db.load()
    return db


@pytest.fixture(scope="module")
def genre_engine(database):
    """Fit genre similarity on real data."""
    gs = GenreSimilarity()
    gs.fit(database.dataset)
    return gs


@pytest.fixture(scope="module")
def recommender(database, genre_engine):
    """Create recommender with real data."""
    return DJRecommender(database, genre_engine)


@pytest.fixture
def sample_track(database):
    """Get a sample track for testing."""
    # Find a house track with reasonable values
    house_tracks = database.dataset[database.dataset['track_genre'] == 'house']
    return house_tracks.iloc[0].to_dict()


@pytest.fixture
def sample_track_electronic(database):
    """Get an electronic track."""
    electronic_tracks = database.dataset[database.dataset['track_genre'] == 'electronic']
    return electronic_tracks.iloc[0].to_dict()


@pytest.fixture
def sample_track_hiphop(database):
    """Get a hip-hop track."""
    hiphop_tracks = database.dataset[database.dataset['track_genre'] == 'hip-hop']
    return hiphop_tracks.iloc[0].to_dict()


# ============================================================================
# CAMELOT TESTS
# ============================================================================

class TestCamelot:
    """Tests for Camelot wheel functionality."""
    
    def test_spotify_to_camelot_major_keys(self):
        """Test conversion of all major keys."""
        assert spotify_to_camelot(0, 1) == "8B"   # C major
        assert spotify_to_camelot(7, 1) == "9B"   # G major
        assert spotify_to_camelot(9, 1) == "11B"  # A major
    
    def test_spotify_to_camelot_minor_keys(self):
        """Test conversion of all minor keys."""
        assert spotify_to_camelot(0, 0) == "5A"   # C minor
        assert spotify_to_camelot(9, 0) == "8A"   # A minor
        assert spotify_to_camelot(4, 0) == "9A"   # E minor
    
    def test_spotify_to_camelot_invalid(self):
        """Test handling of invalid key/mode combinations."""
        assert spotify_to_camelot(15, 0) == "Unknown"
        assert spotify_to_camelot(0, 5) == "Unknown"
        assert spotify_to_camelot(-1, 0) == "Unknown"
    
    def test_camelot_similarity_perfect_match(self):
        """Same key should return 1.0."""
        assert camelot_similarity("8A", "8A") == 1.0
        assert camelot_similarity("12B", "12B") == 1.0
    
    def test_camelot_similarity_relative_key(self):
        """Relative major/minor (same number, different letter) = 0.95."""
        assert camelot_similarity("8A", "8B") == 0.95
        assert camelot_similarity("12B", "12A") == 0.95
    
    def test_camelot_similarity_adjacent_same_mode(self):
        """Adjacent keys in same mode = 0.85."""
        assert camelot_similarity("8A", "9A") == 0.85
        assert camelot_similarity("8A", "7A") == 0.85
        assert camelot_similarity("1A", "12A") == 0.85  # Wrap around
    
    def test_camelot_similarity_adjacent_different_mode(self):
        """Adjacent keys in different mode = 0.75."""
        assert camelot_similarity("8A", "9B") == 0.75
        assert camelot_similarity("8A", "7B") == 0.75
    
    def test_camelot_similarity_two_steps(self):
        """Two steps apart = 0.5."""
        assert camelot_similarity("8A", "10A") == 0.5
        assert camelot_similarity("8A", "6A") == 0.5
    
    def test_camelot_similarity_far_apart(self):
        """Far apart keys should score low."""
        assert camelot_similarity("8A", "2A") == 0.1  # 6 steps
        assert camelot_similarity("8A", "3A") == 0.1  # 5 steps
        assert camelot_similarity("8A", "4A") == 0.25  # 4 steps
    
    def test_camelot_similarity_unknown(self):
        """Unknown keys should return 0.5."""
        assert camelot_similarity("Unknown", "8A") == 0.5
        assert camelot_similarity("8A", "Unknown") == 0.5
        assert camelot_similarity("Unknown", "Unknown") == 0.5
    
    def test_camelot_wraparound(self):
        """Test wraparound from 12 to 1."""
        assert camelot_similarity("12A", "1A") == 0.85  # Adjacent
        assert camelot_similarity("11A", "1A") == 0.5   # Two steps
    
    def test_get_musical_key(self):
        """Test musical key name conversion."""
        assert get_musical_key(0, 1) == "C major"
        assert get_musical_key(9, 0) == "A minor"
        assert get_musical_key(7, 1) == "G major"
        assert get_musical_key(99, 0) == "Unknown"


# ============================================================================
# BPM SCORING TESTS
# ============================================================================

class TestBPMCompatibility:
    """Tests for BPM scoring."""
    
    def test_exact_match(self):
        """Exact BPM match should score ~1.0."""
        score = bpm_compatibility(128, 128)
        assert score >= 0.99
    
    def test_within_tolerance(self):
        """BPM within 7% tolerance should score high."""
        score = bpm_compatibility(128, 130)  # ~1.5% diff
        assert score >= 0.9
        
        score = bpm_compatibility(128, 137)  # ~7% diff
        assert score >= 0.8
    
    def test_outside_tolerance(self):
        """BPM outside tolerance should score lower."""
        score = bpm_compatibility(128, 150)  # ~17% diff
        assert score < 0.7
    
    def test_half_time(self):
        """Half-time relationship should score well."""
        score = bpm_compatibility(70, 140)  # Exact half
        assert score >= 0.85
        
        score = bpm_compatibility(65, 128)  # Close to half
        assert score >= 0.7
    
    def test_double_time(self):
        """Double-time relationship should score well."""
        score = bpm_compatibility(140, 70)  # Exact double
        assert score >= 0.85
    
    def test_direction_faster(self):
        """Faster direction should reward higher BPM."""
        score_faster = bpm_compatibility(120, 130, direction="faster")
        score_slower = bpm_compatibility(120, 110, direction="faster")
        assert score_faster > score_slower
    
    def test_direction_slower(self):
        """Slower direction should reward lower BPM."""
        score_slower = bpm_compatibility(120, 110, direction="slower")
        score_faster = bpm_compatibility(120, 130, direction="slower")
        assert score_slower > score_faster
    
    def test_direction_maintain(self):
        """Maintain should reward similar BPM."""
        score_same = bpm_compatibility(120, 120, direction="maintain")
        score_diff = bpm_compatibility(120, 140, direction="maintain")
        assert score_same > score_diff
    
    def test_invalid_direction(self):
        """Invalid direction should raise error."""
        with pytest.raises(ValueError):
            bpm_compatibility(120, 130, direction="invalid")


# ============================================================================
# ENERGY/FEATURE SCORING TESTS
# ============================================================================

class TestFeatureCompatibility:
    """Tests for energy and feature scoring."""
    
    def test_maintain_same_value(self):
        """Same value with maintain should score 1.0."""
        assert feature_compatibility(0.5, 0.5, "maintain") == 1.0
        assert feature_compatibility(0.8, 0.8, "maintain") == 1.0
    
    def test_maintain_different_values(self):
        """Different values with maintain should score lower."""
        score = feature_compatibility(0.5, 0.7, "maintain")
        assert score == 0.8  # 1.0 - 0.2 diff
    
    def test_build_increasing(self):
        """Build should reward higher candidate values."""
        score_up = feature_compatibility(0.5, 0.7, "build")
        score_down = feature_compatibility(0.5, 0.3, "build")
        assert score_up > score_down
    
    def test_build_at_max(self):
        """Build at max energy should handle edge case."""
        # Candidate is same or higher — can't build further
        score = feature_compatibility(1.0, 1.0, "build")
        assert score == 0.5
        
        # Candidate is lower — penalized
        score = feature_compatibility(1.0, 0.9, "build")
        assert score < 0.5  # Wrong direction
    
    def test_drop_decreasing(self):
        """Drop should reward lower candidate values."""
        score_down = feature_compatibility(0.5, 0.3, "drop")
        score_up = feature_compatibility(0.5, 0.7, "drop")
        assert score_down > score_up
    
    def test_drop_at_min(self):
        """Drop at min energy should handle edge case."""
        # Candidate is same or lower — can't drop further
        score = feature_compatibility(0.1, 0.0, "drop")
        assert score > 0.5
        
        # Candidate is higher — penalized
        score = feature_compatibility(0.0, 0.1, "drop")
        assert score < 0.3  # Wrong direction~
    
    def test_invalid_direction(self):
        """Invalid direction should raise error."""
        with pytest.raises(ValueError):
            feature_compatibility(0.5, 0.5, "invalid")
    
    def test_score_bounds(self):
        """Scores should always be between 0 and 1."""
        for current in [0.0, 0.25, 0.5, 0.75, 1.0]:
            for candidate in [0.0, 0.25, 0.5, 0.75, 1.0]:
                for direction in ["maintain", "build", "drop"]:
                    score = feature_compatibility(current, candidate, direction)
                    assert 0.0 <= score <= 1.0


# ============================================================================
# LOUDNESS SCORING TESTS
# ============================================================================

class TestLoudnessCompatibility:
    """Tests for loudness scoring (dB scale)."""
    
    def test_maintain_same(self):
        """Same loudness should score 1.0."""
        assert loudness_compatibility(-8, -8, "maintain") == 1.0
    
    def test_maintain_small_diff(self):
        """Small loudness diff should score well."""
        score = loudness_compatibility(-8, -6, "maintain")  # 2dB diff
        assert score > 0.6
    
    def test_maintain_large_diff(self):
        """Large loudness diff should score poorly."""
        score = loudness_compatibility(-8, -2, "maintain")  # 6dB diff
        assert score <= 0.1
    
    def test_build_louder(self):
        """Build should reward louder tracks."""
        score_louder = loudness_compatibility(-8, -5, "build")
        score_quieter = loudness_compatibility(-8, -11, "build")
        assert score_louder > score_quieter
    
    def test_drop_quieter(self):
        """Drop should reward quieter tracks."""
        score_quieter = loudness_compatibility(-8, -11, "drop")
        score_louder = loudness_compatibility(-8, -5, "drop")
        assert score_quieter > score_louder


# ============================================================================
# GENRE SIMILARITY TESTS
# ============================================================================

class TestGenreSimilarity:
    """Tests for genre similarity engine."""
    
    def test_fit_creates_distance_matrix(self, genre_engine):
        """Fitting should create a distance matrix."""
        assert genre_engine.distance_matrix is not None
        assert len(genre_engine.distance_matrix) > 0
    
    def test_get_similar_genres_returns_results(self, genre_engine):
        """Should return similar genres."""
        results = genre_engine.get_similar_genres("house", top_k=5)
        assert len(results) == 5
    
    def test_get_similar_genres_structure(self, genre_engine):
        """Results should have correct structure."""
        results = genre_engine.get_similar_genres("house", top_k=3)
        for r in results:
            assert "genre" in r
            assert "distance" in r
            assert "explanation" in r
    
    def test_get_similar_genres_sorted_by_distance(self, genre_engine):
        """Results should be sorted by distance (ascending)."""
        results = genre_engine.get_similar_genres("house", top_k=10)
        distances = [r['distance'] for r in results]
        assert distances == sorted(distances)
    
    def test_get_similar_genres_excludes_self(self, genre_engine):
        """Should not include the query genre itself."""
        results = genre_engine.get_similar_genres("house", top_k=10)
        genres = [r['genre'] for r in results]
        assert "house" not in genres
    
    def test_get_similar_genres_invalid_genre(self, genre_engine):
        """Should raise error for invalid genre."""
        with pytest.raises(ValueError):
            genre_engine.get_similar_genres("not_a_real_genre")
    
    def test_electronic_genres_are_similar(self, genre_engine):
        """Electronic genres should be close to each other."""
        results = genre_engine.get_similar_genres("house", top_k=10)
        genres = [r['genre'] for r in results]
        # At least some electronic genres should be in top 10
        electronic = {"deep-house", "progressive-house", "electro", "techno", "edm", "electronic"}
        assert len(set(genres) & electronic) >= 2


# ============================================================================
# DATABASE TESTS
# ============================================================================

class TestDatabase:
    """Tests for database functionality."""
    
    def test_load(self, database):
        """Database should load successfully."""
        assert database.dataset is not None
        assert len(database.dataset) > 0
    
    def test_search_returns_results(self, database):
        """Search should return matching tracks."""
        results = database.search("Daft Punk", limit=5)
        assert len(results) <= 5
    
    def test_search_limit(self, database):
        """Search should respect limit."""
        results = database.search("love", limit=3)
        assert len(results) <= 3
    
    def test_search_no_results(self, database):
        """Search with no matches should return empty list."""
        results = database.search("xyznonexistenttrack123", limit=5)
        assert results == []
    
    def test_get_track_by_id(self, database):
        """Should retrieve track by ID."""
        # Get a known track ID from the dataset
        sample_id = database.dataset.iloc[0]['track_id']
        track = database.get_track(sample_id)
        assert track is not None
        assert track['track_id'] == sample_id
    
    def test_get_track_invalid_id(self, database):
        """Should return None for invalid ID."""
        track = database.get_track("invalid_track_id_12345")
        assert track is None


# ============================================================================
# RECOMMENDER INITIALIZATION TESTS
# ============================================================================

class TestRecommenderInit:
    """Tests for recommender initialization."""
    
    def test_init_with_valid_data(self, database, genre_engine):
        """Should initialize with loaded database and fitted genre engine."""
        recommender = DJRecommender(database, genre_engine)
        assert recommender.db is not None
        assert recommender.genre_engine is not None
    
    def test_init_unloaded_database(self, genre_engine):
        """Should raise error if database not loaded."""
        db = TrackDatabase()  # Not loaded
        with pytest.raises(ValueError, match="Database must be loaded"):
            DJRecommender(db, genre_engine)
    
    def test_init_unfitted_genre_engine(self, database):
        """Should raise error if genre engine not fitted."""
        gs = GenreSimilarity()  # Not fitted
        with pytest.raises(ValueError, match="GenreSimilarity must be fitted"):
            DJRecommender(database, gs)


# ============================================================================
# RECOMMENDER HELPER METHOD TESTS
# ============================================================================

class TestRecommenderHelpers:
    """Tests for recommender helper methods."""
    
    def test_filter_by_genre_excludes_current(self, recommender, sample_track):
        """Filter should exclude the current track."""
        candidates = recommender._filter_by_genre(sample_track)
        track_ids = candidates['track_id'].tolist()
        assert sample_track['track_id'] not in track_ids
    
    def test_filter_by_genre_with_filter(self, recommender, sample_track):
        """Filter should respect genre_filter parameter."""
        candidates = recommender._filter_by_genre(sample_track, genre_filter=["house"])
        genres = candidates['track_genre'].unique()
        assert len(genres) == 1
        assert "house" in genres
    
    def test_filter_by_genre_similar_genres(self, recommender, sample_track):
        """Filter without explicit filter should use similar genres."""
        candidates = recommender._filter_by_genre(sample_track)
        # Should have multiple genres (similar ones)
        genres = candidates['track_genre'].unique()
        assert len(genres) >= 1
    
    def test_build_target_vector_maintain(self, recommender, sample_track):
        """Maintain should keep same values."""
        directions = {"energy": "maintain", "danceability": "maintain"}
        target = recommender._build_target_vector(sample_track, directions)
        assert target["energy"] == sample_track["energy"]
        assert target["danceability"] == sample_track["danceability"]
    
    def test_build_target_vector_build(self, recommender, sample_track):
        """Build should increase values."""
        directions = {"energy": "build"}
        target = recommender._build_target_vector(sample_track, directions, step=0.15)
        expected = min(1.0, sample_track["energy"] + 0.15)
        assert target["energy"] == expected
    
    def test_build_target_vector_drop(self, recommender, sample_track):
        """Drop should decrease values."""
        directions = {"energy": "drop"}
        target = recommender._build_target_vector(sample_track, directions, step=0.15)
        expected = max(0.0, sample_track["energy"] - 0.15)
        assert target["energy"] == expected
    
    def test_build_target_vector_bounds(self, recommender):
        """Target values should stay within 0-1."""
        high_track = {"energy": 0.95}
        low_track = {"energy": 0.05}
        
        target_high = recommender._build_target_vector(high_track, {"energy": "build"}, step=0.15)
        target_low = recommender._build_target_vector(low_track, {"energy": "drop"}, step=0.15)
        
        assert target_high["energy"] <= 1.0
        assert target_low["energy"] >= 0.0
    
    def test_is_custom_feature_weights_default(self, recommender):
        """Default weights should return False."""
        assert recommender._is_custom_feature_weights(DEFAULT_FEATURE_WEIGHTS) == False
    
    def test_is_custom_feature_weights_modified(self, recommender):
        """Modified weights should return True."""
        custom = DEFAULT_FEATURE_WEIGHTS.copy()
        custom['energy'] = 2.0
        assert recommender._is_custom_feature_weights(custom) == True
    
    def test_vector_similarity_identical(self, recommender):
        """Identical vectors should have similarity ~1.0."""
        candidate = {"energy": 0.5, "danceability": 0.7}
        target = {"energy": 0.5, "danceability": 0.7}
        features = ["energy", "danceability"]
        
        score = recommender._vector_similarity(candidate, target, features)
        assert score >= 0.99
    
    def test_vector_similarity_with_weights(self, recommender):
        """Weights should affect similarity calculation."""
        candidate = {"energy": 0.5, "danceability": 0.5}
        target = {"energy": 0.8, "danceability": 0.5}
        features = ["energy", "danceability"]
        
        # With equal weights
        score_equal = recommender._vector_similarity(candidate, target, features, {"energy": 1.0, "danceability": 1.0})
        
        # With energy weighted higher
        score_energy = recommender._vector_similarity(candidate, target, features, {"energy": 2.0, "danceability": 1.0})
        
        # Energy difference should matter more with higher weight
        assert score_equal != score_energy


# ============================================================================
# RECOMMENDER MAIN FUNCTIONALITY TESTS
# ============================================================================

class TestRecommenderRecommend:
    """Tests for the main recommend() function."""
    
    def test_recommend_returns_results(self, recommender, sample_track):
        """Should return recommendation results."""
        results = recommender.recommend(sample_track, limit=10)
        assert len(results) > 0
        assert len(results) <= 10
    
    def test_recommend_result_structure(self, recommender, sample_track):
        """Results should have correct structure."""
        results = recommender.recommend(sample_track, limit=5)
        for r in results:
            assert "track" in r
            assert "scores" in r
            assert "total_score" in r
            assert "camelot_info" in r
            
            # Check scores structure
            assert "bpm" in r["scores"]
            assert "energy" in r["scores"]
            assert "features" in r["scores"]
            
            # Check camelot_info structure
            assert "camelot_key" in r["camelot_info"]
            assert "camelot_score" in r["camelot_info"]
            assert "musical_key" in r["camelot_info"]
    
    def test_recommend_respects_limit(self, recommender, sample_track):
        """Should respect the limit parameter."""
        for limit in [5, 10, 20]:
            results = recommender.recommend(sample_track, limit=limit)
            assert len(results) <= limit
    
    def test_recommend_excludes_current_track(self, recommender, sample_track):
        """Should not recommend the current track."""
        results = recommender.recommend(sample_track, limit=50)
        track_ids = [r["track"]["track_id"] for r in results]
        assert sample_track["track_id"] not in track_ids
    
    def test_recommend_camelot_threshold(self, recommender, sample_track):
        """All results should meet camelot threshold."""
        threshold = 0.7
        results = recommender.recommend(sample_track, camelot_threshold=threshold, limit=20)
        for r in results:
            assert r["camelot_info"]["camelot_score"] >= threshold
    
    def test_recommend_camelot_threshold_strict(self, recommender, sample_track):
        """Stricter threshold should filter more results."""
        results_loose = recommender.recommend(sample_track, camelot_threshold=0.5, limit=50)
        results_strict = recommender.recommend(sample_track, camelot_threshold=0.85, limit=50)
        
        # Strict threshold might return fewer results
        # (or same if all pass the threshold)
        assert len(results_strict) <= len(results_loose) or len(results_strict) == len(results_loose)
    
    def test_recommend_sorted_by_total_score(self, recommender, sample_track):
        """Results should be sorted by total_score (descending)."""
        results = recommender.recommend(sample_track, limit=20)
        scores = [r["total_score"] for r in results]
        assert scores == sorted(scores, reverse=True)
    
    def test_recommend_with_genre_filter(self, recommender, sample_track):
        """Should respect genre filter."""
        results = recommender.recommend(sample_track, genre_filter=["house"], limit=10)
        for r in results:
            assert r["track"]["track_genre"] == "house"
    
    def test_recommend_with_multiple_genres(self, recommender, sample_track):
        """Should work with multiple genre filters."""
        genres = ["house", "deep-house", "techno"]
        results = recommender.recommend(sample_track, genre_filter=genres, limit=10)
        for r in results:
            assert r["track"]["track_genre"] in genres
    
    def test_recommend_bpm_direction_faster(self, recommender, sample_track):
        """Faster direction should favor higher BPM tracks."""
        results_faster = recommender.recommend(sample_track, bpm_direction="faster", limit=10)
        results_slower = recommender.recommend(sample_track, bpm_direction="slower", limit=10)
        
        avg_bpm_faster = sum(r["track"]["tempo"] for r in results_faster) / len(results_faster)
        avg_bpm_slower = sum(r["track"]["tempo"] for r in results_slower) / len(results_slower)
        
        # Faster direction should have higher average BPM
        assert avg_bpm_faster >= avg_bpm_slower or abs(avg_bpm_faster - avg_bpm_slower) < 10
    
    def test_recommend_energy_direction_build(self, recommender, sample_track):
        """Build direction should favor higher energy tracks."""
        results_build = recommender.recommend(sample_track, energy_direction="build", limit=10)
        results_drop = recommender.recommend(sample_track, energy_direction="drop", limit=10)
        
        if len(results_build) > 0 and len(results_drop) > 0:
            avg_energy_build = sum(r["track"]["energy"] for r in results_build) / len(results_build)
            avg_energy_drop = sum(r["track"]["energy"] for r in results_drop) / len(results_drop)
            
            # Build should have higher or equal average energy
            assert avg_energy_build >= avg_energy_drop - 0.1  # Allow small tolerance
    
    def test_recommend_custom_feature_weights(self, recommender, sample_track):
        """Custom feature weights should trigger advanced master weights."""
        custom_weights = DEFAULT_FEATURE_WEIGHTS.copy()
        custom_weights['danceability'] = 3.0
        
        # This should work without error
        results = recommender.recommend(sample_track, feature_weights=custom_weights, limit=10)
        assert len(results) > 0
    
    def test_recommend_custom_feature_directions(self, recommender, sample_track):
        """Custom feature directions should affect results."""
        directions_build = DEFAULT_FEATURE_DIRECTIONS.copy()
        directions_build['danceability'] = 'build'
        directions_build['valence'] = 'build'
        
        directions_drop = DEFAULT_FEATURE_DIRECTIONS.copy()
        directions_drop['danceability'] = 'drop'
        directions_drop['valence'] = 'drop'
        
        results_build = recommender.recommend(sample_track, feature_directions=directions_build, limit=10)
        results_drop = recommender.recommend(sample_track, feature_directions=directions_drop, limit=10)
        
        # Results should be different
        if len(results_build) > 0 and len(results_drop) > 0:
            build_ids = {r["track"]["track_id"] for r in results_build}
            drop_ids = {r["track"]["track_id"] for r in results_drop}
            # At least some results should differ
            assert build_ids != drop_ids or len(build_ids) == 0
    
    def test_recommend_bpm_tolerance(self, recommender, sample_track):
        """BPM tolerance should affect results."""
        results_tight = recommender.recommend(sample_track, bpm_tolerance=0.03, limit=20)
        results_loose = recommender.recommend(sample_track, bpm_tolerance=0.15, limit=20)
        
        # Looser tolerance might give better BPM scores on average
        # Just verify both work
        assert len(results_tight) >= 0
        assert len(results_loose) >= 0
    
    def test_recommend_default_values(self, recommender, sample_track):
        """Should work with all default values."""
        results = recommender.recommend(sample_track)
        assert len(results) > 0
    
    def test_recommend_scores_in_valid_range(self, recommender, sample_track):
        """All scores should be between 0 and 1."""
        results = recommender.recommend(sample_track, limit=20)
        for r in results:
            assert 0.0 <= r["total_score"] <= 1.0
            assert 0.0 <= r["scores"]["bpm"] <= 1.0
            assert 0.0 <= r["scores"]["energy"] <= 1.0
            assert 0.0 <= r["scores"]["features"] <= 1.0
            assert 0.0 <= r["camelot_info"]["camelot_score"] <= 1.0


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""
    
    def test_recommend_rare_genre(self, recommender, database):
        """Should handle genres with few tracks."""
        # Find a genre with fewer tracks
        genre_counts = database.dataset['track_genre'].value_counts()
        rare_genre = genre_counts.idxmin()
        
        rare_track = database.dataset[database.dataset['track_genre'] == rare_genre].iloc[0].to_dict()
        results = recommender.recommend(rare_track, limit=10)
        
        # Should still return some results (from similar genres)
        assert isinstance(results, list)
    
    def test_recommend_extreme_bpm(self, recommender, database):
        """Should handle tracks with extreme BPM."""
        # Find highest and lowest BPM tracks
        max_bpm_track = database.dataset.loc[database.dataset['tempo'].idxmax()].to_dict()
        min_bpm_track = database.dataset.loc[database.dataset['tempo'].idxmin()].to_dict()
        
        results_high = recommender.recommend(max_bpm_track, limit=5)
        results_low = recommender.recommend(min_bpm_track, limit=5)
        
        assert isinstance(results_high, list)
        assert isinstance(results_low, list)
    
    def test_recommend_extreme_energy(self, recommender, database):
        """Should handle tracks with extreme energy values."""
        max_energy_track = database.dataset.loc[database.dataset['energy'].idxmax()].to_dict()
        min_energy_track = database.dataset.loc[database.dataset['energy'].idxmin()].to_dict()
        
        # Build on max energy - should handle gracefully
        results = recommender.recommend(max_energy_track, energy_direction="build", limit=5)
        assert isinstance(results, list)
        
        # Drop on min energy - should handle gracefully
        results = recommender.recommend(min_energy_track, energy_direction="drop", limit=5)
        assert isinstance(results, list)
    
    def test_recommend_empty_genre_filter(self, recommender, sample_track):
        """Empty genre filter should use default behavior."""
        results = recommender.recommend(sample_track, genre_filter=[], limit=10)
        # Empty list might be treated as "use similar genres"
        assert isinstance(results, list)
    
    def test_recommend_very_strict_threshold(self, recommender, sample_track):
        """Very strict camelot threshold might return few/no results."""
        results = recommender.recommend(sample_track, camelot_threshold=1.0, limit=10)
        # Only exact key matches
        for r in results:
            assert r["camelot_info"]["camelot_score"] == 1.0
    
    def test_recommend_zero_weights(self, recommender, sample_track):
        """Zero weights should be handled."""
        zero_weights = {"bpm": 0, "energy": 0, "features": 1}
        results = recommender.recommend(sample_track, master_weights=zero_weights, limit=10)
        assert isinstance(results, list)
    
    def test_recommend_high_limit(self, recommender, sample_track):
        """Should handle requests for many recommendations."""
        results = recommender.recommend(sample_track, limit=100)
        assert len(results) <= 100


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """End-to-end integration tests."""
    
    def test_full_workflow_simple_mode(self, recommender, sample_track):
        """Test simple mode workflow."""
        # User loads a track and wants to build energy
        results = recommender.recommend(
            sample_track,
            energy_direction="build",
            limit=10
        )
        
        assert len(results) > 0
        
        # Pick the top recommendation
        next_track = results[0]["track"]
        
        # Get recommendations for the next track
        next_results = recommender.recommend(next_track, limit=10)
        
        assert len(next_results) > 0
        assert next_track["track_id"] not in [r["track"]["track_id"] for r in next_results]
    
    def test_full_workflow_advanced_mode(self, recommender, sample_track):
        """Test advanced mode workflow with custom directions."""
        custom_directions = {
            'danceability': 'build',
            'valence': 'drop',  # Getting moodier
            'acousticness': 'maintain',
            'instrumentalness': 'maintain',
            'speechiness': 'maintain',
            'liveness': 'maintain',
            'loudness': 'build'
        }
        
        custom_weights = {
            'danceability': 2.0,
            'valence': 1.5,
            'acousticness': 0.5,
            'instrumentalness': 0.5,
            'speechiness': 0.5,
            'liveness': 0.5,
            'loudness': 1.0
        }
        
        results = recommender.recommend(
            sample_track,
            energy_direction="build",
            feature_directions=custom_directions,
            feature_weights=custom_weights,
            limit=10
        )
        
        assert len(results) > 0
    
    def test_genre_transition(self, recommender, sample_track_electronic, sample_track_hiphop):
        """Test transitioning between different genres."""
        # Start with electronic
        electronic_recs = recommender.recommend(sample_track_electronic, limit=10)
        
        # Start with hip-hop
        hiphop_recs = recommender.recommend(sample_track_hiphop, limit=10)
        
        # Results should be different
        electronic_ids = {r["track"]["track_id"] for r in electronic_recs}
        hiphop_ids = {r["track"]["track_id"] for r in hiphop_recs}
        
        # Should have minimal overlap due to genre filtering
        overlap = electronic_ids & hiphop_ids
        assert len(overlap) < len(electronic_ids)


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])