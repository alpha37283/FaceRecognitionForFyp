# backend/integration.py
"""
Integration module that connects processing service to backend API
This module bridges the gap between existing processing code and new backend API
"""
import requests
import json
from typing import Optional, Dict, List
from backend.schemas import PersonData, EmbeddingData, UploadEmbeddingRequest


class BackendAPIClient:
    """Client for communicating with backend API"""
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        """
        Initialize backend API client
        
        Args:
            api_base_url: Base URL of the backend API server
        """
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
        """
        Upload embedding to backend API
        
        Args:
            person_data: Dictionary with person info (name, age, gender, notes)
            embedding_vector: 512-dimensional embedding vector
            source_image_url: URL/path to source image
            preprocessed_image_url: URL/path to preprocessed image
            detection_method: 'mtcnn' or 'retinaface'
            confidence_score: Detection confidence (0-1)
            
        Returns:
            Response dictionary with embedding_id and person_id
        """
        # Prepare request payload
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
        
        # Send request
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
    """
    Convenience function to upload embedding to backend
    
    This function can be called from the processing service after
    generating embeddings.
    
    Args:
        person_data: Dictionary with person info
        embedding_vector: 512-dimensional embedding vector
        source_image_url: URL/path to source image
        preprocessed_image_url: URL/path to preprocessed image
        detection_method: 'mtcnn' or 'retinaface'
        confidence_score: Detection confidence
        api_base_url: Backend API base URL
        
    Returns:
        Response dictionary
    """
    client = BackendAPIClient(api_base_url=api_base_url)
    return client.upload_embedding(
        person_data=person_data,
        embedding_vector=embedding_vector,
        source_image_url=source_image_url,
        preprocessed_image_url=preprocessed_image_url,
        detection_method=detection_method,
        confidence_score=confidence_score
    )

