# backend/services.py
import json
from sqlalchemy.orm import Session
from sqlalchemy import and_
from backend.models import Person, FaceEmbedding, EmbeddingSyncLog, SyncAction
from backend.schemas import PersonData, EmbeddingData
from typing import Optional, List, Dict


def create_or_get_person(db: Session, person_data: PersonData) -> Person:
    existing_person = db.query(Person).filter(Person.name == person_data.name).first()
    
    if existing_person:
        if person_data.age is not None:
            existing_person.age = person_data.age
        if person_data.gender is not None:
            existing_person.gender = person_data.gender
        if person_data.notes is not None:
            existing_person.notes = person_data.notes
        db.commit()
        db.refresh(existing_person)
        return existing_person
    
    new_person = Person(
        name=person_data.name,
        age=person_data.age,
        gender=person_data.gender,
        notes=person_data.notes
    )
    db.add(new_person)
    db.commit()
    db.refresh(new_person)
    return new_person


def store_embedding(db: Session, person_id: int, embedding_data: EmbeddingData) -> FaceEmbedding:
    embedding_vector_json = json.dumps(embedding_data.embedding_vector)
    
    new_embedding = FaceEmbedding(
        person_id=person_id,
        embedding_vector=embedding_vector_json,
        source_image_url=embedding_data.source_image_url,
        preprocessed_image_url=embedding_data.preprocessed_image_url,
        detection_method=embedding_data.detection_method,
        confidence_score=embedding_data.confidence_score
    )
    
    db.add(new_embedding)
    db.commit()
    db.refresh(new_embedding)
    
    sync_log = EmbeddingSyncLog(
        embedding_id=new_embedding.embedding_id,
        person_id=person_id,
        action=SyncAction.INSERT,
        synced="false"
    )
    db.add(sync_log)
    db.commit()
    
    return new_embedding


def get_embedding_vector(db: Session, embedding_id: int) -> Optional[List[float]]:
    embedding = db.query(FaceEmbedding).filter(FaceEmbedding.embedding_id == embedding_id).first()
    if embedding:
        return json.loads(embedding.embedding_vector)
    return None


def get_person_embeddings(db: Session, person_id: int) -> List[FaceEmbedding]:
    return db.query(FaceEmbedding).filter(FaceEmbedding.person_id == person_id).all()


def get_person_by_id(db: Session, person_id: int) -> Optional[Person]:
    return db.query(Person).filter(Person.person_id == person_id).first()

