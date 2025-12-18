import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from src.config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET

sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET
    )
)

# Get a specific track ID
track_id = "7ouMYWpwJ422jRcDASAM3t"  # Strobe by Deadmau5

# Try audio features directly
try:
    features = sp.audio_features([track_id])
    print("Audio features response:")
    print(features)
except Exception as e:
    print(f"Error: {e}")

# Also try the single track endpoint (not batch)
try:
    features = sp.audio_features(track_id)
    print("\nSingle track audio features:")
    print(features)
except Exception as e:
    print(f"Single track error: {e}")