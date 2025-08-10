from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.models.database import get_db
from app.ai.lead_scoring import LeadScoringService
from app.ai.sentiment_analysis import SentimentAnalysisService

router = APIRouter()

# Initialize AI services
lead_scoring_service = LeadScoringService()
sentiment_service = SentimentAnalysisService()

class LeadScoringRequest(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    source: Optional[str] = None
    budget: Optional[float] = None
    timeline: Optional[str] = None
    activities: Optional[List[Dict[str, Any]]] = []
    activity_count: Optional[int] = 0
    days_since_last_activity: Optional[int] = 999
    avg_response_time_hours: Optional[float] = 24.0

class SentimentAnalysisRequest(BaseModel):
    text: str

class ConversationAnalysisRequest(BaseModel):
    messages: List[Dict[str, Any]]

class EmailSuggestionRequest(BaseModel):
    context: str
    tone: Optional[str] = "professional"
    purpose: Optional[str] = "follow_up"

@router.post("/lead-scoring")
async def score_lead(
    lead_data: LeadScoringRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Score a lead using AI."""
    try:
        result = lead_scoring_service.predict_lead_score(lead_data.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scoring lead: {str(e)}")

@router.post("/sentiment-analysis")
async def analyze_sentiment(
    request: SentimentAnalysisRequest,
    current_user = Depends(get_current_user)
):
    """Analyze sentiment of text."""
    try:
        result = sentiment_service.analyze_sentiment(request.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing sentiment: {str(e)}")

@router.post("/conversation-analysis")
async def analyze_conversation(
    request: ConversationAnalysisRequest,
    current_user = Depends(get_current_user)
):
    """Analyze sentiment across a conversation."""
    try:
        result = sentiment_service.analyze_conversation_sentiment(request.messages)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing conversation: {str(e)}")

@router.post("/email-suggestions")
async def get_email_suggestions(
    request: EmailSuggestionRequest,
    current_user = Depends(get_current_user)
):
    """Get AI-generated email suggestions."""
    try:
        # Simple email template suggestions based on context
        suggestions = {
            "follow_up": [
                "Hi [Name], I wanted to follow up on our recent conversation about [topic]. Do you have any questions or would you like to schedule a time to discuss this further?",
                "Hello [Name], I hope this email finds you well. I'm reaching out to see if you've had a chance to review the information I sent about [topic].",
                "Hi [Name], I wanted to check in and see if you need any additional information about [topic]. I'm here to help!"
            ],
            "proposal": [
                "Hi [Name], I'm excited to share our proposal for [project/topic]. I believe this solution will address your needs and deliver significant value.",
                "Hello [Name], Thank you for the opportunity to present our proposal. I've tailored this solution specifically to your requirements.",
                "Hi [Name], I've prepared a comprehensive proposal that outlines how we can help you achieve your goals with [solution]."
            ],
            "meeting_request": [
                "Hi [Name], I'd love to schedule a meeting to discuss [topic] in more detail. Would you be available for a 30-minute call this week?",
                "Hello [Name], I think it would be valuable to have a conversation about [topic]. Are you free for a brief meeting?",
                "Hi [Name], I'd like to set up a time to explore how we can help with [topic]. What's your availability like?"
            ]
        }
        
        purpose = request.purpose or "follow_up"
        tone = request.tone or "professional"
        
        # Get suggestions based on purpose
        purpose_suggestions = suggestions.get(purpose, suggestions["follow_up"])
        
        # Apply tone modifications
        if tone == "casual":
            purpose_suggestions = [s.replace("Hi [Name]", "Hey [Name]") for s in purpose_suggestions]
        elif tone == "formal":
            purpose_suggestions = [s.replace("Hi [Name]", "Dear [Name]") for s in purpose_suggestions]
        
        return {
            "suggestions": purpose_suggestions[:3],
            "context": request.context,
            "tone": tone,
            "purpose": purpose
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating email suggestions: {str(e)}")

@router.get("/ai-status")
async def get_ai_status(current_user = Depends(get_current_user)):
    """Get status of AI models."""
    return {
        "lead_scoring": {
            "status": "available",
            "model": "Random Forest + Fallback",
            "features": ["lead scoring", "conversion prediction", "risk assessment"]
        },
        "sentiment_analysis": {
            "status": "available",
            "model": "Hugging Face + Fallback",
            "features": ["sentiment analysis", "emotion detection", "conversation analysis"]
        },
        "email_suggestions": {
            "status": "available",
            "model": "Template-based",
            "features": ["email templates", "tone adaptation", "context-aware suggestions"]
        }
    }

@router.post("/train-lead-scoring")
async def train_lead_scoring_model(
    training_data: List[Dict[str, Any]],
    current_user = Depends(get_current_user)
):
    """Train the lead scoring model with new data."""
    try:
        result = lead_scoring_service.train_model(training_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error training model: {str(e)}")

@router.get("/feature-importance")
async def get_feature_importance(current_user = Depends(get_current_user)):
    """Get feature importance from the lead scoring model."""
    try:
        importance = lead_scoring_service.get_feature_importance()
        return {"feature_importance": importance}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting feature importance: {str(e)}") 