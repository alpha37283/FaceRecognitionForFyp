# backend/schemas.py
"""
Pydantic schemas for API request/response validation
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


class PersonData(BaseModel):
    """Person information schema"""
    name: str = Field(..., min_length=1, max_length=255, description="Person's full name")
    age: Optional[int] = Field(None, ge=0, le=150, description="Person's age")
    gender: Optional[str] = Field(None, description="Gender: 'M', 'F', or 'Other'")
    notes: Optional[str] = Field(None, description="Additional notes or description")

    @validator('gender')
    def validate_gender(cls, v):
        if v is not None and v not in ['M', 'F', 'Other']:
            raise ValueError("Gender must be 'M', 'F', or 'Other'")
        return v


class EmbeddingData(BaseModel):
    """Embedding data schema"""
    embedding_vector: List[float] = Field(..., description="512-dimensional embedding vector")
    source_image_url: Optional[str] = Field(None, max_length=500, description="URL/path to source image")
    preprocessed_image_url: Optional[str] = Field(None, max_length=500, description="URL/path to preprocessed 112x112 image")
    detection_method: Optional[str] = Field(None, description="Detection method: 'mtcnn' or 'retinaface'")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Detection confidence score")

    @validator('embedding_vector')
    def validate_embedding_dimension(cls, v):
        if len(v) != 512:
            raise ValueError(f"Embedding vector must have 512 dimensions, got {len(v)}")
        return v

    @validator('detection_method')
    def validate_detection_method(cls, v):
        if v is not None and v not in ['mtcnn', 'retinaface']:
            raise ValueError("Detection method must be 'mtcnn' or 'retinaface'")
        return v


class UploadEmbeddingRequest(BaseModel):
    """Request schema for uploading embedding"""
    person_data: PersonData
    embedding_data: EmbeddingData


class UploadEmbeddingResponse(BaseModel):
    """Response schema for uploading embedding"""
    success: bool
    embedding_id: int
    person_id: int
    message: str
    data: dict


class PersonResponse(BaseModel):
    """Person information response"""
    person_id: int
    name: str
    age: Optional[int]
    gender: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime


class EmbeddingResponse(BaseModel):
    """Embedding information response (without vector)"""
    embedding_id: int
    person_id: int
    source_image_url: Optional[str]
    preprocessed_image_url: Optional[str]
    detection_method: Optional[str]
    confidence_score: Optional[float]
    created_at: datetime


class ErrorResponse(BaseModel):
    """Error response schema"""
    success: bool = False
    error: str
    code: str

