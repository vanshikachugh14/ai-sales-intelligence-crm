import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine, SessionLocal
from app.models import User
from app.services.security import hash_password
from app.routes.api import router


# Create database tables
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="AI Sales Intelligence & CRM",
    version="1.0.0",
    description="AI-powered sales CRM with lead scoring, deal intelligence and copilot"
)


# CORS configuration
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


# API routes
app.include_router(router)


@app.on_event("startup")
def seed_users():
    db = SessionLocal()

    try:
        # Create admin user if it does not exist
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

        # One-time production demo user repair
        if os.getenv("RESET_DEMO_USER") == "true":

            demo_user = db.query(User).filter(
                User.email == "demo2@salesiq.com"
            ).first()

            if demo_user:
                demo_user.password_hash = hash_password("Demo@12345")
                demo_user.role = "sales_manager"

            else:
                db.add(
                    User(
                        name="Demo User",
                        email="demo2@salesiq.com",
                        password_hash=hash_password("Demo@12345"),
                        role="sales_manager"
                    )
                )

        db.commit()

    finally:
        db.close()


@app.get("/")
def root():
    return {
        "message": "AI Sales Intelligence & CRM API",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }