from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc
from app.models.user import User, UserRole
from app.models.chat import Chat, Message
from app.models.document import Document
from app.models.subscription import Subscription, Payment, SubscriptionStatus
from app.models.log import APILog
from datetime import datetime, timedelta, timezone


class AdminService:
    def __init__(self, db: Session):
        self.db = db

    def get_dashboard_stats(self) -> dict:
        users_count = self.db.scalar(select(func.count(User.id))) or 0
        chats_count = self.db.scalar(select(func.count(Chat.id))) or 0
        messages_count = self.db.scalar(select(func.count(Message.id))) or 0
        docs_count = self.db.scalar(select(func.count(Document.id))) or 0
        active_subs = self.db.scalar(
            select(func.count(Subscription.id)).where(Subscription.status == SubscriptionStatus.ACTIVE)
        ) or 0

        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        api_today = self.db.scalar(select(func.count(APILog.id)).where(APILog.created_at >= today)) or 0
        errors_today = self.db.scalar(select(func.count(APILog.id)).where(APILog.created_at >= today, APILog.status_code >= 500)) or 0
        error_rate = round((errors_today / api_today * 100) if api_today > 0 else 0, 2)
        revenue = float(self.db.scalar(
            select(func.coalesce(func.sum(Payment.amount), 0)).where(
                Payment.status == "succeeded", Payment.created_at >= today - timedelta(days=30)
            )
        ) or 0)

        return {
            "users_count": users_count, "chats_count": chats_count,
            "messages_count": messages_count, "documents_count": docs_count,
            "active_subscriptions": active_subs, "revenue_monthly": revenue,
            "api_requests_today": api_today, "error_rate": error_rate,
        }

    def get_users(self, page: int = 1, per_page: int = 20, search: str = None) -> tuple[list[dict], int]:
        q = select(User)
        if search:
            q = q.where(User.email.ilike(f"%{search}%") | User.full_name.ilike(f"%{search}%"))
        total = self.db.scalar(select(func.count()).select_from(q.subquery())) or 0
        users = self.db.execute(q.order_by(desc(User.created_at)).offset((page - 1) * per_page).limit(per_page)).scalars().all()

        user_list = []
        for user in users:
            sub = self.db.execute(select(Subscription).where(Subscription.user_id == user.id)).scalar_one_or_none()
            user_list.append({
                "id": str(user.id), "email": user.email, "full_name": user.full_name,
                "role": user.role.value if hasattr(user.role, 'value') else user.role,
                "is_active": user.is_active, "is_verified": user.is_verified,
                "total_messages": user.total_messages, "created_at": user.created_at.isoformat(),
                "subscription_plan": sub.plan if sub else "free",
                "subscription_status": sub.status.value if sub and hasattr(sub.status, 'value') else (sub.status if sub else None),
            })
        return user_list, total

    def get_analytics(self) -> dict:
        total_users = self.db.scalar(select(func.count(User.id))) or 0
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        active_today = self.db.scalar(select(func.count(func.distinct(Message.user_id))).where(Message.created_at >= today)) or 0
        total_msgs = self.db.scalar(select(func.count(Message.id))) or 0
        total_tokens = self.db.scalar(select(func.coalesce(func.sum(Message.tokens_used), 0))) or 0
        total_rev = float(self.db.scalar(select(func.coalesce(func.sum(Payment.amount), 0)).where(Payment.status == "succeeded")) or 0)
        plan_rows = self.db.execute(select(User.role, func.count(User.id)).group_by(User.role)).fetchall()
        model_rows = self.db.execute(
            select(Message.model, func.count(Message.id)).where(Message.model.isnot(None)).group_by(Message.model).limit(10)
        ).fetchall()
        return {
            "total_users": total_users, "active_users_today": active_today,
            "total_messages": total_msgs, "total_tokens": total_tokens,
            "total_revenue": total_rev,
            "users_by_plan": {str(r[0]): r[1] for r in plan_rows},
            "messages_by_model": {str(r[0]): r[1] for r in model_rows},
        }

    def update_user_role(self, user_id: str, role: str) -> dict:
        user = self.db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
        if not user:
            raise ValueError("User not found")
        user.role = UserRole(role)
        self.db.flush()
        return {"id": str(user.id), "email": user.email, "role": user.role.value if hasattr(user.role, 'value') else user.role}


def get_admin_service(db: Session) -> AdminService:
    return AdminService(db)
