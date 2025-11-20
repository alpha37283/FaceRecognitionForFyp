# modules/recognition/upload_to_backend.py
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
    if api_base_url is None:
        api_base_url = os.getenv("BACKEND_API_URL", "http://localhost:8000")
    
    person_data = {
        "name": person_name,
        "age": age,
        "gender": gender,
        "notes": notes
    }
    
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

