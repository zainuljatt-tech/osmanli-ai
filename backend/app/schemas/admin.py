from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class AdminUserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    role: str
    is_active: bool
    is_verified: bool
    total_messages: int
    created_at: datetime
    subscription_plan: Optional[str] = None
    subscription_status: Optional[str] = None

    class Config:
        from_attributes = True


class AnalyticsResponse(BaseModel):
    total_users: int
    active_users_today: int
    total_messages: int
    total_tokens: int
    total_revenue: float
    users_by_plan: dict
    messages_by_model: dict
    daily_usage: list[dict]


class DashboardStats(BaseModel):
    users_count: int
    chats_count: int
    messages_count: int
    documents_count: int
    active_subscriptions: int
    revenue_monthly: float
    api_requests_today: int
    error_rate: float
