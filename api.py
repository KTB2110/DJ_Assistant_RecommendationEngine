"""
FastAPI backend for DJ Assistant.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from src.database import TrackDatabase
from src.genres import GenreSimilarity
from src.recommender import DJRecommender

# Global instances
db = None
genre_engine = None
recommender = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load database and models on startup."""
    global db, genre_engine, recommender
    
    print("Loading database...")
    db = TrackDatabase()
    db.load()
    
    print("Fitting genre engine...")
    genre_engine = GenreSimilarity()
    genre_engine.fit(db.dataset)
    
    print("Initializing recommender...")
    recommender = DJRecommender(db, genre_engine)
    
    print("API ready!")
    
    yield
    
    print("Shutting down...")


app = FastAPI(title="DJ Assistant API", lifespan=lifespan)

# CORS - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RecommendRequest(BaseModel):
    track: dict
    bpm_direction: str = "maintain"
    energy_direction: str = "maintain"
    feature_directions: Optional[dict] = None
    feature_weights: Optional[dict] = None
    limit: int = 10
    genre_filter: Optional[list] = None
    camelot_threshold: float = 0.7


@app.get("/")
def root():
    return {"status": "DJ Assistant API running"}


@app.get("/search")
def search_tracks(query: str, limit: int = 10):
    """Search for tracks by name or artist."""
    if not query:
        return []
    return db.search(query, limit=limit)


@app.get("/track/{track_id}")
def get_track(track_id: str):
    """Get a single track by ID."""
    track = db.get_track(track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    return track


@app.post("/recommend")
def get_recommendations(request: RecommendRequest):
    """Get track recommendations based on current track."""
    return recommender.recommend(
        current_track=request.track,
        bpm_direction=request.bpm_direction,
        energy_direction=request.energy_direction,
        feature_directions=request.feature_directions,
        feature_weights=request.feature_weights,
        limit=request.limit,
        genre_filter=request.genre_filter,
        camelot_threshold=request.camelot_threshold
    )


@app.get("/genres")
def get_genres():
    """Get all available genres."""
    return sorted(db.dataset['track_genre'].unique().tolist())


@app.get("/genres/{genre}/similar")
def get_similar_genres(genre: str, top_k: int = 10):
    """Get similar genres."""
    try:
        return genre_engine.get_similar_genres(genre, top_k=top_k)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))