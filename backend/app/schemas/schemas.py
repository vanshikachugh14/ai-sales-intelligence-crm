from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


# =========================
# AUTHENTICATION
# =========================

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    role: str = "sales_rep"


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str

    model_config = ConfigDict(from_attributes=True)


# =========================
# CUSTOMERS
# =========================

class CustomerCreate(BaseModel):
    company_name: str
    contact_name: str
    email: str
    phone: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    annual_revenue: Optional[float] = None


class CustomerResponse(CustomerCreate):
    id: int
    status: str

    model_config = ConfigDict(from_attributes=True)


# =========================
# LEADS
# =========================

class LeadCreate(BaseModel):
    name: str
    email: str
    company_name: str
    source: str
    industry: str
    estimated_value: float


class LeadResponse(LeadCreate):
    id: int
    lead_score: float
    priority: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# =========================
# DEALS
# =========================

class DealCreate(BaseModel):
    name: str
    customer_id: Optional[int] = None
    value: float
    stage: str


class DealResponse(DealCreate):
    id: int
    probability: float
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# =========================
# ACTIVITIES
# =========================

class ActivityCreate(BaseModel):
    customer_id: Optional[int] = None
    lead_id: Optional[int] = None
    deal_id: Optional[int] = None
    subject: str
    activity_type: str
    description: str
    due_date: Optional[datetime] = None


class ActivityResponse(ActivityCreate):
    id: int
    completed: bool
    created_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True
    )
    
class ActivityUpdate(BaseModel):
    completed: bool