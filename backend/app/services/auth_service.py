from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.user import User
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from fastapi import HTTPException, status
from typing import Optional
import httpx


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def signup(self, email: str, password: str, full_name: Optional[str] = None) -> dict:
        existing = self.db.execute(select(User).where(User.email == email)).scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

        user = User(
            email=email,
            full_name=full_name,
            password_hash=get_password_hash(password),
        )
        self.db.add(user)
        self.db.flush()

        token_data = self._create_tokens(user)
        return {"user": self._user_to_dict(user), **token_data}

    def login(self, email: str, password: str) -> dict:
        result = self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user or not user.password_hash:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        if not verify_password(password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled")

        token_data = self._create_tokens(user)
        return {"user": self._user_to_dict(user), **token_data}

    def get_user_by_id(self, user_id: str) -> User:
        result = self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    def update_profile(self, user_id: str, full_name: Optional[str] = None, avatar_url: Optional[str] = None) -> User:
        user = self.get_user_by_id(user_id)
        if full_name is not None:
            user.full_name = full_name
        if avatar_url is not None:
            user.avatar_url = avatar_url
        self.db.flush()
        return user

    def _create_tokens(self, user: User) -> dict:
        return {
            "access_token": create_access_token(str(user.id)),
            "refresh_token": create_refresh_token(str(user.id)),
        }

    def _user_to_dict(self, user: User) -> dict:
        return {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "avatar_url": user.avatar_url,
            "role": user.role.value if hasattr(user.role, 'value') else user.role,
            "is_verified": user.is_verified,
            "total_messages": user.total_messages,
            "created_at": user.created_at.isoformat(),
        }


def get_auth_service(db: Session) -> AuthService:
    return AuthService(db)
