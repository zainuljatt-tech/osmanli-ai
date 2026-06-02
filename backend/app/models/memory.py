from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.db.database import Base
from app.db.types import get_vector_type, get_uuid_type, make_uuid
import enum


class MemoryType(str, enum.Enum):
    USER = "user"
    CONVERSATION = "conversation"
    FACT = "fact"
    PREFERENCE = "preference"


class Memory(Base):
    __tablename__ = "memories"

    id = Column(get_uuid_type(), primary_key=True, default=make_uuid)
    user_id = Column(get_uuid_type(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(SQLEnum(MemoryType), default=MemoryType.FACT, nullable=False)
    key = Column(String(255), nullable=True, index=True)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    embedding = Column(get_vector_type(1536), nullable=True)
    memory_metadata = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="memories")
