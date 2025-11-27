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


def get_unsynced_embeddings(db: Session) -> List[Dict]:
    """
    Get all unsynced embeddings with person metadata.
    Returns embeddings that have not been synced to live feed devices.
    
    Returns:
        List of dicts containing:
        - embedding_id
        - person_id
        - person_name
        - person_age
        - person_gender
        - person_notes
        - embedding_vector (512-dim list)
        - action (INSERT/UPDATE/DELETE)
        - timestamp
        - sync_id
    """
    # Query unsynced entries from sync log
    unsynced_logs = db.query(EmbeddingSyncLog).filter(
        EmbeddingSyncLog.synced == "false"
    ).order_by(EmbeddingSyncLog.timestamp.asc()).all()
    
    results = []
    for sync_log in unsynced_logs:
        # Get embedding
        embedding = db.query(FaceEmbedding).filter(
            FaceEmbedding.embedding_id == sync_log.embedding_id
        ).first()
        
        if not embedding:
            continue
        
        # Get person info
        person = get_person_by_id(db, sync_log.person_id)
        if not person:
            continue
        
        # Parse embedding vector
        embedding_vector = json.loads(embedding.embedding_vector)
        
        result = {
            "sync_id": sync_log.sync_id,
            "embedding_id": embedding.embedding_id,
            "person_id": person.person_id,
            "person_name": person.name,
            "person_age": person.age,
            "person_gender": person.gender,
            "person_notes": person.notes,
            "embedding_vector": embedding_vector,
            "action": sync_log.action.value if hasattr(sync_log.action, 'value') else str(sync_log.action),
            "timestamp": sync_log.timestamp.isoformat() if sync_log.timestamp else None,
            "source_image_url": embedding.source_image_url,
            "preprocessed_image_url": embedding.preprocessed_image_url,
            "detection_method": embedding.detection_method,
            "confidence_score": embedding.confidence_score
        }
        results.append(result)
    
    return results


def mark_embeddings_as_synced(db: Session, sync_ids: List[int]) -> bool:
    """
    Mark embeddings as synced after they've been fetched by live feed device.
    
    Args:
        sync_ids: List of sync_id values to mark as synced
    
    Returns:
        True if successful, False otherwise
    """
    try:
        db.query(EmbeddingSyncLog).filter(
            EmbeddingSyncLog.sync_id.in_(sync_ids)
        ).update({"synced": "true"}, synchronize_session=False)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error marking embeddings as synced: {e}")
        return False
