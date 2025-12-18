import os
import requests
import tempfile
import librosa
import numpy as np
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from src.config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET

print("Testing preview download and analysis...\n")

# Connect to Spotify
sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET
    )
)

# Search for a track
results = sp.search(q="Strobe Deadmau5", type="track", limit=1)
track = results["tracks"]["items"][0]

print(f"Track: {track['name']}")
print(f"Artist: {track['artists'][0]['name']}")
print(f"Preview URL: {track['preview_url']}")

if not track['preview_url']:
    print("\n✗ No preview available for this track")
    exit()

# Download preview to a temporary file
print("\nDownloading preview...")
response = requests.get(track['preview_url'])

# Create a temporary file that auto-deletes
with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
    tmp_file.write(response.content)
    tmp_path = tmp_file.name

print(f"✓ Downloaded to temporary file: {tmp_path}")

# Analyze with librosa
print("\nAnalyzing audio...")
try:
    y, sr = librosa.load(tmp_path, sr=22050)
    
    # BPM
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    bpm = float(tempo)
    
    # Energy (RMS)
    rms = librosa.feature.rms(y=y)
    energy = float(np.mean(rms))
    
    # Normalize energy to 0-1 scale (rough approximation)
    energy_normalized = min(1.0, energy * 10)
    
    print(f"\n✓ Analysis complete!")
    print(f"  BPM: {bpm:.1f}")
    print(f"  Energy: {energy_normalized:.2f}")
    print(f"  Duration: {len(y)/sr:.1f} seconds")
    
finally:
    # Clean up - delete the temporary file
    os.unlink(tmp_path)
    print(f"\n✓ Temporary file deleted")

print("\n" + "=" * 50)
print("Preview analysis works!")
print("=" * 50)