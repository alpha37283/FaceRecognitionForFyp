# modules/recognition/upload_to_backend.py
"""
Helper module to upload embeddings to backend API
This connects the processing service to the backend storage API
"""
import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.append(project_root)

from backend.integration import upload_embedding_to_backend
from typing import Optional, Dict, List


def upload_embedding(
    person_name: str,
    embedding_vector: List[float],
    age: Optional[int] = None,
    gender: Optional[str] = None,
    notes: Optional[str] = None,
    source_image_url: Optional[str] = None,
    preprocessed_image_url: Optional[str] = None,
    detection_method: Optional[str] = None,
    confidence_score: Optional[float] = None,
    api_base_url: Optional[str] = None
) -> Dict:
    """
    Upload embedding to backend API after generation
    
    This function should be called after generating embeddings using
    the existing embedding generation system.
    
    Args:
        person_name: Person's name (required)
        embedding_vector: 512-dimensional embedding vector (required)
        age: Person's age (optional)
        gender: Person's gender - 'M', 'F', or 'Other' (optional)
        notes: Additional notes (optional)
        source_image_url: Path/URL to original image (optional)
        preprocessed_image_url: Path/URL to preprocessed 112x112 image (optional)
        detection_method: 'mtcnn' or 'retinaface' (optional)
        confidence_score: Detection confidence 0-1 (optional)
        api_base_url: Backend API URL (default: http://localhost:8000)
        
    Returns:
        Dictionary with response from backend API
        
    Example:
        # After generating embedding
        embedding, preprocessed_img, landmarks = generator.generate_embedding(face_image)
        
        # Upload to backend
        result = upload_embedding(
            person_name="John Doe",
            embedding_vector=embedding.tolist(),
            age=35,
            gender="M",
            notes="Security guard",
            source_image_url="data/cropped_faces/face1.jpg",
            preprocessed_image_url="data/embeddings/preprocessed/face1_112x112.jpg",
            detection_method="mtcnn"
        )
    """
    if api_base_url is None:
        api_base_url = os.getenv("BACKEND_API_URL", "http://localhost:8000")
    
    # Prepare person data
    person_data = {
        "name": person_name,
        "age": age,
        "gender": gender,
        "notes": notes
    }
    
    # Upload to backend
    try:
        result = upload_embedding_to_backend(
            person_data=person_data,
            embedding_vector=embedding_vector,
            source_image_url=source_image_url,
            preprocessed_image_url=preprocessed_image_url,
            detection_method=detection_method,
            confidence_score=confidence_score,
            api_base_url=api_base_url
        )
        return result
    except Exception as e:
        print(f"[-] Error uploading to backend: {str(e)}")
        raise

