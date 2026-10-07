from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine, SessionLocal
from app.models import User
from app.services.security import hash_password
from app.routes.api import router


# Create database tables
Base.metadata.create_all(bind=engine)


# Create FastAPI application
app = FastAPI(
    title="AI Sales Intelligence & CRM",
    version="1.0.0",
    description="AI-powered sales CRM with lead scoring, deal intelligence and copilot"
)


# Allow React frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register API routes
app.include_router(router)


# Seed admin user
@app.on_event("startup")
def seed_admin():
    db = SessionLocal()

    try:
        if not db.query(User).filter(
            User.email == "admin@crm.local"
        ).first():

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


# Root endpoint
@app.get("/")
def root():
    return {
        "message": "AI Sales Intelligence & CRM API",
        "status": "running"
    }


# Health endpoint
@app.get("/health")
def health():
    return {
        "status": "healthy"
    }