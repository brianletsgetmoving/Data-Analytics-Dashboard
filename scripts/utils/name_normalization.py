"""Name normalization and matching utilities."""
from typing import List, Tuple, Optional
import difflib


def calculate_name_similarity(name1: str, name2: str) -> float:
    """
    Calculate similarity between two names using multiple methods.
    
    Args:
        name1: First name to compare
        name2: Second name to compare
        
    Returns:
        float: Similarity score between 0.0 and 1.0
    """
    if not name1 or not name2:
        return 0.0
    
    # Normalize names
    n1 = name1.strip().lower()
    n2 = name2.strip().lower()
    
    # Exact match
    if n1 == n2:
        return 1.0
    
    # Use SequenceMatcher for fuzzy matching
    similarity = difflib.SequenceMatcher(None, n1, n2).ratio()
    
    return similarity


def find_best_match(
    name: str,
    candidate_list: List[Tuple[str, str]],
    threshold: float = 0.75
) -> Optional[Tuple[str, float, str]]:
    """
    Find the best matching name from a candidate list.
    
    Args:
        name: Name to match
        candidate_list: List of tuples (id, name) to search
        threshold: Minimum similarity score (default: 0.75)
        
    Returns:
        Optional[Tuple[str, float, str]]: (matched_id, similarity_score, match_type) or None
        match_type can be: 'exact', 'high', 'medium'
    """
    if not name or not candidate_list:
        return None
    
    best_match = None
    best_score = 0.0
    best_id = None
    
    normalized_name = name.strip().lower()
    
    for candidate_id, candidate_name in candidate_list:
        if not candidate_name:
            continue
            
        normalized_candidate = candidate_name.strip().lower()
        
        # Exact match
        if normalized_name == normalized_candidate:
            return (candidate_id, 1.0, 'exact')
        
        # Calculate similarity
        score = calculate_name_similarity(normalized_name, normalized_candidate)
        
        if score > best_score:
            best_score = score
            best_id = candidate_id
            best_match = candidate_name
    
    # Check if best match meets threshold
    if best_score >= threshold:
        match_type = 'high' if best_score >= 0.9 else 'medium'
        return (best_id, best_score, match_type)
    
    return None

