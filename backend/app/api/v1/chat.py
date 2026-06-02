from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.chat import ChatCreateRequest, ChatUpdateRequest, SendMessageRequest
from app.services.chat_service import get_chat_service
from app.services.ai_service import ai_service
from app.agents.agent_orchestrator import AgentOrchestrator
from app.core.dependencies import get_current_user
from app.models.user import User
from fastapi.responses import StreamingResponse
import json

router = APIRouter()


@router.post("")
def create_chat(req: ChatCreateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    chat = get_chat_service(db).create_chat(
        user_id=str(current_user.id), title=req.title or "Yeni Sohbet",
        model=req.model or "gpt-4o", system_prompt=req.system_prompt,
        temperature=req.temperature or 0.7, max_tokens=req.max_tokens or 4096,
    )
    return {
        "id": str(chat.id), "title": chat.title, "model": chat.model,
        "system_prompt": chat.system_prompt, "temperature": chat.temperature,
        "max_tokens": chat.max_tokens, "message_count": 0,
        "created_at": chat.created_at.isoformat(), "updated_at": chat.updated_at.isoformat(),
    }


@router.get("")
def list_chats(limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0),
               current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    chats, total = get_chat_service(db).get_user_chats(str(current_user.id), limit, offset)
    return {
        "chats": [{"id": str(c.id), "title": c.title, "model": c.model, "temperature": c.temperature,
                    "message_count": len(c.messages), "created_at": c.created_at.isoformat(),
                    "updated_at": c.updated_at.isoformat()} for c in chats],
        "total": total,
    }


@router.get("/{chat_id}")
def get_chat(chat_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = get_chat_service(db)
    chat = service.get_chat(chat_id, str(current_user.id))
    messages = service.get_chat_messages(chat_id, str(current_user.id))
    return {
        "id": str(chat.id), "title": chat.title, "model": chat.model,
        "system_prompt": chat.system_prompt, "temperature": chat.temperature,
        "max_tokens": chat.max_tokens, "message_count": len(messages),
        "messages": [{"id": str(m.id), "role": m.role, "content": m.content,
                       "tokens_used": m.tokens_used, "model": m.model,
                       "created_at": m.created_at.isoformat()} for m in messages],
        "created_at": chat.created_at.isoformat(), "updated_at": chat.updated_at.isoformat(),
    }


@router.patch("/{chat_id}")
def update_chat(chat_id: str, req: ChatUpdateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    chat = get_chat_service(db).update_chat(chat_id, str(current_user.id), title=req.title, model=req.model,
                                             system_prompt=req.system_prompt, temperature=req.temperature, max_tokens=req.max_tokens)
    return {"id": str(chat.id), "title": chat.title, "model": chat.model, "updated_at": chat.updated_at.isoformat()}


@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chat(chat_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    get_chat_service(db).delete_chat(chat_id, str(current_user.id))


@router.post("/{chat_id}/messages")
async def send_message(chat_id: str, req: SendMessageRequest,
                       current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = get_chat_service(db)
    chat = service.get_chat(chat_id, str(current_user.id))
    service.save_message(chat_id=chat_id, role="user", content=req.content)
    chat_history = service.get_chat_messages(chat_id, str(current_user.id))
    formatted_history = [{"role": m.role, "content": m.content} for m in chat_history]

    orchestrator = AgentOrchestrator(db, str(current_user.id))
    full_response = ""

    async def generate():
        nonlocal full_response
        async for chunk in orchestrator.process_message(
            message=req.content, chat_history=formatted_history[:-1] if len(formatted_history) > 1 else [],
            model=req.model or chat.model, temperature=req.temperature or chat.temperature,
            max_tokens=req.max_tokens or chat.max_tokens, system_prompt=req.system_prompt or chat.system_prompt,
            use_memory=req.use_memory if req.use_memory is not None else True,
            use_rag=req.use_rag or False, use_web_search=req.use_web_search or False,
            document_ids=req.document_ids, tool_ids=req.tool_ids,
        ):
            if chunk["type"] == "content":
                full_response += chunk["content"]
            yield json.dumps(chunk) + "\n"
        if full_response:
            service.save_message(chat_id=chat_id, role="assistant", content=full_response,
                                 model=req.model or chat.model, tokens_used=len(full_response.split()))
            if chat.title == "Yeni Sohbet" and len(full_response) > 20:
                title = ai_service.generate_title(req.content)
                service.update_chat(chat_id, str(current_user.id), title=title)

    return StreamingResponse(generate(), media_type="text/event-stream")
