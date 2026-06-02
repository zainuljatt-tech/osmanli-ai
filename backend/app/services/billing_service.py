from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.subscription import Subscription, Payment, PaymentStatus, SubscriptionStatus
from app.models.user import User, UserRole
from app.core.config import settings
import stripe
import logging

logger = logging.getLogger(__name__)


class BillingService:
    def __init__(self, db: Session):
        self.db = db
        if settings.STRIPE_SECRET_KEY:
            stripe.api_key = settings.STRIPE_SECRET_KEY

    def create_checkout_session(self, user_id: str, price_id: str, success_url: str, cancel_url: str) -> dict:
        if not settings.STRIPE_SECRET_KEY:
            return {"url": "/settings?upgrade=success"}
        user = self.db.execute(select(User).where(User.id == user_id)).scalar_one()
        sub = self.db.execute(select(Subscription).where(Subscription.user_id == user_id)).scalar_one_or_none()
        customer_id = sub.stripe_customer_id if sub and sub.stripe_customer_id else None
        if not customer_id:
            customer = stripe.Customer.create(email=user.email, name=user.full_name, metadata={"user_id": str(user.id)})
            customer_id = customer.id
        session = stripe.checkout.Session.create(
            customer=customer_id, mode="subscription",
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=success_url, cancel_url=cancel_url,
            metadata={"user_id": str(user.id)},
        )
        return {"url": session.url}

    def get_subscription(self, user_id: str):
        return self.db.execute(select(Subscription).where(Subscription.user_id == user_id)).scalar_one_or_none()

    def get_payment_history(self, user_id: str) -> list[Payment]:
        return list(self.db.execute(
            select(Payment).where(Payment.user_id == user_id).order_by(Payment.created_at.desc()).limit(50)
        ).scalars().all())


def get_billing_service(db: Session) -> BillingService:
    return BillingService(db)
