from sqlalchemy.orm import Session
from sqlalchemy import select, desc, text
from app.models.memory import Memory, MemoryType
from app.services.ai_service import ai_service
from app.core.config import settings
from typing import Optional
import json


class MemoryService:
    def __init__(self, db: Session):
        self.db = db

    def add_memory(self, user_id: str, content: str, type: str = "fact",
                   key: Optional[str] = None) -> Memory:
        embedding = ai_service.generate_embedding(content)
        embedding_value = json.dumps(embedding) if settings.USE_SQLITE and embedding else embedding
        memory = Memory(
            user_id=user_id, type=MemoryType(type), key=key,
            content=content, embedding=embedding_value,
        )
        self.db.add(memory)
        self.db.flush()
        return memory

    def search_memories(self, user_id: str, query: str, limit: int = 5) -> list[dict]:
        if not settings.USE_SQLITE:
            query_embedding = ai_service.generate_embedding(query)
            if query_embedding and not all(v == 0.0 for v in query_embedding):
                embedding_str = "[" + ",".join(str(v) for v in query_embedding) + "]"
                sql = text("""
                    SELECT id, content, type, 1 - (embedding <=> :query_emb) as score, created_at
                    FROM memories WHERE user_id = :user_id AND embedding IS NOT NULL
                    ORDER BY embedding <=> :query_emb2 LIMIT :limit
                """)
                rows = self.db.execute(sql, {
                    "query_emb": embedding_str, "query_emb2": embedding_str,
                    "user_id": user_id, "limit": limit,
                }).fetchall()
                return [{"id": str(r[0]), "content": r[1], "type": r[2],
                         "score": float(r[3]) if r[3] else 0, "created_at": str(r[4])} for r in rows]

        memories = self.db.execute(
            select(Memory).where(Memory.user_id == user_id, Memory.content.ilike(f"%{query}%"))
            .order_by(desc(Memory.created_at)).limit(limit)
        ).scalars().all()
        return [{"id": str(m.id), "content": m.content,
                 "type": m.type.value if hasattr(m.type, 'value') else m.type,
                 "score": 1.0, "created_at": str(m.created_at)} for m in memories]

    def get_user_memories(self, user_id: str, limit: int = 50) -> list[Memory]:
        return list(self.db.execute(
            select(Memory).where(Memory.user_id == user_id).order_by(desc(Memory.created_at)).limit(limit)
        ).scalars().all())

    def delete_memory(self, memory_id: str, user_id: str):
        memory = self.db.execute(
            select(Memory).where(Memory.id == memory_id, Memory.user_id == user_id)
        ).scalar_one_or_none()
        if memory:
            self.db.delete(memory)
            self.db.flush()

    def get_memory_context(self, user_id: str, query: str, limit: int = 5) -> str:
        memories = self.search_memories(user_id, query, limit)
        if not memories:
            return ""
        return "Relevant memories:\n" + "\n".join(f"- {m['content']}" for m in memories)


def get_memory_service(db: Session) -> MemoryService:
    return MemoryService(db)
