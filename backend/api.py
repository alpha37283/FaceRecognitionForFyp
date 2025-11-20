# backend/api.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from backend.database import get_db, init_db
from backend.schemas import (
    UploadEmbeddingRequest,
    UploadEmbeddingResponse,
    PersonResponse,
    EmbeddingResponse,
    ErrorResponse
)
from backend.services import (
    create_or_get_person,
    store_embedding,
    get_embedding_vector,
    get_person_embeddings,
    get_person_by_id
)
from backend.models import Person, FaceEmbedding

app = FastAPI(
    title="Face Embedding Storage API",
    description="API for storing face embeddings and person information",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    init_db()
    print("[INFO] Database initialized")


@app.get("/")
async def root():
    return {
        "message": "Face Embedding Storage API",
        "version": "1.0.0",
        "status": "running"
    }


@app.post("/api/persons/upload-embedding", response_model=UploadEmbeddingResponse)
async def upload_embedding(request: UploadEmbeddingRequest, db: Session = Depends(get_db)):
    try:
        # Create or get person
        person = create_or_get_person(db, request.person_data)
        
        # Store embedding
        embedding = store_embedding(db, person.person_id, request.embedding_data)
        
        return UploadEmbeddingResponse(
            success=True,
            embedding_id=embedding.embedding_id,
            person_id=person.person_id,
            message="Embedding stored successfully",
            data={
                "embedding_id": embedding.embedding_id,
                "person_id": person.person_id,
                "name": person.name,
                "created_at": embedding.created_at.isoformat()
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@app.get("/api/persons/{person_id}", response_model=PersonResponse)
async def get_person(person_id: int, db: Session = Depends(get_db)):
    person = get_person_by_id(db, person_id)
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found"
        )
    return person


@app.get("/api/persons/{person_id}/embeddings", response_model=list[EmbeddingResponse])
async def get_person_embeddings_endpoint(person_id: int, db: Session = Depends(get_db)):
    person = get_person_by_id(db, person_id)
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found"
        )
    
    embeddings = get_person_embeddings(db, person_id)
    return embeddings


@app.get("/api/embeddings/{embedding_id}/vector")
async def get_embedding_vector_endpoint(embedding_id: int, db: Session = Depends(get_db)):
    embedding = db.query(FaceEmbedding).filter(FaceEmbedding.embedding_id == embedding_id).first()
    if not embedding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Embedding not found"
        )
    
    person = get_person_by_id(db, embedding.person_id)
    vector = get_embedding_vector(db, embedding_id)
    
    return {
        "success": True,
        "embedding_id": embedding_id,
        "person_id": embedding.person_id,
        "name": person.name if person else "Unknown",
        "vector": vector
    }

