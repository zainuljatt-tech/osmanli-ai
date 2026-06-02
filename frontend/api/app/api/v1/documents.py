from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.document import DocumentSearchRequest
from app.services.document_service import get_document_service
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("")
def list_documents(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    docs = get_document_service(db).get_user_documents(str(current_user.id))
    return {"documents": [{"id": str(d.id), "filename": d.original_filename,
                           "file_type": d.file_type.value if hasattr(d.file_type, 'value') else d.file_type,
                           "file_size": d.file_size,
                           "status": d.status.value if hasattr(d.status, 'value') else d.status,
                           "page_count": d.page_count, "chunk_count": d.chunk_count,
                           "created_at": d.created_at.isoformat(), "updated_at": d.updated_at.isoformat()} for d in docs],
            "total": len(docs)}


@router.post("/upload")
def upload_document(file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    content = file.file.read()
    if len(content) > 50 * 1024 * 1024:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File too large (max 50MB)")
    doc = get_document_service(db).upload_document(user_id=str(current_user.id), filename=file.filename or "untitled", content=content)
    return {"id": str(doc.id), "filename": doc.original_filename,
            "file_type": doc.file_type.value if hasattr(doc.file_type, 'value') else doc.file_type,
            "file_size": doc.file_size,
            "status": doc.status.value if hasattr(doc.status, 'value') else doc.status,
            "created_at": doc.created_at.isoformat()}


@router.post("/search")
def search_documents(req: DocumentSearchRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return {"results": get_document_service(db).search_documents(
        user_id=str(current_user.id), query=req.query, document_ids=req.document_ids, limit=req.limit or 5)}


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    get_document_service(db).delete_document(document_id, str(current_user.id))
