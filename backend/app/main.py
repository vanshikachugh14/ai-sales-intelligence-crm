import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine, SessionLocal
from app.models import User
from app.services.security import hash_password
from app.routes.api import router
from app.seed_demo import seed_demo_data


# ============================================================
# DATABASE
# ============================================================

Base.metadata.create_all(bind=engine)


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="AI Sales Intelligence & CRM",
    version="1.0.0",
    description="AI-powered sales CRM with lead scoring, deal intelligence and copilot"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://salesiq-crm.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ROUTES
# ============================================================

app.include_router(router)


# ============================================================
# STARTUP
# ============================================================

@app.on_event("startup")
def seed_users():

    db = SessionLocal()

    try:

        # ----------------------------------------------------
        # Create admin user if it does not exist
        # ----------------------------------------------------

        admin_user = db.query(User).filter(
            User.email == "admin@crm.local"
        ).first()

        if not admin_user:
            db.add(
                User(
                    name="Admin",
                    email="admin@crm.local",
                    password_hash=hash_password("Admin@123"),
                    role="admin"
                )
            )

        db.commit()

    finally:
        db.close()

    # --------------------------------------------------------
    # One-time production demo data seed
    # --------------------------------------------------------

    if os.getenv("SEED_DEMO_DATA") == "true":
        seed_demo_data()


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "AI Sales Intelligence & CRM API",
        "status": "running"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }