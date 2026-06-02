from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class MemoryCreateRequest(BaseModel):
    type: Optional[str] = "fact"
    key: Optional[str] = None
    content: str = Field(..., min_length=1)


class MemoryResponse(BaseModel):
    id: str
    type: str
    key: Optional[str] = None
    content: str
    summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MemorySearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    limit: Optional[int] = 5


class MemorySearchResult(BaseModel):
    id: str
    content: str
    type: str
    score: float
    created_at: datetime
