from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DocumentResponse(BaseModel):
    id: str
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    status: str
    page_count: Optional[int] = None
    chunk_count: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]
    total: int


class DocumentSearchRequest(BaseModel):
    query: str
    document_ids: Optional[list[str]] = None
    limit: Optional[int] = 5


class DocumentSearchResult(BaseModel):
    chunk_id: str
    document_id: str
    content: str
    score: float
    chunk_index: int
    filename: str
