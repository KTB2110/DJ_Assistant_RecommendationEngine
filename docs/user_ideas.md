```markdown
<!-- filepath: docs/user_ideas.md -->
# User Ideas Log

A running list of feature ideas and UI concepts for the DJ Assistant project.

---

## Idea #1: Genre Suggestion Button
**Date:** December 18, 2025

**Description:** 
- UI button: "Suggest genres to mix into"
- Shows 10 closest genres based on distance matrix
- Display the distance metric alongside each genre (transparency for the user)

**Notes:**
- Some unexpected matches might actually work well for creative mixing
- Distance metric helps user understand *why* a genre was suggested

---

## Idea #2: Advanced Mode Feature Dials
**Date:** December 18, 2025

**Description:**
- Toggle between Simple Mode (master dial) and Advanced Mode (per-feature dials)
- Simple Mode: One dial controls energy (Build/Maintain/Drop)
- Advanced Mode: Individual dials for each audio feature
- Features: energy, danceability, valence, tempo, loudness, acousticness, instrumentalness, speechiness, liveness

**Notes:**
- Need to decide default behavior for untouched features in Advanced Mode
- Need scoring logic to combine multiple feature directions

## Idea #3: Dynamic Genre Selection
**Date:** December 18, 2025

**Description:**
- User can manually select genres for recommendations
- Genre options are sorted by similarity (closest first)
- User can pick any genre, not just similar ones

**Notes:**
- GenreSimilarity is always loaded in backend
- UI shows suggested genres at top, but full list available

## Idea #4: Setlist Energy Curve Visualization
**Date:** December 19, 2025

**Description:**
- UI Component: A dynamic line chart at the bottom of the Setlist Sidebar.
- X-axis: Track order (1, 2, 3...).
- Y-axis: Feature value (Energy, Valence, or Danceability).
- Real-time updates: As a user adds a recommendation to the setlist, the graph plots a new point.

**Notes:**
- Allows DJs to see the "shape" of their set (e.g., a "Mountain" shape where energy peaks in the middle, or a "Steady Build").
- Visualizes "vibe shifts"—a sharp drop in the line indicates a potential "mood breaker" that the DJ might want to reconsider.
- Could color-code the line segments based on harmonic compatibility (Green = smooth transition, Red = potential clash).


## Idea #5: Transition "Red-Zone" Warning
**Date:** December 19, 2025

**Description:**
- UI Logic: Compare the currently loaded Deck A and the selected Deck B recommendation.
- Visual: A "Transition Safety" meter between the two decks.
- Indicator:
    - **Green:** Harmonic match (Camelot) + < 3% BPM difference.
    - **Yellow:** Non-harmonic match but compatible + 3-6% BPM difference.
    - **Red:** Key clash (e.g., 1A to 6B) or > 8% BPM difference (requires heavy "pitching").

**Notes:**
- This adds "Domain Logic" to the UI.
- Shows recruiters you didn't just build a database; you built a tool that understands the *rules* of DJing.
```