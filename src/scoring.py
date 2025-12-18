"""
Scoring functions for evaluating DJ track compatibility
"""

def bpm_compatibility(bpm1: float, bpm2: float, tolerance=0.07) -> float:
    """
    Check if two BPM values are compatible within a given threshold.
    
    Args:
        bpm1 (float): BPM of the first track.
        bpm2 (float): BPM of the second track.
        tolerance (float): Maximum allowed difference (%) in BPM for compatibility.
        
    Returns:
        float: A compatibility score between 0 and 1.
    """
    max1 = max(bpm1, bpm2)
    min1 = min(bpm1, bpm2)

    # Checks if either track is near the double or half BPM of the other
    if max1 - (max1 * tolerance) < min1 * 2 < max1 + (max1 * tolerance):
        diff = abs(max1 - (min1 * 2)) / max1  # Percentage difference

        if diff <= tolerance:
            score = 0.9 - (diff / tolerance) * 0.15  # Lower Ceiling than exact match
        else:
            score = max(0.1, 0.8 - (diff - tolerance) * 2)  # Steeper drop outside
        
        return score


    diff = abs(bpm1 - bpm2) / max1  # Percentage difference

    if diff <= tolerance:
        score = 1.0 - (diff / tolerance) * 0.15  # Small penalty within tolerance
    else:
        score = max(0.1, 0.85 - (diff - tolerance) * 2)  # Steeper drop outside
    
    return score

def energy_compatibility(energy1: float, energy2: float, direction: str = "maintain") -> float:
    """
    Score energy compatibility based on desired flow.
    
    Args:
        energy1: Current track's energy (0-1)
        energy2: Candidate track's energy (0-1)
        direction: "maintain", "build", or "drop"
    
    Returns:
        Score from 0-1
    """
    diff = energy2 - energy1

    if direction == "maintain":
        score = 1.0 - abs(diff)
    
    elif direction == "build":
        if diff >= 0:
            if energy1 >= 1.0:
                score = 0.5  # Already at max, can't build
            else:
                score = 0.5 + (diff / (1 - energy1)) * 0.5
        else:
            if energy1 <= 0.0:
                score = 0.1
            else:
                score = max(0.1, 0.3 - (abs(diff) / energy1) * 0.4)
    
    elif direction == "drop":
        if diff <= 0:
            if energy1 <= 0.0:
                score = 0.5  # Already at min, can't drop
            else:
                score = 0.5 + (abs(diff) / energy1) * 0.5
        else:
            if energy1 >= 1.0:
                score = 0.1
            else:
                score = max(0.1, 0.3 - (diff / (1 - energy1)) * 0.4)
    
    else:
        raise ValueError("Direction must be 'maintain', 'build', or 'drop'")
    
    return min(max(score, 0.0), 1.0)

def combined_score(
    camelot_score: float,
    bpm_score: float,
    energy_score: float,
    weights: dict = None
) -> float:
    """
    Combine individual scores into overall compatibility.
    
    Args:
        camelot_score: Harmonic compatibility (0-1)
        bpm_score: BPM compatibility (0-1)
        energy_score: Energy compatibility (0-1)
        weights: Dict with keys 'camelot', 'bpm', 'energy' (default: equal weights)
    
    Returns:
        Weighted average score (0-1)
    """
    if weights is None:
        weights = {'camelot': 1, 'bpm': 1, 'energy': 1}
    
    total_weight = sum(weights.values())
    if total_weight <= 0:
        return 0.0

    weighted_sum = (
        camelot_score * weights.get('camelot', 0) +
        bpm_score * weights.get('bpm', 0) +
        energy_score * weights.get('energy', 0)
    )

    return weighted_sum / total_weight if total_weight > 0 else 0.0


if __name__ == "__main__":
    # BPM tests
    print("BPM compatibility tests:")
    print("128 vs 128:", bpm_compatibility(128, 128))    # ~1.0
    print("128 vs 130:", bpm_compatibility(128, 130))    # ~0.95
    print("128 vs 140:", bpm_compatibility(128, 140))    # lower
    print("70 vs 140:", bpm_compatibility(70, 140))      # half-time, ~0.9
    print("100 vs 140:", bpm_compatibility(100, 140))    # bad match

    # Energy tests
    print("\nEnergy compatibility tests:")
    print("0.5 vs 0.5 (maintain):", energy_compatibility(0.5, 0.5, "maintain"))  # ~1.0
    print("0.5 vs 0.7 (maintain):", energy_compatibility(0.5, 0.7, "maintain"))  # ~0.8
    print("0.5 vs 0.7 (build):", energy_compatibility(0.5, 0.7, "build"))        # high
    print("0.5 vs 0.3 (build):", energy_compatibility(0.5, 0.3, "build"))        # low
    print("0.5 vs 0.3 (drop):", energy_compatibility(0.5, 0.3, "drop"))          # high
    print("1.0 vs 0.9 (build):", energy_compatibility(1.0, 0.9, "build"))        # edge case
    print("0.9 vs 1.0 (drop):", energy_compatibility(0.9, 1.0, "drop"))        # edge case

    # Combined score tests
    print("\nCombined scores:")
    print("All perfect (equal weights):", combined_score(1.0, 1.0, 1.0))  # 1.0
    print("All 0.5 (equal weights):", combined_score(0.5, 0.5, 0.5))      # 0.5
    print("Mixed (equal):", combined_score(1.0, 0.5, 0.75))               # 0.75
    print("Mixed (camelot heavy):", combined_score(1.0, 0.5, 0.75, {'camelot': 3, 'bpm': 1, 'energy': 1}))  # higher
    print("Empty weights:", combined_score(1.0, 1.0, 1.0, {'camelot': 0, 'bpm': 0, 'energy': 0}))  # 0.0