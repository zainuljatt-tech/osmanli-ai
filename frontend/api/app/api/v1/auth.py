from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.auth import (
    SignUpRequest, LoginRequest, GoogleAuthRequest, UpdateProfileRequest,
)
from app.services.auth_service import get_auth_service
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/signup")
def signup(req: SignUpRequest, db: Session = Depends(get_db)):
    return get_auth_service(db).signup(req.email, req.password, req.full_name)


@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    return get_auth_service(db).login(req.email, req.password)


@router.post("/google")
def google_auth(req: GoogleAuthRequest, db: Session = Depends(get_db)):
    return get_auth_service(db).google_auth(req.id_token)


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": str(current_user.id), "email": current_user.email,
        "full_name": current_user.full_name, "avatar_url": current_user.avatar_url,
        "role": current_user.role.value if hasattr(current_user.role, 'value') else current_user.role,
        "is_verified": current_user.is_verified, "total_messages": current_user.total_messages,
        "created_at": current_user.created_at.isoformat(),
    }


@router.patch("/profile")
def update_profile(req: UpdateProfileRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user = get_auth_service(db).update_profile(str(current_user.id), req.full_name, req.avatar_url)
    return {"id": str(user.id), "email": user.email, "full_name": user.full_name}
