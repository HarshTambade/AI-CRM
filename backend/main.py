from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import uvicorn

from app.core.config import settings
from app.models.database import engine, Base
from app.models import *  # Import all models
from app.api import auth, users, contacts, leads, opportunities, activities, ai

# Create database tables
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    print("Database tables created")
    yield
    # Shutdown
    print("Application shutdown")

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered CRM System with advanced analytics and automation",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(contacts.router, prefix="/api/contacts", tags=["Contacts"])
app.include_router(leads.router, prefix="/api/leads", tags=["Leads"])
app.include_router(opportunities.router, prefix="/api/opportunities", tags=["Opportunities"])
app.include_router(activities.router, prefix="/api/activities", tags=["Activities"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI Services"])

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "AI-Powered CRM API",
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "database": "connected",
        "ai_models": "loaded"
    }

@app.get("/api/info")
async def api_info():
    """API information endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "AI-Powered CRM System",
        "features": [
            "User Management with Role-Based Access Control",
            "Contact and Lead Management",
            "Sales Pipeline Management",
            "Activity Tracking",
            "AI-Powered Lead Scoring",
            "Sentiment Analysis",
            "Sales Forecasting",
            "Smart Email Suggestions",
            "Churn Prediction",
            "Next Best Action Recommendations"
        ],
        "ai_models": {
            "lead_scoring": settings.SENTENCE_TRANSFORMER_MODEL,
            "sentiment_analysis": settings.SENTIMENT_MODEL,
            "text_generation": settings.TEXT_GENERATION_MODEL,
            "ner": settings.NER_MODEL
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    ) 