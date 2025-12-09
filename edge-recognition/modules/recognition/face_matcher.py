# modules/recognition/face_matcher.py
"""
Face matching module using cosine similarity.
Compares live camera face embeddings with synced embeddings from database.
"""
import numpy as np
from typing import Dict, Optional, Tuple, List


def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Calculate cosine similarity between two vectors.
    
    Args:
        vec1: First embedding vector (512-dim)
        vec2: Second embedding vector (512-dim)
    
    Returns:
        Similarity score between -1 and 1 (typically 0 to 1 for normalized embeddings)
    """
    # Normalize vectors
    vec1_norm = vec1 / (np.linalg.norm(vec1) + 1e-8)
    vec2_norm = vec2 / (np.linalg.norm(vec2) + 1e-8)
    
    # Calculate cosine similarity
    similarity = np.dot(vec1_norm, vec2_norm)
    return float(similarity)


def find_best_match(
    live_embedding: np.ndarray,
    synced_embeddings: Dict[int, Dict],
    similarity_threshold: float = 0.6
) -> Optional[Tuple[int, Dict, float]]:
    """
    Find best matching person from synced embeddings.
    
    Args:
        live_embedding: Embedding vector from live camera face (512-dim)
        synced_embeddings: Dict of synced embeddings {embedding_id: {metadata, embedding_vector}}
        similarity_threshold: Minimum similarity score to consider a match (default: 0.6)
    
    Returns:
        Tuple of (embedding_id, person_metadata, similarity_score) if match found, else None
    """
    if not synced_embeddings:
        return None
    
    best_match = None
    best_similarity = -1.0
    
    # Compare with all available embeddings
    for emb_id, emb_data in synced_embeddings.items():
        synced_vector = emb_data.get('embedding_vector')
        
        if synced_vector is None:
            continue
        
        # Ensure both are numpy arrays
        if not isinstance(live_embedding, np.ndarray):
            live_embedding = np.array(live_embedding)
        if not isinstance(synced_vector, np.ndarray):
            synced_vector = np.array(synced_vector)
        
        # Calculate similarity
        similarity = cosine_similarity(live_embedding, synced_vector)
        
        # Track best match
        if similarity > best_similarity:
            best_similarity = similarity
            best_match = (emb_id, emb_data, similarity)
    
    # Return match if above threshold
    if best_match and best_similarity >= similarity_threshold:
        return best_match
    
    return None


class FaceMatcher:
    """
    Face matching service for live camera feed.
    Compares live face embeddings with synced embeddings.
    """
    
    def __init__(self, similarity_threshold: float = 0.6):
        """
        Initialize face matcher.
        
        Args:
            similarity_threshold: Minimum cosine similarity for a match (default: 0.6)
        """
        self.similarity_threshold = similarity_threshold
        self.synced_embeddings = {}
    
    def load_synced_embeddings(self, synced_embeddings: Dict):
        """
        Load synced embeddings for comparison.
        
        Args:
            synced_embeddings: Dict from EmbeddingSyncClient.get_local_embeddings()
        """
        self.synced_embeddings = synced_embeddings
    
    def match_face(self, live_embedding: np.ndarray) -> Optional[Dict]:
        """
        Match live face embedding with synced embeddings.
        
        Args:
            live_embedding: Embedding vector from live camera (512-dim)
        
        Returns:
            Dict with match info if found:
            {
                'person_name': str,
                'person_age': int or None,
                'person_gender': str or None,
                'person_id': int,
                'embedding_id': int,
                'similarity': float
            }
            None if no match found
        """
        match = find_best_match(
            live_embedding,
            self.synced_embeddings,
            self.similarity_threshold
        )
        
        if match:
            emb_id, emb_data, similarity = match
            return {
                'person_name': emb_data.get('person_name', 'Unknown'),
                'person_age': emb_data.get('person_age'),
                'person_gender': emb_data.get('person_gender'),
                'person_id': emb_data.get('person_id'),
                'embedding_id': emb_id,
                'similarity': similarity
            }
        
        return None

