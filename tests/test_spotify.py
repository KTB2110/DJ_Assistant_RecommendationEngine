import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from src.config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET

print("Testing Spotify connection...\n")

# Check credentials are loaded
if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
    print("✗ Credentials not found in .env file")
    exit()

print(f"✓ Client ID loaded: {SPOTIFY_CLIENT_ID[:8]}...")

# Try to connect
try:
    sp = spotipy.Spotify(
        auth_manager=SpotifyClientCredentials(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET
        )
    )
    
    # Search for a track to verify it works
    results = sp.search(q="Strobe Deadmau5", type="track", limit=1)
    
    if results["tracks"]["items"]:
        track = results["tracks"]["items"][0]
        print(f"✓ Connected to Spotify API")
        print(f"\nTest search result:")
        print(f"  Track: {track['name']}")
        print(f"  Artist: {track['artists'][0]['name']}")
        print(f"  ID: {track['id']}")
        
        # Get audio features
        features = sp.audio_features([track['id']])[0]
        print(f"\nAudio features:")
        print(f"  BPM: {features['tempo']:.1f}")
        print(f"  Key: {features['key']}")
        print(f"  Mode: {'Major' if features['mode'] == 1 else 'Minor'}")
        print(f"  Energy: {features['energy']:.2f}")
        print(f"  Danceability: {features['danceability']:.2f}")
    else:
        print("✗ Search returned no results")
        
except Exception as e:
    print(f"✗ Connection failed: {e}")

print("\n" + "=" * 50)
print("Spotify setup complete!" if "sp" in dir() else "Fix the errors above.")
print("=" * 50)