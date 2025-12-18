"""
Camelot Wheel implementation for harmonic mixing.

The Camelot Wheel maps musical keys to a notation system (1A-12A, 1B-12B)
that makes it easy to find compatible keys for DJ mixing.
"""

SPOTIFY_TO_CAMELOT = {
    # Minor keys (mode = 0)
    (0, 0): "5A",   # C minor
    (1, 0): "12A",  # C# minor
    (2, 0): "7A",   # D minor
    (3, 0): "2A",   # D# minor
    (4, 0): "9A",   # E minor
    (5, 0): "4A",   # F minor
    (6, 0): "11A",  # F# minor
    (7, 0): "6A",   # G minor
    (8, 0): "1A",   # G# minor
    (9, 0): "8A",   # A minor
    (10, 0): "3A",  # A# minor
    (11, 0): "10A", # B minor
    
    # Major keys (mode = 1)
    (0, 1): "8B",   # C major
    (1, 1): "3B",   # C# major
    (2, 1): "10B",  # D major
    (3, 1): "5B",   # D# major
    (4, 1): "12B",  # E major
    (5, 1): "7B",   # F major
    (6, 1): "2B",   # F# major
    (7, 1): "9B",   # G major
    (8, 1): "4B",   # G# major
    (9, 1): "11B",  # A major
    (10, 1): "6B",  # A# major
    (11, 1): "1B",  # B major
}

def spotify_to_camelot(key: int, mode: int) -> str:
    """
    Convert Spotify key and mode to Camelot notation.
    """
    return SPOTIFY_TO_CAMELOT.get((key, mode), "Unknown")

def camelot_similarity(camelot1: str, camelot2: str) -> float:
    """
    Calculate the similarity between two Camelot keys.
    
    Similarity is defined as the number of steps apart on the Camelot Wheel.
    Adjacent keys have a similarity of 1, same keys have a similarity of 0.
    """

    if camelot1 == "Unknown" or camelot2 == "Unknown":
        return 0.5

    if camelot1 == camelot2:
        return 1
    
    num1, letter1 = int(camelot1[:-1]), camelot1[-1]
    num2, letter2 = int(camelot2[:-1]), camelot2[-1]

    # Calculating circular distance
    diff = min(abs(num1 - num2), 12 - abs(num1 - num2))

    # Checking if same mode (A or B)
    if diff == 0 and letter1 != letter2:
        return 0.95  # Same number, different mode (Relative key)
    elif diff == 1 and letter1 == letter2:
        return 0.85   # Adjacent keys in same mode
    elif diff == 1 and letter1 != letter2:
        return 0.75  # Adjacent keys in different modes
    elif diff == 2:
        return 0.5   # Two steps apart
    elif diff > 2 and diff <= 4:
        return 0.25  # Moderately compatible
    else:
        return 0.1  # Not compatible

if __name__ == "__main__":
    # Test conversions
    print("C major ->", spotify_to_camelot(0, 1))  # Should be 8B
    print("A minor ->", spotify_to_camelot(9, 0))  # Should be 8A
    
    # Test similarity
    print("\n8A vs 8A:", camelot_similarity("8A", "8A"))   # 1.0
    print("8A vs 8B:", camelot_similarity("8A", "8B"))     # 0.95
    print("8A vs 9A:", camelot_similarity("8A", "9A"))     # 0.85
    print("8A vs 2A:", camelot_similarity("8A", "2A"))     # 0.1