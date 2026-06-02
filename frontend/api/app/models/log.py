from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Float, Text, ForeignKey
from app.db.database import Base
from app.db.types import get_uuid_type, make_uuid


class APILog(Base):
    __tablename__ = "api_logs"

    id = Column(get_uuid_type(), primary_key=True, default=make_uuid)
    user_id = Column(get_uuid_type(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    method = Column(String(10), nullable=False)
    endpoint = Column(String(500), nullable=False)
    status_code = Column(Integer, nullable=False)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    request_body = Column(Text, nullable=True)
    response_body = Column(Text, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
