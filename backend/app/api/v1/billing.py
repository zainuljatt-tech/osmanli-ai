from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.billing import CreateCheckoutRequest, CreatePortalRequest
from app.services.billing_service import get_billing_service
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/create-checkout")
def create_checkout(req: CreateCheckoutRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_billing_service(db).create_checkout_session(str(current_user.id), req.price_id, req.success_url, req.cancel_url)


@router.get("/subscription")
def get_subscription(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    sub = get_billing_service(db).get_subscription(str(current_user.id))
    if not sub:
        return {"plan": "free", "status": "active", "cancel_at_period_end": False}
    return {"id": str(sub.id), "plan": sub.plan,
            "status": sub.status.value if hasattr(sub.status, 'value') else sub.status,
            "current_period_start": sub.current_period_start.isoformat() if sub.current_period_start else None,
            "current_period_end": sub.current_period_end.isoformat() if sub.current_period_end else None,
            "cancel_at_period_end": sub.cancel_at_period_end, "created_at": sub.created_at.isoformat()}


@router.get("/payments")
def get_payments(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    payments = get_billing_service(db).get_payment_history(str(current_user.id))
    return {"payments": [{"id": str(p.id), "amount": p.amount, "currency": p.currency,
                          "status": p.status.value if hasattr(p.status, 'value') else p.status,
                          "description": p.description, "created_at": p.created_at.isoformat()} for p in payments],
            "total": len(payments)}
