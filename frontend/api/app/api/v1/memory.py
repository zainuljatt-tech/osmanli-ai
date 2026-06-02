from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.memory import MemoryCreateRequest, MemorySearchRequest
from app.services.memory_service import get_memory_service
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("")
def list_memories(limit: int = Query(50, ge=1, le=100), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    memories = get_memory_service(db).get_user_memories(str(current_user.id), limit)
    return {"memories": [{"id": str(m.id), "type": m.type.value if hasattr(m.type, 'value') else m.type,
                          "key": m.key, "content": m.content, "summary": m.summary,
                          "created_at": m.created_at.isoformat(), "updated_at": m.updated_at.isoformat()} for m in memories],
            "total": len(memories)}


@router.post("")
def create_memory(req: MemoryCreateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    memory = get_memory_service(db).add_memory(user_id=str(current_user.id), content=req.content, type=req.type or "fact", key=req.key)
    return {"id": str(memory.id), "type": memory.type.value if hasattr(memory.type, 'value') else memory.type,
            "content": memory.content, "created_at": memory.created_at.isoformat()}


@router.post("/search")
def search_memories(req: MemorySearchRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return {"results": get_memory_service(db).search_memories(str(current_user.id), req.query, req.limit)}


@router.delete("/{memory_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_memory(memory_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    get_memory_service(db).delete_memory(memory_id, str(current_user.id))
