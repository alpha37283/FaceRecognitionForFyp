# backend/models.py
"""
Database models for face embedding storage
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base
import enum


class SyncAction(enum.Enum):
    """Enum for sync log actions"""
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class Person(Base):
    """Person information table"""
    __tablename__ = "persons"

    person_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)  # 'M', 'F', 'Other'
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship
    embeddings = relationship("FaceEmbedding", back_populates="person", cascade="all, delete-orphan")


class FaceEmbedding(Base):
    """Face embedding storage table"""
    __tablename__ = "face_embeddings"

    embedding_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    person_id = Column(Integer, ForeignKey("persons.person_id", ondelete="CASCADE"), nullable=False, index=True)
    embedding_vector = Column(String, nullable=False)  # JSON string or BLOB, depending on DB
    source_image_url = Column(String(500), nullable=True)
    preprocessed_image_url = Column(String(500), nullable=True)
    detection_method = Column(String(20), nullable=True)  # 'mtcnn' or 'retinaface'
    confidence_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationship
    person = relationship("Person", back_populates="embeddings")
    sync_logs = relationship("EmbeddingSyncLog", back_populates="embedding")


class EmbeddingSyncLog(Base):
    """Sync log for tracking embedding changes"""
    __tablename__ = "embedding_sync_log"

    sync_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    embedding_id = Column(Integer, ForeignKey("face_embeddings.embedding_id", ondelete="CASCADE"), nullable=False)
    person_id = Column(Integer, ForeignKey("persons.person_id", ondelete="CASCADE"), nullable=False, index=True)
    action = Column(Enum(SyncAction), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    synced = Column(String(10), default="false", index=True)  # 'true' or 'false' as string for SQLite compatibility

    # Relationships
    embedding = relationship("FaceEmbedding", back_populates="sync_logs")
    person = relationship("Person")

