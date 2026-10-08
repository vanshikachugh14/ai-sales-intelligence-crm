from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.ml.deal_model import predict_win_probability

import jwt

from app.database import get_db
from app.models import User, Customer, Lead, Deal, Activity
from app.schemas import *
from app.services.security import (
    hash_password,
    verify_password,
    create_token,
    SECRET_KEY,
    ALGORITHM
)
from app.services.scoring import (
    calculate_lead_score,
    deal_probability
)
from app.services.analytics import dashboard
from app.services.copilot import answer


router = APIRouter()

# ---------------------------------------------------------
# AUTHENTICATION
# ---------------------------------------------------------

security = HTTPBearer()


def current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        uid = int(payload["sub"])

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user = db.get(User, uid)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return user


# ---------------------------------------------------------
# REGISTER
# ---------------------------------------------------------

@router.post(
    "/auth/register",
    response_model=UserResponse
)
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(
        User.email == data.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
        role=data.role
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


# ---------------------------------------------------------
# LOGIN
# ---------------------------------------------------------

@router.post(
    "/auth/login",
    response_model=TokenResponse
)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.email == data.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    return {
        "access_token": create_token(user.id),
        "token_type": "bearer"
    }


# ---------------------------------------------------------
# CURRENT USER
# ---------------------------------------------------------

@router.get(
    "/me",
    response_model=UserResponse
)
def me(
    user=Depends(current_user)
):
    return user


# ---------------------------------------------------------
# CUSTOMERS
# ---------------------------------------------------------

@router.get(
    "/customers/",
    response_model=list[CustomerResponse]
)
def customers(
    db: Session = Depends(get_db),
    user=Depends(current_user)
):
    return db.query(Customer).all()


@router.post(
    "/customers/",
    response_model=CustomerResponse
)
def create_customer(
    x: CustomerCreate,
    db: Session = Depends(get_db),
    user=Depends(current_user)
):
    obj = Customer(
        **x.model_dump()
    )

    db.add(obj)
    db.commit()
    db.refresh(obj)

    return obj


# ---------------------------------------------------------
# LEADS
# ---------------------------------------------------------

@router.get(
    "/leads/",
    response_model=list[LeadResponse]
)
def leads(
    db: Session = Depends(get_db),
    user=Depends(current_user)
):
    return (
        db.query(Lead)
        .order_by(Lead.lead_score.desc())
        .all()
    )


@router.post(
    "/leads/",
    response_model=LeadResponse
)
def create_lead(
    x: LeadCreate,
    db: Session = Depends(get_db),
    user=Depends(current_user)
):
    score, priority = calculate_lead_score(
        x.source,
        x.industry,
        x.estimated_value
    )

    obj = Lead(
        **x.model_dump(),
        lead_score=score,
        priority=priority
    )

    db.add(obj)
    db.commit()
    db.refresh(obj)

    return obj


@router.get(
    "/leads/{lead_id}",
    response_model=LeadResponse
)
def lead(
    lead_id: int,
    db: Session = Depends(get_db),
    user=Depends(current_user)
):
    obj = db.get(
        Lead,
        lead_id
    )

    if not obj:
        raise HTTPException(
            status_code=404,
            detail="Lead not found"
        )

    return obj


# ---------------------------------------------------------
# DEALS
# ---------------------------------------------------------

@router.get(
    "/deals/",
    response_model=list[DealResponse]
)
def deals(
    db: Session = Depends(get_db),
    user=Depends(current_user)
):
    return db.query(Deal).all()


@router.post(
    "/deals/",
    response_model=DealResponse
)
def create_deal(
    x: DealCreate,
    db: Session = Depends(get_db),
    user=Depends(current_user)
):
    obj = Deal(
        **x.model_dump(),
        probability=deal_probability(x.stage)
    )

    db.add(obj)
    db.commit()
    db.refresh(obj)

    return obj


# ---------------------------------------------------------
# ACTIVITIES
# ---------------------------------------------------------

@router.get(
    "/activities/",
    response_model=list[ActivityResponse]
)
def activities(
    db: Session = Depends(get_db),
    user=Depends(current_user)
):
    return (
        db.query(Activity)
        .order_by(Activity.due_date.asc())
        .all()
    )


@router.post(
    "/activities/",
    response_model=ActivityResponse
)
def create_activity(
    x: ActivityCreate,
    db: Session = Depends(get_db),
    user=Depends(current_user)
):
    obj = Activity(
        **x.model_dump()
    )

    db.add(obj)
    db.commit()
    db.refresh(obj)

    return obj


# ---------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------

@router.get(
    "/dashboard"
)
def dash(
    db: Session = Depends(get_db),
    user=Depends(current_user)
):
    return dashboard(db)
@router.get("/analytics")
def analytics_data(
    db: Session = Depends(get_db),
    user=Depends(current_user)
):
    return dashboard(db)


# ---------------------------------------------------------
# AI COPILOT
# ---------------------------------------------------------

@router.post(
    "/copilot"
)
def copilot(
    payload: dict,
    db: Session = Depends(get_db),
    user=Depends(current_user)
):
    question = payload.get(
        "question",
        ""
    )

    return {
        "answer": answer(
            question,
            db
        )
    }
@router.post("/deals/predict")
def predict_deal(
    payload: dict,
    db: Session = Depends(get_db),
    user=Depends(current_user)
):
    deal_value = float(payload.get("deal_value", 0))
    stage = payload.get("stage", "prospecting")
    lead_score = float(payload.get("lead_score", 50))
    activity_count = int(
        payload.get("activity_count", 0)
    )

    probability = predict_win_probability(
        deal_value=deal_value,
        stage=stage,
        lead_score=lead_score,
        activity_count=activity_count
    )

    return {
        "win_probability": probability
    }
@router.patch(
    "/activities/{activity_id}",
    response_model=ActivityResponse
)
def update_activity(
    activity_id: int,
    data: ActivityUpdate,
    db: Session = Depends(get_db),
    user=Depends(current_user)
):
    activity = (
        db.query(Activity)
        .filter(Activity.id == activity_id)
        .first()
    )

    if not activity:
        raise HTTPException(
            status_code=404,
            detail="Activity not found"
        )

    activity.completed = data.completed

    db.commit()
    db.refresh(activity)

    return activity