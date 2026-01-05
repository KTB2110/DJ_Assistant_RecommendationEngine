"""
Scoring functions for evaluating DJ track compatibility
"""

def bpm_compatibility(bpm1: float, bpm2: float, tolerance=0.07, direction: str = "maintain") -> float:
    """
    Check if two BPM values are compatible within a given threshold.
    
    Args:
        bpm1 (float): BPM of the first track.
        bpm2 (float): BPM of the second track.
        tolerance (float): Maximum allowed difference (%) in BPM for compatibility.
        
    Returns:
        float: A compatibility score between 0 and 1.
    """
    if bpm1 == 0.0:
        bpm1 = 1.0  # Avoid division by zero
    

    diff = bpm2 - bpm1  # Positive = candidate is faster
    diff_pct = diff / bpm1  # As percentage
    
    if direction == "maintain":
        # Reward closeness (existing logic)
        abs_diff_pct = abs(diff_pct)
        
        if abs_diff_pct <= tolerance:
            score = 1.0 - (abs_diff_pct / tolerance) * 0.15
        else:
            score = max(0.1, 0.85 - (abs_diff_pct - tolerance) * 2)
        
        # Also check half/double time
        half_diff = abs(bpm2 - bpm1 * 2) / (bpm1 * 2)
        double_diff = abs(bpm2 - bpm1 / 2) / (bpm1 / 2)
        
        if half_diff <= tolerance:
            half_score = 0.9 - (half_diff / tolerance) * 0.15
            score = max(score, half_score)
        if double_diff <= tolerance:
            double_score = 0.9 - (double_diff / tolerance) * 0.15
            score = max(score, double_score)
        
        return score
    
    elif direction == "faster":
        # Reward faster BPMs
        if diff_pct >= 0:
            # Candidate is faster — good
            # +5% = 0.75, +10% = 1.0
            return min(1.0, 0.5 + diff_pct * 5)
        else:
            # Candidate is slower — bad
            # -5% = 0.25, -10% = 0.0
            return max(0.0, 0.5 + diff_pct * 5)
    
    elif direction == "slower":
        # Reward slower BPMs
        if diff_pct <= 0:
            # Candidate is slower — good
            # -5% = 0.75, -10% = 1.0
            return min(1.0, 0.5 - diff_pct * 5)
        else:
            # Candidate is faster — bad
            # +5% = 0.25, +10% = 0.0
            return max(0.0, 0.5 - diff_pct * 5)
    
    else:
        raise ValueError("Direction must be 'faster', 'maintain', or 'slower'")

def feature_compatibility(energy1: float, energy2: float, direction: str = "maintain") -> float:
    """
    Score energy compatibility based on desired flow.
    
    Args:
        energy1: Current track's energy (0-1)
        energy2: Candidate track's energy (0-1)
        direction: "maintain", "build", or "drop"
    
    Returns:
        Score from 0-1
    """
    if energy1 == 0:
        energy1 = 0.01  # Avoid division by zero
    
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

def master_combined_score(
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

def loudness_compatibility(loudness1: float, loudness2: float, direction: str = "maintain") -> float:
    """
    Calculate loudness compatibility between two tracks.
    
    Loudness is in dB (typically -60 to 0, where 0 is loudest).
    """
    diff = loudness2 - loudness1  # Positive = candidate is louder
    
    if direction == "maintain":
        # Within 2dB = good, 6dB = poor
        return max(0, 1 - abs(diff) / 6)
    
    elif direction == "build":
        # Want louder (positive diff)
        if diff >= 0:
            return min(1.0, 0.5 + diff / 12)  # +6dB = 1.0
        else:
            return max(0, 0.5 + diff / 12)    # -6dB = 0.0
    
    elif direction == "drop":
        # Want quieter (negative diff)
        if diff <= 0:
            return min(1.0, 0.5 - diff / 12)  # -6dB = 1.0
        else:
            return max(0, 0.5 - diff / 12)    # +6dB = 0.0
    
    return 0.5

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
    print("0.5 vs 0.5 (maintain):", feature_compatibility(0.5, 0.5, "maintain"))  # ~1.0
    print("0.5 vs 0.7 (maintain):", feature_compatibility(0.5, 0.7, "maintain"))  # ~0.8
    print("0.5 vs 0.7 (build):", feature_compatibility(0.5, 0.7, "build"))        # high
    print("0.5 vs 0.3 (build):", feature_compatibility(0.5, 0.3, "build"))        # low
    print("0.5 vs 0.3 (drop):", feature_compatibility(0.5, 0.3, "drop"))          # high
    print("1.0 vs 0.9 (build):", feature_compatibility(1.0, 0.9, "build"))        # edge case
    print("0.9 vs 1.0 (drop):", feature_compatibility(0.9, 1.0, "drop"))        # edge case

    # Loudness tests
    print("\nLoudness compatibility tests:")
    print("-8 vs -8 (maintain):", loudness_compatibility(-8, -8, "maintain"))    # 1.0 (same)
    print("-8 vs -6 (maintain):", loudness_compatibility(-8, -6, "maintain"))    # ~0.67 (2dB diff)
    print("-8 vs -2 (maintain):", loudness_compatibility(-8, -2, "maintain"))    # 0.0 (6dB diff)
    print("-8 vs -5 (build):", loudness_compatibility(-8, -5, "build"))        # 0.75 (+3dB, good)
    print("-8 vs -2 (build):", loudness_compatibility(-8, -2, "build"))          # 1.0 (+6dB, max)
    print("-8 vs -11 (build):", loudness_compatibility(-8, -11, "build"))        # 0.25 (-3dB, bad)
    print("-8 vs -14 (build):", loudness_compatibility(-8, -14, "build"))        # 0.0 (-6dB, worst)
    print("-8 vs -11 (drop):", loudness_compatibility(-8, -11, "drop"))        # 0.75 (-3dB, good)
    print("-8 vs -14 (drop):", loudness_compatibility(-8, -14, "drop"))          # 1.0 (-6dB, max)
    print("-8 vs -5 (drop):", loudness_compatibility(-8, -5, "drop"))            # 0.25 (+3dB, bad)
    print("-8 vs -2 (drop):", loudness_compatibility(-8, -2, "drop"))            # 0.0 (+6dB, worst)

    # Combined score tests
    print("\nCombined scores:")
    print("All perfect (equal weights):", master_combined_score(1.0, 1.0, 1.0))  # 1.0
    print("All 0.5 (equal weights):", master_combined_score(0.5, 0.5, 0.5))      # 0.5
    print("Mixed (equal):", master_combined_score(1.0, 0.5, 0.75))               # 0.75
    print("Mixed (camelot heavy):", master_combined_score(1.0, 0.5, 0.75, {'camelot': 3, 'bpm': 1, 'energy': 1}))  # higher
    print("Empty weights:", master_combined_score(1.0, 1.0, 1.0, {'camelot': 0, 'bpm': 0, 'energy': 0}))  # 0.0