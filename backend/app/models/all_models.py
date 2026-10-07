from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Boolean,
    ForeignKey
)

from sqlalchemy.orm import relationship

from app.database import Base


# ============================================================
# USER
# ============================================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="sales_rep", nullable=False)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# ============================================================
# CUSTOMER
# ============================================================

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)

    company_name = Column(
        String,
        nullable=False
    )

    contact_name = Column(
        String,
        nullable=False
    )

    email = Column(
        String,
        unique=True,
        nullable=False
    )

    phone = Column(
        String,
        nullable=True
    )

    industry = Column(
        String,
        nullable=True
    )

    location = Column(
        String,
        nullable=True
    )

    annual_revenue = Column(
        Float,
        nullable=True
    )

    status = Column(
        String,
        default="active"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    # Customer → Deals
    deals = relationship(
        "Deal",
        back_populates="customer"
    )


# ============================================================
# LEAD
# ============================================================

class Lead(Base):
    __tablename__ = "leads"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String,
        nullable=False
    )

    email = Column(
        String,
        nullable=False
    )

    company_name = Column(
        String,
        nullable=False
    )

    source = Column(
        String,
        nullable=False
    )

    industry = Column(
        String,
        nullable=False
    )

    estimated_value = Column(
        Float,
        nullable=False
    )

    lead_score = Column(
        Float,
        default=0
    )

    priority = Column(
        String,
        default="Low"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# ============================================================
# DEAL
# ============================================================

class Deal(Base):
    __tablename__ = "deals"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String,
        nullable=False
    )

    customer_id = Column(
        Integer,
        ForeignKey("customers.id"),
        nullable=True
    )

    value = Column(
        Float,
        nullable=False
    )

    stage = Column(
        String,
        nullable=False,
        default="prospecting"
    )

    probability = Column(
        Float,
        default=10
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    # Deal → Customer
    customer = relationship(
        "Customer",
        back_populates="deals"
    )


# ============================================================
# ACTIVITY
# ============================================================

class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)

    customer_id = Column(
        Integer,
        ForeignKey("customers.id"),
        nullable=True
    )

    lead_id = Column(
        Integer,
        ForeignKey("leads.id"),
        nullable=True
    )

    deal_id = Column(
        Integer,
        ForeignKey("deals.id"),
        nullable=True
    )

    subject = Column(
        String,
        nullable=False
    )

    activity_type = Column(
        String,
        nullable=False
    )

    description = Column(
        String,
        nullable=False
    )

    due_date = Column(
        DateTime,
        nullable=True
    )

    completed = Column(
        Boolean,
        default=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    customer_id = Column(
        Integer,
        ForeignKey("customers.id"),
        nullable=True
    )

    lead_id = Column(
        Integer,
        ForeignKey("leads.id"),
        nullable=True
    )

    deal_id = Column(
        Integer,
        ForeignKey("deals.id"),
        nullable=True
    )

    activity_type = Column(
        String,
        nullable=False
    )

    description = Column(
        String,
        nullable=False
    )

    due_date = Column(
        DateTime,
        nullable=True
    )

    completed = Column(
        Boolean,
        default=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )