# backend/integration.py
import requests
import json
from typing import Optional, Dict, List
from backend.schemas import PersonData, EmbeddingData, UploadEmbeddingRequest


class BackendAPIClient:
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url.rstrip('/')
        self.upload_endpoint = f"{self.api_base_url}/api/persons/upload-embedding"
    
    def upload_embedding(
        self,
        person_data: Dict,
        embedding_vector: List[float],
        source_image_url: Optional[str] = None,
        preprocessed_image_url: Optional[str] = None,
        detection_method: Optional[str] = None,
        confidence_score: Optional[float] = None
    ) -> Dict:
        payload = UploadEmbeddingRequest(
            person_data=PersonData(**person_data),
            embedding_data=EmbeddingData(
                embedding_vector=embedding_vector,
                source_image_url=source_image_url,
                preprocessed_image_url=preprocessed_image_url,
                detection_method=detection_method,
                confidence_score=confidence_score
            )
        )
        
        try:
            response = requests.post(
                self.upload_endpoint,
                json=payload.model_dump(),
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to upload embedding to backend API: {str(e)}")


def upload_embedding_to_backend(
    person_data: Dict,
    embedding_vector: List[float],
    source_image_url: Optional[str] = None,
    preprocessed_image_url: Optional[str] = None,
    detection_method: Optional[str] = None,
    confidence_score: Optional[float] = None,
    api_base_url: str = "http://localhost:8000"
) -> Dict:
    client = BackendAPIClient(api_base_url=api_base_url)
    return client.upload_embedding(
        person_data=person_data,
        embedding_vector=embedding_vector,
        source_image_url=source_image_url,
        preprocessed_image_url=preprocessed_image_url,
        detection_method=detection_method,
        confidence_score=confidence_score
    )

