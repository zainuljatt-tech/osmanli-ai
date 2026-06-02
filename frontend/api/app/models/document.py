from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.db.database import Base
from app.db.types import get_vector_type, get_uuid_type, make_uuid
import enum


class DocumentStatus(str, enum.Enum):
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class DocumentType(str, enum.Enum):
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    CSV = "csv"
    IMAGE = "image"


class Document(Base):
    __tablename__ = "documents"

    id = Column(get_uuid_type(), primary_key=True, default=make_uuid)
    user_id = Column(get_uuid_type(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(500), nullable=False)
    original_filename = Column(String(500), nullable=False)
    file_type = Column(SQLEnum(DocumentType), nullable=False)
    file_size = Column(Integer, nullable=False)
    storage_path = Column(String(1000), nullable=False)
    status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.PROCESSING, nullable=False)
    page_count = Column(Integer, nullable=True)
    chunk_count = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(get_uuid_type(), primary_key=True, default=make_uuid)
    document_id = Column(get_uuid_type(), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(get_vector_type(1536), nullable=True)
    chunk_metadata = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    document = relationship("Document", back_populates="chunks")
