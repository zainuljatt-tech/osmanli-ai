from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.admin_service import get_admin_service
from app.core.dependencies import get_admin_user
from app.models.user import User

router = APIRouter()


@router.get("/dashboard")
def admin_dashboard(admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    return get_admin_service(db).get_dashboard_stats()


@router.get("/users")
def admin_users(page: int = Query(1, ge=1), per_page: int = Query(20, ge=1, le=100),
                search: str = Query(None), admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    users, total = get_admin_service(db).get_users(page, per_page, search)
    return {"users": users, "total": total, "page": page, "per_page": per_page}


@router.get("/analytics")
def admin_analytics(admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    return get_admin_service(db).get_analytics()


@router.patch("/users/{user_id}/role")
def update_user_role(user_id: str, role: str = Query(..., regex="^(free|pro|enterprise|admin)$"),
                     admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    try:
        return get_admin_service(db).update_user_role(user_id, role)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
