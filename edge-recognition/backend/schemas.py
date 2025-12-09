# backend/schemas.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


class PersonData(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    age: Optional[int] = Field(None, ge=0, le=150)
    gender: Optional[str] = Field(None)
    notes: Optional[str] = Field(None)

    @validator('gender')
    def validate_gender(cls, v):
        if v is not None and v not in ['M', 'F', 'Other']:
            raise ValueError("Gender must be 'M', 'F', or 'Other'")
        return v


class EmbeddingData(BaseModel):
    embedding_vector: List[float] = Field(...)
    source_image_url: Optional[str] = Field(None, max_length=500)
    preprocessed_image_url: Optional[str] = Field(None, max_length=500)
    detection_method: Optional[str] = Field(None)
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)

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
    person_data: PersonData
    embedding_data: EmbeddingData


class UploadEmbeddingResponse(BaseModel):
    success: bool
    embedding_id: int
    person_id: int
    message: str
    data: dict


class PersonResponse(BaseModel):
    person_id: int
    name: str
    age: Optional[int]
    gender: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime


class EmbeddingResponse(BaseModel):
    embedding_id: int
    person_id: int
    source_image_url: Optional[str]
    preprocessed_image_url: Optional[str]
    detection_method: Optional[str]
    confidence_score: Optional[float]
    created_at: datetime


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    code: str

