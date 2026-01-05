<div align="center">

# 🎧 DJ Assistant

**An intelligent DJ assistant that recommends tracks based on harmonic compatibility, BPM matching, and energy flow — using real DJ mixing principles.**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.125-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)](https://react.dev)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-4.0-06B6D4?logo=tailwindcss&logoColor=white)](https://tailwindcss.com)

</div>

---

## ✨ Features

### 🎹 Harmonic Mixing (Camelot Wheel)
- Automatically maps Spotify key/mode data to the **Camelot Wheel** notation (1A-12A, 1B-12B)
- Recommends tracks that are harmonically compatible for smooth transitions
- Supports same key, relative key, and adjacent key matching with configurable thresholds

### 🎚️ BPM Compatibility
- Intelligent tempo matching with configurable tolerance (default ±7%)
- **Half-time/double-time detection** — seamlessly mix 70 BPM with 140 BPM tracks
- Direction controls: `faster`, `maintain`, or `slower` for building or dropping energy

### ⚡ Energy Flow Management
- Control the energy trajectory of your set with `build`, `maintain`, or `drop` modes
- Separate control for energy levels independent of other audio features
- Smart scoring that accounts for edge cases (can't build when already at max)

### 🎛️ Advanced Audio Feature Controls
Fine-tune recommendations using Spotify's audio analysis features:

| Feature | Description |
|---------|-------------|
| **Danceability** | How suitable for dancing (rhythm, tempo, beat strength) |
| **Valence** | Musical positiveness (happy vs sad) |
| **Acousticness** | Likelihood of being acoustic |
| **Instrumentalness** | Predicts if track has no vocals |
| **Speechiness** | Presence of spoken words |
| **Liveness** | Presence of live audience |
| **Loudness** | Overall loudness in dB |

Each feature supports directional control: `build`, `maintain`, or `drop`.

### 🎸 Genre Intelligence
- **Genre similarity engine** using audio feature centroids
- Automatically suggests similar genres based on your current track
- Explainable results: *"Similar energy (0.78 vs 0.81) and tempo (128 vs 126 BPM)"*
- Filter recommendations by specific genres

### 🎚️ Dual Deck System
- **Deck A & Deck B** for professional DJ-style workflow
- Build separate playlists for each deck
- Toggle recommendation source between decks
- Preview tracks before committing to your set

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Frontend (React + Vite)                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   Deck A    │  │   Deck B    │  │    Recommendations      │  │
│  │  (Preview)  │  │  (Preview)  │  │  (Scored & Filtered)    │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FastAPI Backend (api.py)                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   /search   │  │  /recommend │  │  /genres/{genre}/similar│  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Core Engine (src/)                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │  Camelot    │  │   Scoring   │  │    Genre Similarity     │  │
│  │   Wheel     │  │   Engine    │  │    (Euclidean dist)     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
│  ┌─────────────┐  ┌─────────────────────────────────────────┐   │
│  │ Recommender │  │        TrackDatabase (HuggingFace)      │   │
│  │   Engine    │  │        114k+ Spotify Tracks             │   │
│  └─────────────┘  └─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+ (for frontend)

### 1. Clone & Setup Backend

```bash
git clone https://github.com/KTB2110/dj-assistant.git
cd dj-assistant

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (for Spotify API features)
cp .env.example .env
# Edit .env with your Spotify API credentials
```

### 2. Start the API Server

```bash
uvicorn api:app --reload
```

The API will be available at `http://127.0.0.1:8000`

### 3. Setup & Run Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173`

---

## 📡 API Reference

### Search Tracks
```http
GET /search?query=daft+punk&limit=10
```

### Get Track by ID
```http
GET /track/{track_id}
```

### Get Recommendations
```http
POST /recommend
Content-Type: application/json

{
  "track": { ... },           // Current track object
  "bpm_direction": "maintain", // "faster" | "maintain" | "slower"
  "energy_direction": "build", // "build" | "maintain" | "drop"
  "feature_directions": {      // Optional advanced controls
    "danceability": "maintain",
    "valence": "build",
    "loudness": "drop"
  },
  "limit": 10,
  "genre_filter": ["house", "tech-house"],
  "camelot_threshold": 0.7
}
```

### Get All Genres
```http
GET /genres
```

### Get Similar Genres
```http
GET /genres/{genre}/similar?top_k=10
```

---

## 📁 Project Structure

```
dj-assistant/
├── api.py                    # FastAPI backend server
├── app.py                    # Streamlit app (alternative UI)
├── requirements.txt          # Python dependencies
│
├── src/                      # Core Python modules
│   ├── camelot.py            # Camelot wheel & harmonic mixing
│   ├── scoring.py            # BPM, energy, loudness compatibility
│   ├── recommender.py        # Main DJRecommender engine
│   ├── database.py           # Track database (HuggingFace dataset)
│   ├── genres.py             # Genre similarity engine
│   └── config.py             # Configuration & environment
│
├── frontend/                 # React + Vite frontend
│   ├── src/
│   │   ├── App.jsx           # Main dual-deck interface
│   │   └── ...
│   ├── package.json
│   └── vite.config.js
│
├── notebooks/                # Jupyter notebooks for exploration
│   ├── genre_analysis.ipynb  # Genre similarity development
│   └── spotipy_analysis.ipynb
│
├── data/                     # Data files
│   ├── raw/
│   ├── processed/
│   └── cache/
│
└── tests/                    # Unit tests
    ├── test_recommender.py
    ├── test_dataset.py
    └── ...
```

---

## 🧮 Scoring Algorithm

The recommendation engine uses a weighted scoring system:

### Default Weights
| Component | Weight | Description |
|-----------|--------|-------------|
| BPM | 35% | Tempo compatibility |
| Energy | 35% | Energy level match |
| Features | 30% | Audio feature similarity |

### Advanced Mode Weights
When custom feature weights are applied:
| Component | Weight |
|-----------|--------|
| BPM | 27.5% |
| Energy | 27.5% |
| Features | 45% |

### Camelot Similarity Scores
| Relationship | Score |
|--------------|-------|
| Same key | 1.0 |
| Relative key (same number, A↔B) | 0.95 |
| Adjacent key (±1, same mode) | 0.85 |
| Adjacent key (±1, different mode) | 0.75 |
| 2 steps apart | 0.5 |
| 3-4 steps apart | 0.25 |
| 5+ steps apart | 0.1 |

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
```

### Customizing Weights

You can customize the scoring weights when calling the recommender:

```python
from src.recommender import DJRecommender

recommender.recommend(
    current_track=track,
    master_weights={
        'bpm': 0.4,
        'energy': 0.4,
        'features': 0.2
    },
    feature_weights={
        'danceability': 1.5,  # Prioritize danceability
        'valence': 0.5,       # De-prioritize mood
    }
)
```

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

---

## 🛣️ Roadmap

- [ ] Spotify OAuth integration for library access
- [ ] Audio preview playback
- [ ] Setlist export (M3U, CSV)
- [ ] BPM/key analysis for local files
- [ ] Transition suggestions between tracks
- [ ] Machine learning personalization

---

## 📄 License

MIT License — feel free to use this for your own DJ projects!

---

## 🙏 Acknowledgments

- Dataset: [Spotify Tracks Dataset](https://huggingface.co/datasets/maharshipandya/spotify-tracks-dataset) by Maharshi Pandya
- Camelot Wheel concept by Mark Davis

---

<div align="center">

**Built with ❤️ for DJs who love data**

</div>