# DJ Assistant

An intelligent DJ assistant that recommends tracks based on harmonic compatibility, 
BPM matching, and energy flow — using real DJ mixing principles.

## Setup

1. Clone the repository:
```bash
   git clone https://github.com/KTB2110/dj-assistant.git
   cd dj-assistant
```

2. Create and activate a virtual environment:
```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
   pip install -r requirements.txt
```

4. Set up environment variables:
```bash
   cp .env.example .env
   # Edit .env with your Spotify API credentials
```

5. Run the app:
```bash
   streamlit run app.py
```

## Project Structure
```
dj-assistant/
├── src/                  # Source code modules
│   ├── config.py         # Configuration and environment variables
│   ├── features.py       # Audio feature extraction
│   ├── key_detection.py  # Musical key detection and Camelot wheel
│   ├── scoring.py        # Compatibility scoring functions
│   ├── recommender.py    # Main DJAssistant class
│   └── spotify.py        # Spotify API integration
├── data/                 # Data files (not in git)
├── notebooks/            # Jupyter notebooks for exploration
├── tests/                # Unit tests
├── app.py                # Streamlit web application
└── requirements.txt      # Python dependencies
```

## Features

- **Harmonic mixing:** Recommends tracks compatible on the Camelot wheel
- **BPM matching:** Filters by tempo compatibility
- **Energy management:** Suggests tracks that build, maintain, or drop energy
- **Explainability:** Tells you *why* each track is recommended

## Getting Spotify API Credentials

1. Go to https://developer.spotify.com/dashboard
2. Create a new application
3. Copy the Client ID and Client Secret to your `.env` file